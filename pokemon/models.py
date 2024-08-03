import os
import math
import random

from django.db import models
from accounts.models import Profile
from harvoldsite import consts


# Helper functions for level calculations
def get_xp_for_level(max_xp, level):
    if level < 1:
        raise ValueError("Pokemon level cannot be lower than 1!")
    return math.floor((max_xp / 1000000) * level ** 3)


def get_progress_to_next_level(max_xp, level, xp):
    if level < 1:
        raise ValueError("Pokemon level cannot be lower than 1!")
    if xp < 0:
        raise ValueError("Pokemon XP cannot be lower than 0!")
    if level == 100:
        return 0
    start_xp = get_xp_for_level(max_xp, level)
    end_xp = get_xp_for_level(max_xp, level + 1)
    return (xp - start_xp) / (end_xp - start_xp) * 100


def populate_moveset(dex_number, level):
    """
    Get up to 4 moves that the Pokemon knows based on level
    """
    learnset = consts.LEARNSETS[dex_number]["level"]
    learnable_moves = [move for level_req, move in learnset if int(level) >= int(level_req)]

    return learnable_moves[-4:]


def get_base_stats(dex_number):
    if dex_number not in consts.POKEMON:
        # Try using integer
        dex_number = str(dex_number).zfill(3)
    base_stats = {
        "hp": consts.POKEMON[dex_number]["hp"],
        "atk": consts.POKEMON[dex_number]["attack"],
        "def": consts.POKEMON[dex_number]["defense"],
        "spa": consts.POKEMON[dex_number]["sp_attack"],
        "spd": consts.POKEMON[dex_number]["sp_defense"],
        "spe": consts.POKEMON[dex_number]["speed"],
    }
    return base_stats


def get_nature_multiplier(nature, stat):
    """
    Get the nature multiplier for a given stat, default to 1.0 if no effect
    """
    return consts.NATURES[nature].get(stat, default=1.0)


def create_pokemon(dex_number, level, sex, shiny=False, iv_advantage=1, traded=False, iv_override=None,
                   nature_override=None, ev_override=None, ability_override=None,
                   held_item=None, status=None, current_hp=None):
    """
    Instantiate a pokemon with no current assigned trainer
    """
    # Randomly generate nature, IVs, and ability
    nature = random.choice(list(consts.NATURES.keys()))
    ivs = iv_override if iv_override is not None else \
        {stat: max([random.randint(0, 31)] * iv_advantage) for stat in consts.STATS}
    evs = ev_override if ev_override is not None else \
        {stat: 0 for stat in consts.STATS}
    abilities = consts.POKEMON[dex_number]["abilities"]
    if ability_override:
        ability = ability_override
    elif len(abilities) == 1:
        # Assign ability
        ability = abilities[0]
    elif len(abilities) == 2:
        # Roll abilities equally
        ability = abilities[0] if random.randrange(100) < 50 else abilities[1]
    elif len(abilities) == 3:
        # Roll for HA chance first
        ability = abilities[3] if random.randrange(100) < 20 else \
            abilities[0] if random.randrange(100) < 50 else abilities[1]
    else:
        raise ValueError("Pokemon cannot have more than 3 abilities!")

    # Get the moveset
    moves = populate_moveset(dex_number, level)

    # Create the pokemon object
    pkmn = Pokemon(
        dex_number=dex_number,
        level=level,
        xp=get_xp_for_level(consts.POKEMON[dex_number]["experience_growth"], level),
        sex=sex,
        nature=nature,
        shiny=shiny,
        ability=ability,
        hp_iv=ivs["hp"],
        hp_ev=evs["hp"],
        atk_iv=ivs["atk"],
        atk_ev=evs["atk"],
        def_iv=ivs["def"],
        def_ev=evs["def"],
        spa_iv=ivs["spa"],
        spa_ev=evs["spa"],
        spd_iv=ivs["spd"],
        spd_ev=evs["spd"],
        spe_iv=ivs["spe"],
        spe_ev=evs["spe"],
        held_item=held_item,
        happiness=consts.POKEMON[dex_number]["base_happiness"],

    )

    # Generate the stats


# Create a pokemon template; this can be used for a wild battle before getting passed into the Pokemon model
#def create_pokemon(dex_number, shiny, level, sex=None)
class Pokemon(models.Model):
    # Administrative fields
    pkmn_id = models.IntegerField(primary_key=True)
    trainer = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    original_trainer = models.IntegerField(null=True, blank=True)
    # General info
    dex_number = models.IntegerField()
    level = models.IntegerField()
    experience = models.IntegerField(default=1)
    ball = models.CharField(max_length=20, null=True, blank=True)
    sex = models.CharField(max_length=1)
    nature = models.CharField(max_length=10)
    shiny = models.BooleanField(default=False)
    ability = models.CharField(max_length=20, null=True, blank=True)

    # Stats
    hp_stat = models.IntegerField(default=1)
    hp_iv = models.IntegerField()
    hp_ev = models.IntegerField(default=0)
    atk_stat = models.IntegerField(default=1)
    atk_iv = models.IntegerField()
    atk_ev = models.IntegerField(default=0)
    def_stat = models.IntegerField(default=1)
    def_iv = models.IntegerField()
    def_ev = models.IntegerField(default=0)
    spa_stat = models.IntegerField(default=1)
    spa_iv = models.IntegerField()
    spa_ev = models.IntegerField(default=0)
    spd_stat = models.IntegerField(default=1)
    spd_iv = models.IntegerField()
    spd_ev = models.IntegerField(default=0)
    spe_stat = models.IntegerField(default=1)
    spe_iv = models.IntegerField()
    spe_ev = models.IntegerField(default=0)

    # Status
    held_item = models.CharField(max_length=20, null=True, blank=True)
    current_hp = models.IntegerField()
    status = models.CharField(max_length=20, null=True, blank=True)
    traded = models.BooleanField(default=False)
    happiness = models.IntegerField(default=200)
    location = models.CharField(max_length=10, null=True, blank=True)

    # Move info
    move1 = models.CharField(max_length=20) # Pokemon must know at least one move
    move1_pp = models.IntegerField()
    move2 = models.CharField(max_length=20, null=True, blank=True)
    move2_pp = models.IntegerField(null=True)
    move3 = models.CharField(max_length=20, null=True, blank=True)
    move3_pp = models.IntegerField(null=True)
    move4 = models.CharField(max_length=20, null=True, blank=True)
    move4_pp = models.IntegerField(null=True)

    def assign_trainer(self, trainer, ball=None):
        raise NotImplementedError()

    def recalculate_stats(self):
        """
        Recalculate base stats given pokemon's IVs, EVs, level, and nature. Uses gen 3+ calculation
        """
        base_stats = get_base_stats(self.dex_number)

        # HP has separate calculation
        self.hp_stat = (2 * base_stats["hp"] + self.hp_iv + self.hp_ev / 4) * self.level / 100 + self.level + 10

        raise NotImplementedError()

    def restore_hp(self):
        raise NotImplementedError()

    def restore_pp(self, move=None):
        """
        Restores PP to pokemon moves. If move is not specified, restore to all applicable moves.
        If pokemon doesn't have chosen move, do nothing.
        """
        raise NotImplementedError()

    def cure_status(self):
        raise NotImplementedError()

    def add_xp(self):
        raise NotImplementedError()

    def add_evs(self):
        raise NotImplementedError()

    def evolve(self):
        raise NotImplementedError()

    def change_nature(self):
        raise NotImplementedError()

    def move_to_party(self):
        raise NotImplementedError()

    def move_to_box(self):
        raise NotImplementedError()


class Party(models.Model):
    party_id = models.IntegerField(primary_key=True)
    trainer = models.OneToOneField(Profile, on_delete=models.CASCADE)
    slot_1 = models.ForeignKey(Pokemon, related_name="slot_1", null=True, on_delete=models.SET_NULL)
    slot_2 = models.ForeignKey(Pokemon, related_name="slot_2", null=True, on_delete=models.SET_NULL)
    slot_3 = models.ForeignKey(Pokemon, related_name="slot_3", null=True, on_delete=models.SET_NULL)
    slot_4 = models.ForeignKey(Pokemon, related_name="slot_4", null=True, on_delete=models.SET_NULL)
    slot_5 = models.ForeignKey(Pokemon, related_name="slot_5", null=True, on_delete=models.SET_NULL)
    slot_6 = models.ForeignKey(Pokemon, related_name="slot_6", null=True, on_delete=models.SET_NULL)

    def swap(self, slot1, slot2):
        raise NotImplementedError()
