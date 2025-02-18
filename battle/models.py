import os
import json
import random
import copy
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.apps import apps
from pokemon.models import Pokemon
from accounts.models import Profile
from harvoldsite import consts

from .battle_manager import BattleState


BATTLE_TYPES = [
    ("live", "Live Battle"),
    ("wild", "Wild Battle"),
    ("npc", "Trainer Battle")
]
SERIES_TYPES = [
    ("bounty", "Bounty"),
    ("mansion", "Battle Mansion")
]


def players_battle_eligible(p1_id, p2_id, gauntlet):
    """
    Get the players, check if they are eligible for the battle, and return their Profile objects
    """
    player_1 = Profile.objects.get(pk=p1_id)
    if player_1.current_battle is not None:
        raise ValueError("Player 1 is already in battle!")
    if player_1.current_gauntlet is not None and gauntlet is None:
        raise ValueError("Player 1 is in a gauntlet!")

    # Player 2 is None default case
    player_2 = None
    if type == "live":
        player_2 = Profile.objects.get(pk=p2_id)
        if player_2.current_battle is not None:
            raise ValueError("Player 1 is already in battle!")
        if player_2.current_gauntlet is not None and gauntlet is None:
            raise ValueError("Player 1 is in a gauntlet!")

    return player_1, player_2


def get_battle_inventory(player):
    """
    Get the inventory in a safe way; only include items usable in battle
    """
    battle_bag = {}
    for category, item_quantities in player.bag.items():
        if category not in consts.ITEM_USAGE:
            continue
        valid_items = {item: qty for item, qty in item_quantities.items() if item in consts.ITEM_USAGE[category]}
        if valid_items:
            battle_bag[category] = valid_items
    return copy.deepcopy(battle_bag)


def create_battle(p1_id, p2_id, type, bg="default", opp_override=None, team_override=None, no_items=False, gauntlet=None, save_team=True):
    """
    Player 2 should either be a player ID, a Pokemon ID, or an NPC ID (stored in data file)

    A team should never enter battle fully knocked out. If a team is in a knocked out state, it is
    a bug and it is safe to full restore the team before starting the battle.
    """
    battle_state = {
        "player_1": copy.deepcopy(consts.PLAYER_STATE),
        "player_2": copy.deepcopy(consts.PLAYER_STATE),
        "weather": None,
        "weather_turns": 0,
        "terrain": None,
        "outcome": None,
        "type": type,
        "trick_room": None,
        "gravity": None,
    }

    player_1, player_2 = players_battle_eligible(p1_id, p2_id, gauntlet)
    party_1 = player_1.get_party()
    battle_state["player_1"]["party"] = [pkmn.get_battle_info() for pkmn in party_1] if team_override is None else team_override
    battle_state["player_1"]["name"] = player_1.user.username
    battle_state["player_1"]["inventory"] = get_battle_inventory(player_1)
    battle_state["player_2"]["inventory"] = None

    # Attempt to find opponent and team data
    npc_opponent = None
    wild_opponent = None
    reward = None
    if type == "wild":
        wild_opponent = create_wild_battle(p2_id, battle_state)
    elif type == "npc":
        npc_opponent, reward = create_npc_battle(p2_id, battle_state, opp_override, player_1)
    elif type == "live":
        player_2, party_2 = create_live_battle(battle_state, p2_id)
    else:
        raise ValueError("Type of battle must be 'wild', 'npc', or 'live'")

    # For case when first Pokemon is fainted, increment until we reach a living Pokemon
    set_first_pokemon(battle_state)

    # Wipe inventories
    if no_items:
        battle_state["player_1"]["inventory"] = {"medicine": {}, "berries": {}}
        battle_state["player_2"]["inventory"] = {"medicine": {}, "berries": {}}

    # Pre-move abilities like intimidate, sand stream, etc.
    pre_state = BattleState(battle_state)
    pre_state.process_start()
    pre_output = pre_state.output
    pre_state.output = None

    save_inventory = not no_items

    # DB opereations
    battle = Battle(
        type=type,
        status="ongoing",
        player_1=player_1,
        player_2=player_2,
        npc_opponent=npc_opponent,
        wild_opponent=wild_opponent,
        battle_state=pre_state.jsonify(),
        battle_prize=reward,
        output_log=pre_output,
        background=bg,
        gauntlet=gauntlet,
        save_inventory=save_inventory,
        save_team=save_team
    )

    # Check that parties are not knocked out
    # User party knockout should not persist after battle, and in battle check was already made
    # It is safe to fix this outside the main DB write
    if all([pkmn.current_hp == 0 for pkmn in party_1]):
        for pkmn in party_1:
            pkmn.full_heal()
    if type == "live":
        if all([pkmn.current_hp == 0 for pkmn in party_2]):
            for pkmn in party_2:
                pkmn.full_heal()


    # Save users and parties together
    with transaction.atomic():
        battle.save()
        player_1.current_battle = battle
        player_1.save()
        if player_2 is not None:
            player_2.current_battle = battle
            player_2.save()
    return battle


def create_wild_battle(p2_id, battle_state):
    wild_opponent = Pokemon.objects.get(pk=p2_id)
    if wild_opponent.original_trainer is not None:
        raise ValueError("You cannot catch someone else's Pokémon!")
    battle_state["player_2"]["party"] = [wild_opponent.get_battle_info()]
    battle_state["escapes"] = 0
    battle_state["player_2"]["name"] = "wild {}".format(wild_opponent.name)
    return wild_opponent


def create_npc_battle(p2_id, battle_state, opp_override, player_1):
    npc_opponent = p2_id
    reward = None
    if opp_override:
        battle_state["player_2"]["party"] = opp_override["party"]
        battle_state["player_2"]["name"] = opp_override["name"]
        if "reward" in opp_override:
            reward = opp_override["reward"]
    else:
        trainer_data = "{}.json".format(p2_id)
        trainer_path = os.path.join(consts.STATIC_PATH, "data", "trainers", trainer_data)
        if not os.path.isfile(trainer_path):
            raise KeyError("{} not recognized as a trainer".format(p2_id))
        with open(trainer_path) as trainer_file:
            trainer_json = json.load(trainer_file)
            battle_state["player_2"]["party"] = trainer_json["team"]
            battle_state["player_2"]["name"] = trainer_json["name"]
            reward = trainer_json["reward"]
            # If the trainer requires the user be on a map, perform check now
            if "map" in trainer_json:
                if trainer_json["map"] != player_1.current_map:
                    raise ValueError("Trainer is not on the right map!")
    return npc_opponent, reward


def create_live_battle(battle_state, p2_id):
    player_2 = Profile.objects.get(pk=p2_id)
    if player_2.current_battle is not None:
        raise ValueError("Player 2 is already in battle!")
    if player_2.current_gauntlet is not None:
        raise ValueError("Player 2 is in a gauntlet!")
    party_2 = player_2.get_party()
    battle_state["player_2"]["party"] = [pkmn.get_battle_info() for pkmn in party_2]
    battle_state["player_2"]["name"] = player_2.user.username
    battle_state["player_2"]["inventory"] = get_battle_inventory(player_2)
    return player_2, party_2


def set_first_pokemon(battle_state):
    for player in ["player_1", "player_2"]:
        current = 0
        while True:
            try:
                if battle_state[player]["party"][current]["current_hp"] > 0:
                    break
                current += 1
            except:
                raise ValueError("All Pokemon are fainted, cannot make battle!")
        battle_state[player]["current_pokemon"] = current
        battle_state[player]["participants"] = [pkmn for pkmn in range(len(battle_state[player]["party"])) if pkmn == current or battle_state[player]["party"][pkmn]["held_item"] == "exp-share"]



# Create your models here.
class Battle(models.Model):
    type = models.CharField(max_length=10, choices=BATTLE_TYPES)
    status = models.CharField(max_length=15)
    player_1 = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="p1"
    )

    # Three possibilities for battle opponent
    player_2 = models.ForeignKey(
        "accounts.Profile",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="p2"
    )
    npc_opponent = models.CharField(max_length=20, blank=True, null=True)
    wild_opponent = models.ForeignKey(
        Pokemon,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    player_1_choice = models.JSONField(blank=True, null=True, default=None)
    player_2_choice = models.JSONField(blank=True, null=True, default=None)
    current_turn = models.IntegerField(default=1)

    # Logical move history
    move_history = models.JSONField(blank=True, null=True, default=None)

    # Data to output to user
    output_log = models.JSONField(blank=True, null=True, default=None)

    # Time tracking
    battle_start = models.DateTimeField(auto_now_add=True)
    battle_end = models.DateTimeField(blank=True, null=True, default=None)
    last_move_time = models.DateTimeField(auto_now_add=True)

    # Main var for storing important battle stuff
    battle_state = models.JSONField(blank=True, null=True)

    # Prize tracking
    battle_prize = models.JSONField(blank=True, null=True, default=None)

    # Background
    background = models.CharField(max_length=20, blank=True, null=True, default=None)

    # Flags to sasve
    save_team = models.BooleanField(default=True)
    save_inventory = models.BooleanField(default=True)

    # Gauntlet if applicable
    gauntlet = models.ForeignKey(
        "battle.Gauntlet",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )


    def get_battle_state(self):
        battle_state = self.battle_state
        for pkmn in battle_state["player_1"]["party"]:
            pkmn["dex_number"] = str(pkmn["dex_number"]).zfill(3)
        for pkmn in battle_state["player_2"]["party"]:
            pkmn["dex_number"] = str(pkmn["dex_number"]).zfill(3)
        return battle_state


    def get_all_moves(self):
        moves = []
        for player in [self.battle_state["player_1"], self.battle_state["player_2"]]:
            for pkmn in player["party"]:
                for move in pkmn["moves"]:
                    if move["move"] is not None:
                        if not move["move"] in moves:
                            moves.append(move["move"])
        return moves

    def get_opp(self, player):
        if player == self.player_1:
            return self.player_2
        elif player == self.player_2:
            return self.player_1
        return None


    def send_state_to_gauntlet(self):
        if self.gauntlet is not None:
            current_team_state = self.battle_state["player_1"]["party"]
            self.gauntlet.team_state = current_team_state

class Gauntlet(models.Model):
    # Generic model to track any event that consists of a series of battles; bounties, Battle Mansion, etc
    gauntlet_type = models.CharField(max_length=10, choices=SERIES_TYPES)
    status = models.CharField(max_length=10)
    player = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE
    )
    # Flags
    team_mutable = models.BooleanField(default=False)
    can_heal = models.BooleanField(default=False)

    # State to track team throughout series
    team_state = models.JSONField(blank=True, null=True, default=None)
    # State to track all info about series; include stuff like inventory, buffs/debuffs, trainers to fight, progress
    gauntlet_state = models.JSONField(blank=True, null=True, default=None)
    # Var to track the state of the current battle; can be pending, victory, or defeat
    current_battle = models.CharField(max_length=10, default="pending")


    def heal(self, percent, revive_percent, status=False):
        team = []
        for pokemon in self.team_state:
            if pokemon["current_hp"] == 0:
                pokemon["current_hp"] = int(revive_percent * pokemon["stats"]["hp"])
            else:
                boosted_hp = max(
                    int(revive_percent * pokemon["stats"]["hp"]),
                    int(pokemon["current_hp"] * (1 + percent)))
                pokemon["current_hp"] = min(boosted_hp, pokemon["stats"]["hp"])
            if status:
                pokemon["status"] = ""
            team.append(pokemon)
        self.team_state = team


def create_gauntlet(player, gauntlet_type, gauntlet_state, team_state=None, mutable=False, heal=False):
    if player.current_battle is not None or player.current_gauntlet is not None:
        return False, "User is already in a battle or gauntlet."

    if team_state is None:
        team_state = [pkmn.get_battle_info() for pkmn in player.get_party()]
    new_gauntlet = Gauntlet(
        gauntlet_type=gauntlet_type,
        status="ongoing",
        player=player,
        team_mutable=mutable,
        can_heal=heal,
        team_state=team_state,
        gauntlet_state=gauntlet_state
    )
    with transaction.atomic():
        try:
            new_gauntlet.save()
            player.current_gauntlet = new_gauntlet
            player.save()
            return new_gauntlet, ""
        except BaseException as e:
            return False, "Failed to create gauntlet"