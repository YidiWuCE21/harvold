import random
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.apps import apps
from pokemon.models import Pokemon
from accounts.models import Profile
from harvoldsite import consts


def create_battle(p1_id, p2_id, type, ai="default"):
    """
    Player 2 should either be a player ID, a Pokemon ID, or an NPC ID (stored in data file)

    A team should never enter battle fully knocked out. If a team is in a knocked out state, it is
    a bug and it is safe to full restore the team before starting the battle.
    """
    battle_state = {
        "current_pokemon": {
            "player_1": None,
            "player_2": None
        },
        "stat_boosts": {
            "player_1": [0, 0, 0, 0, 0, 0, 0],
            "player_2": [0, 0, 0, 0, 0, 0, 0],
        },
        "entry_hazards": {
            "player_1": [],
            "player_2": []
        },
        "weather": None,
        "weather_turns": 0,
        "confusion": {
            "player_1": False,
            "player_2": False,
        },
        "terrain": None,
        "ai": None,
        # Used for thrash, taunt, truant, giga impact, etc.
        "locked_moves": {
            "player_1": [],
            "player_2": []
        },
        # Used for protect, endure, etc.
        "defense_active": {
            "player_1": None,
            "player_2": None,
        },
        "outcome": None,
        "escapes": 0
    }

    # Attempt to finder player 1 and team data
    player_1 = Profile.objects.get(pk=p1_id)
    if player_1.current_battle is not None:
        raise ValueError("Player 1 is already in battle!")
    party_1 = player_1.get_party()
    battle_state["party"] = {"player_1": [pkmn.get_battle_info() for pkmn in party_1]}

    # Attempt to find opponent and team data
    player_2 = None
    npc_opponent = None
    wild_opponent = None
    if type == "wild":
        wild_opponent = Pokemon.objects.get(pk=p2_id)
        battle_state["party"]["player_2"] = [wild_opponent.get_battle_info()]
    elif type == "npc":
        battle_state["party"]["player_2"] = consts.TRAINERS[p2_id]
        npc_opponent = p2_id
    elif type == "live":
        player_2 = Profile.objects.get(pk=p2_id)
        if player_2.current_battle is not None:
            raise ValueError("Player 2 is already in battle!")
        party_2 = player_2.get_party()
        battle_state["party"]["player_2"] = [pkmn.get_battle_info() for pkmn in party_2]
    else:
        raise ValueError("Type of battle must be 'wild', 'npc', or 'live'")

    # Set the current Pokemon to be the first

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
    except IntegrityError:
        return (False, "Battle creation failed!")
    return (True, "")


BATTLE_TYPES = [
    ("live", "Live Battle"),
    ("wild", "Wild Battle"),
    ("npc", "Trainer Battle")
]


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
    battle_end = models.DateTimeField(default=None)
    last_move_time = models.DateTimeField(auto_now_add=True)

    # Main var for storing important battle stuff
    battle_state = models.JSONField(blank=True, null=True)


    def current_pokemon(self, player):
        pokemon_idx = self.battle_state["current_pokemon"][player]
        return self.battle_state["party"][pokemon_idx]


    def process_battle(self):
        """
        Process phase 1 of the battle, up until Pokemon KO. If no pokemon KO, process P2 immediately.

        Function should be called when both players have selected a move. Process the move and clear it from the DB
        Need on-fail handling, have up to 3 retries


        """

        # Stage 1 - Process standard commands
        # 0) Save the move log
        output_log = []

        # 1) Check for surrender/run/draw
        if self.check_surrender():
            # Add output to log
            return

        # 2) Check for switch-in/switch-out, and arena trap/shadow tag

        # 3) Check for item usage

        # 4a) Determine move priority

        # 4b) First Pokemon move if alive

        # 4c) Second Pokemon move if alive

        # 5) Apply weather -> item -> status effects

        # 6) Save to both battle and pokemon state tables

        raise NotImplementedError()


    def check_surrender(self):
        """
        Processes all updates relating to battle end from surrender

        Return True if battle should end
        """
        # Attempt to flee wild battle
        if self.type == "wild":
            if self.player_1_choice["action"] == "surrender":
                # Increment escape attempts
                self.battle_state["escapes"] += 1

                # Calculate escape odds
                player_speed = self.current_pokemon("player_1")["stats"]["speed"]
                opponent_speed = self.current_pokemon("player_2")["stats"]["speed"]
                escape_odds = (int(player_speed * 8 / opponent_speed) + 30 * self.battle_state["escapes"]) / 256
                escaped = random.randrange(100) < escape_odds * 100

                # Process escape
                if escaped:
                    # Delete opponent Pokemon
                    self.wild_opponent.delete()

                    # Update battle
                    self.status = "ended"
                    self.battle_end = datetime.utcnow()
                    self.save()
                    return True
                else:
                    return False

            else:
                # Reset escape attempts
                self.battle_state["escapes"] = 0
                return False

        # Surrender a trainer battle
        elif self.type == "trainer":
            if self.player_1_choice["action"] == "surrender":
                # Full heal team
                for pkmn in self.player_1.get_party():
                    pkmn.full_heal()

                # Deduct pokedollars

                # Set status and battle end
                self.status = "loss"
                self.battle_end = datetime.utcnow()
                self.save()
                return True
            else:
                return False

        # Surrender a live battle
        elif self.type == "live":
            # Both surrender
            if self.player_1_choice["action"] == "surrender" and self.player_2_choice["action"] == "surrender":
                print()
            # P1 surrenders
            elif self.player_1_choice["action"] == "surrender":
                print()
            # P2 surrenders
            elif self.player_2_choice["action"] == "surrender":
                print()
            else:
                return False



def process_switch():
    """
    If Pokemon is KO'd, process switch here
    """
    raise NotImplementedError()
    # Stage 2 - Check if Pokemon are knocked out; can be by entry hazards, moves, etc.

    # 1) Check for battle end; one or both teams are fully knocked out; send rewards if so

    # 2) Prompt owners of KO'd Pokemon to switch


def check_winner():
    raise NotImplementedError()


def check_priority():
    """
    Determine which move has priority if two are selected
    """
    raise NotImplementedError()


def process_move():
    # Check that user is not knocked out
    # Check for protection
    # Calculate damage
    # Calculate self-damage
    # Roll for status effects
    # Apply boosts
    raise NotImplementedError()


def switch_in():
    # Set chosen pokemon as switched in
    # Apply entry hazards
    # Apply switch-in abilities
    raise NotImplementedError()

def switch_out():
    #
    raise NotImplementedError()