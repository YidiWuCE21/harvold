import random
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


def create_battle(p1_id, p2_id, type, ai="default"):
    """
    Player 2 should either be a player ID, a Pokemon ID, or an NPC ID (stored in data file)

    A team should never enter battle fully knocked out. If a team is in a knocked out state, it is
    a bug and it is safe to full restore the team before starting the battle.
    """
    player_state = {
        "current_pokemon": 0,
        "contributors": [],
        "stat_boosts": [],
        "entry_hazards": [],
        "confusion": False,
        "locked_moves": [],
        "defense_active": [],
        "tailwind": None,
        "name": None
    }
    battle_state = {
        "player_1": player_state.copy(),
        "player_2": player_state.copy(),
        "weather": None,
        "weather_turns": 0,
        "terrain": None,
        "outcome": None,
        "type": type,
        "trick_room": None,
    }

    # Attempt to finder player 1 and team data
    player_1 = Profile.objects.get(pk=p1_id)
    if player_1.current_battle is not None:
        raise ValueError("Player 1 is already in battle!")
    party_1 = player_1.get_party()
    battle_state["player_1"]["party"] = [pkmn.get_battle_info() for pkmn in party_1]
    battle_state["player_1"]["name"] = player_1.user.username

    # Attempt to find opponent and team data
    player_2 = None
    npc_opponent = None
    wild_opponent = None
    if type == "wild":
        wild_opponent = Pokemon.objects.get(pk=p2_id)
        if wild_opponent.original_trainer is not None:
            raise ValueError("You cannot catch someone else's Pokémon!")
        battle_state["player_2"]["party"] = [wild_opponent.get_battle_info()]
        battle_state["escapes"] = 0
        battle_state["player_2"]["name"] = "wild {}".format(wild_opponent.name)
    elif type == "npc":
        if p2_id not in consts.TRAINERS:
            raise KeyError("{} not recognized as a trainer".format(p2_id))
        battle_state["player_2"]["party"] = consts.TRAINERS[p2_id]["team"]
        npc_opponent = p2_id
        battle_state["player_2"]["name"] = consts.TRAINERS[p2_id]["name"]
    elif type == "live":
        player_2 = Profile.objects.get(pk=p2_id)
        if player_2.current_battle is not None:
            raise ValueError("Player 2 is already in battle!")
        party_2 = player_2.get_party()
        battle_state["player_2"]["party"] = [pkmn.get_battle_info() for pkmn in party_2]
        battle_state["player_2"]["name"] = player_2.user.username
    else:
        raise ValueError("Type of battle must be 'wild', 'npc', or 'live'")

    # DB opereations
    battle = Battle(
        type=type,
        status="ongoing",
        player_1=player_1,
        player_2=player_2,
        npc_opponent=npc_opponent,
        wild_opponent=wild_opponent,
        battle_state = battle_state
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
    try:
        with transaction.atomic():
            battle.save()
            player_1.current_battle = battle
            player_1.save()
            if player_2 is not None:
                player_2.current_battle = battle
                player_2.save()
    except BaseException as e:
        return (False, "Battle creation failed!")
    return (True, battle)


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


    def get_battle_state(self):
        battle_state = self.battle_state
        for pkmn in battle_state["player_1"]["party"]:
            pkmn["dex_number"] = str(pkmn["dex_number"]).zfill(3)
        for pkmn in battle_state["player_2"]["party"]:
            pkmn["dex_number"] = str(pkmn["dex_number"]).zfill(3)
        return battle_state