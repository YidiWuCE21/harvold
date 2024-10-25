import os
import math
import random
from datetime import datetime

from django.db import models
from django.db import IntegrityError, transaction
from harvoldsite import consts


# Helper functions for level calculations
def get_xp_for_level(level, growth):
    if level < 1:
        raise ValueError("Pokemon level cannot be lower than 1!")
    return consts.EXP_CURVES[growth][str(level)]


def get_levelups(level, xp, growth):
    if xp < 0:
        raise ValueError("Pokemon XP cannot be lower than 0!")
    current_level = level
    while current_level < 100:
        xp_needed = get_xp_for_level(current_level + 1, growth)
        if xp >= xp_needed:
            current_level += 1
        else:
            break
    return current_level - level


def get_progress_to_next_level(level, xp, growth):
    if level < 1:
        raise ValueError("Pokemon level cannot be lower than 1!")
    if xp < 0:
        raise ValueError("Pokemon XP cannot be lower than 0!")
    if level == 100:
        return 0
    start_xp = get_xp_for_level(level, growth)
    end_xp = get_xp_for_level(level + 1, growth)
    return (xp - start_xp) / (end_xp - start_xp) * 100


def populate_moveset(dex_number, level, last_four=True, tms=False, tutor=False):
    """
    Get up to 4 moves that the Pokemon knows based on level
    """
    if last_four and (tms or tutor):
        return "Cannot show TMs and move tutor moves when constructing moveset"
    learnset = consts.LEARNSETS[dex_number]["level"]
    learnable_moves = [move for level_req, move in learnset if int(level) >= int(level_req)]
    if tms:
        learnable_moves += consts.LEARNSETS[dex_number]["tm"]
    if tutor:
        learnable_moves += consts.LEARNSETS[dex_number]["egg"]
        learnable_moves += consts.LEARNSETS[dex_number]["tutor"]
    if last_four:
        return learnable_moves[-4:]
    return learnable_moves


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
    return consts.NATURES[nature].get(stat, 1.0)


def create_pokemon(dex_number, level, sex, shiny=False, iv_advantage=1, traded=False, iv_override=None,
                   nature_override=None, ev_override=None, ability_override=None,
                   held_item=None, status=None, current_hp=None):
    """
    Instantiate a pokemon with no current assigned trainer
    """
    # Randomly generate nature, IVs, and ability
    nature = nature_override if nature_override is not None else \
        random.choice(list(consts.NATURES.keys()))
    ivs = iv_override if iv_override is not None else \
        {stat: max([random.randint(0, 31)] * iv_advantage) for stat in consts.STATS}
    evs = ev_override if ev_override is not None else \
        {stat: 0 for stat in consts.STATS}
    abilities = consts.POKEMON[dex_number]["abilities"]
    if ability_override:
        ability = ability_override
    else:
        ability = random.choice(abilities)

    # Get the moveset
    moves = populate_moveset(dex_number, level)
    moves = [(move, consts.MOVES[move]["pp"]) for move in moves]
    moves += [None] * (4 - len(moves))

    # Create the pokemon object
    pkmn = Pokemon(
        dex_number=dex_number,
        level=level,
        experience=get_xp_for_level(level, consts.POKEMON[dex_number]["experience_growth"]),
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
        iv_total=sum(ivs.values()),
        bst=sum(get_base_stats(dex_number).values()),
        held_item=held_item,
        traded=traded,
        happiness=consts.POKEMON[dex_number]["base_happiness"],
        location="box",
        move1=moves[0][0],
        move1_pp=moves[0][1],
        move2=moves[1][0] if moves[1] is not None else None,
        move2_pp=moves[1][1] if moves[1] is not None else None,
        move3=moves[2][0] if moves[2] is not None else None,
        move3_pp=moves[2][1] if moves[2] is not None else None,
        move4=moves[3][0] if moves[3] is not None else None,
        move4_pp=moves[3][1] if moves[3] is not None else None,
    )

    # Generate the stats
    pkmn.recalculate_stats(skip_save=True)
    # Full heal
    pkmn.restore_hp(skip_save=True)
    pkmn.save()
    return pkmn


# Create a pokemon template; this can be used for a wild battle before getting passed into the Pokemon model
#def create_pokemon(dex_number, shiny, level, sex=None)
class Pokemon(models.Model):
    # Administrative fields
    trainer = models.ForeignKey(
        "accounts.Profile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trainer"
    )
    original_trainer = models.ForeignKey(
        "accounts.Profile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="original_trainer"
    )
    caught_date = models.DateTimeField(auto_now_add=True)
    # General info
    dex_number = models.IntegerField()
    level = models.IntegerField()
    experience = models.IntegerField(default=1)
    ball = models.CharField(max_length=20, null=True, blank=True)
    sex = models.CharField(max_length=1)
    nature = models.CharField(max_length=10)
    shiny = models.BooleanField(default=False)
    ability = models.CharField(max_length=20, null=True, blank=True)
    box_tag = models.CharField(max_length=20, null=True, blank=True)
    locked = models.BooleanField(default=False)

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

    # For sorting
    iv_total = models.IntegerField(default=0)
    bst = models.IntegerField(default=0)

    # Status
    held_item = models.CharField(max_length=20, null=True, blank=True)
    current_hp = models.IntegerField()
    status = models.CharField(max_length=20, null=True, blank=True)
    traded = models.BooleanField(default=False)
    happiness = models.IntegerField(default=200)
    location = models.CharField(max_length=10, null=True, blank=True, default="box")

    # Move info
    move1 = models.CharField(max_length=20) # Pokemon must know at least one move
    move1_pp = models.IntegerField()
    move2 = models.CharField(max_length=20, null=True, blank=True)
    move2_pp = models.IntegerField(null=True)
    move3 = models.CharField(max_length=20, null=True, blank=True)
    move3_pp = models.IntegerField(null=True)
    move4 = models.CharField(max_length=20, null=True, blank=True)
    move4_pp = models.IntegerField(null=True)


    def get_battle_info(self):
        """
        Return all the battle-relevant information
        """
        return {
            # Modifiable attributes
            "current_hp": self.current_hp,
            "status": self.status,
            "moves": [
                {"move": self.move1, "pp": self.move1_pp},
                {"move": self.move2, "pp": self.move2_pp},
                {"move": self.move3, "pp": self.move3_pp},
                {"move": self.move4, "pp": self.move4_pp}
            ],
            # Immutable attributes
            "held_item": self.held_item,
            "happiness": self.happiness,
            "ability": self.ability,
            "dex_number": self.dex_number,
            "level": self.level,
            "shiny": self.shiny,
            "stats": {
                stat: getattr(self, "{}_stat".format(stat)) for stat in consts.STATS
            },
            "id": self.pk
        }

    def get_party_info(self):
        return {
            "hp_percent": (self.current_hp / self.hp_stat) * 100,
            "name": self.name,
            "id": self.pk,
            "dex": self.dex,
            "experience_progress": get_progress_to_next_level(self.level, self.experience, consts.POKEMON[self.dex]["experience_growth"]),
            "status": self.status,
            "level": self.level,
            "ball": self.ball,
            "shiny": self.shiny
        }


    def set_battle_info(self, battle_info):
        """
        Set modifiable characteristics based on battle info
        """
        self.current_hp = battle_info["current_hp"]
        self.status = battle_info["status"]
        self.move1_pp = battle_info["moves"][0]["pp"]
        self.move2_pp = battle_info["moves"][1]["pp"]
        self.move3_pp = battle_info["moves"][2]["pp"]
        self.move4_pp = battle_info["moves"][3]["pp"]
        self.save()


    def assign_trainer(self, trainer, ball=None):
        self.trainer = trainer
        if self.original_trainer is None:
            self.original_trainer = trainer
        if ball is not None:
            self.ball = ball
        self.ball = "pokeball"
        self.location = "box"
        self.trainer.add_pokedex(self.dex)
        self.save(update_fields=["trainer", "original_trainer", "ball"])

    def release(self, trainer):
        """
        Releases a Pokemon and saves.
        """
        if self.trainer != trainer:
            return "Cannot release Pokemon you don't own!"
        if self.location != "box":
            return "Only box pokemon can be released."
        self.location = "released"
        self.trainer = None
        self.save()

    def add_xp(self, xp, recalculate=False):
        """
        Adds experience and levels if applicable. Does not change movesets or prompt evolutions.

        Recalculate flag should be used for rare candy leveling, battle xp handled separately
        """
        self.experience += xp
        extra_levels = get_levelups(self.level, self.experience, consts.POKEMON[self.dex]["experience_growth"])
        self.level += extra_levels

        # Save fields in one go
        if recalculate:
            self.recalculate_stats(skip_save=True)
            self.save(update_fields=["experience", "level", "hp_stat", "atk_stat",
                                     "def_stat", "spa_stat", "spd_stat", "spe_stat"])

    def add_evs(self, evs, recalculate=False):
        """
        Adds EVs and recalculates stats.

        Recalculate flag should be used for EV juicing, battle EVs handled separately.
        """
        ev_map = {
            "hp": self.hp_ev,
            "atk": self.atk_ev,
            "def": self.def_ev,
            "spa": self.spa_ev,
            "spd": self.spd_ev,
            "spe": self.spe_ev
        }
        for stat in consts.STATS:
            total = sum(ev_map.values())
            current_val = ev_map[stat]
            to_add = evs[stat]
            # Ensure individual EV does not exceed 252 and total does not exceed 510
            max_gain = min(252 - current_val, 510 - total, to_add)
            # Ensure individual EV does not dip below 0 for EV reducers
            max_gain = max(-1 * current_val, max_gain)
            ev_map[stat] += max_gain
            setattr(self, "{}_ev".format(stat), ev_map[stat])

        if recalculate:
            self.recalculate_stats(skip_save=True)
            self.save(update_fields=["experience", "level", "{}_stat".format(stat)])

    def recalculate_stats(self, skip_save=False):
        """
        Recalculate base stats given pokemon's IVs, EVs, level, and nature. Uses gen 3+ calculation
        """
        base_stats = get_base_stats(self.dex_number)

        # HP has separate calculation
        self.hp_stat = int((2 * base_stats["hp"] + self.hp_iv + int(self.hp_ev / 4)) * self.level / 100) + self.level + 10
        # Calculation for all other stats
        self.atk_stat = int((int((2 * base_stats["atk"] + self.atk_iv + int(self.atk_ev / 4)) * self.level / 100) + 5) \
                        * get_nature_multiplier(self.nature, "atk"))
        self.def_stat = int((int((2 * base_stats["def"] + self.def_iv + int(self.def_ev / 4)) * self.level / 100) + 5) \
                        * get_nature_multiplier(self.nature, "def"))
        self.spa_stat = int((int((2 * base_stats["spa"] + self.spa_iv + int(self.spa_ev / 4)) * self.level / 100) + 5) \
                        * get_nature_multiplier(self.nature, "spa"))
        self.spd_stat = int((int((2 * base_stats["spd"] + self.spd_iv + int(self.spd_ev / 4)) * self.level / 100) + 5) \
                        * get_nature_multiplier(self.nature, "spd"))
        self.spe_stat = int((int((2 * base_stats["spe"] + self.spe_iv + int(self.spe_ev / 4)) * self.level / 100) + 5) \
                        * get_nature_multiplier(self.nature, "spe"))

        if not skip_save:
            self.save(update_fields=["hp_stat", "atk_stat", "def_stat", "spa_stat", "spd_stat", "spe_stat"])

    def restore_hp(self, amount=None, percent=None, skip_save=False):
        if amount is not None:
            self.current_hp = max(self.current_hp, self.hp_stat + amount)
        if percent is not None:
            self.current_hp = max(self.current_hp, self.hp_stat + percent * self.current_hp)
        else:
            self.current_hp = self.hp_stat
        if not skip_save:
            self.save(update_fields=["current_hp"])

    def restore_pp(self, move_no=None, restore_by=None, skip_save=False):
        """
        Restores PP to pokemon moves. If move number is not specified, restore to all applicable moves.
        If pokemon doesn't have chosen move, do nothing.
        """
        move_mapping = {
            1: (self.move1, self.move1_pp, "move1_pp"),
            2: (self.move2, self.move2_pp, "move2_pp"),
            3: (self.move3, self.move3_pp, "move3_pp"),
            4: (self.move4, self.move4_pp, "move4_pp")
        }
        moves = [move_no] if move_no else [1, 2, 3, 4]
        for move in moves:
            move_name = move_mapping[move][0]
            move_pp = move_mapping[move][1]
            move_pp_attr = move_mapping[move][2]
            if move_name is None:
                continue
            move_cap = consts.MOVES[move_name]["pp"]
            if restore_by is None:
                setattr(self, move_pp_attr, move_cap)
            else:
                setattr(self, move_pp_attr, min(move_cap, move_pp + restore_by))
        if not skip_save:
            self.save(update_fields=["move1_pp", "move2_pp", "move3_pp", "move4_pp"])

    def cure_status(self, target_status=None, skip_save=False):
        if target_status is not None and self.status != target_status:
            return
        self.status = ""
        if not skip_save:
            self.save(update_fields=["status"])


    def full_heal(self, skip_save=False):
        self.restore_hp(skip_save=True)
        self.restore_pp(skip_save=True)
        self.cure_status(skip_save=True)
        if not skip_save:
            self.save(update_fields=["current_hp", "move1_pp", "move2_pp", "move3_pp", "move4_pp", "status"])


    def learn_move(self, move, slot, tms=False, tutor=False, skip_save=False):
        """
        Learn a move. Flags to enable TM amd movetutor moves
        """
        # Check if slot is valid
        move_slots = ["move1", "move2", "move3", "move4"]
        if slot not in move_slots:
            return "Not a valid slot to save."
        # Check if move is already known
        for current_slot in move_slots:
            current_move = getattr(self, current_slot)
            if move == current_move:
                return "Move is already known!"
        learnset = populate_moveset(self.dex, self.level, last_four=False, tms=tms, tutor=tutor)
        if move not in learnset:
            return "Cannot learn this move!"
        setattr(self, slot, move)
        setattr(self, "{}_pp".format(slot), consts.MOVES[move]["pp"])
        if not skip_save:
            self.save(update_fields=[slot, "{}_pp".format(slot)])


    @property
    def name(self):
        pkmn = consts.POKEMON[str(self.dex)]
        return pkmn["name"]


    @property
    def dex(self):
        return str(self.dex_number).zfill(3)


    def get_all_evolutions(self):
        """
        Get all evolutions and conditions
        """
        evolutions = []
        if consts.EVOLUTIONS[self.dex] is None:
            return evolutions

        for pokemon, requirements in consts.EVOLUTIONS[self.dex].items():
            reqs_clean = []
            items = []
            if requirements["min_level"] != None:
                reqs_clean.append("Level {}".format(requirements["min_level"]))
            if requirements["min_happiness"] != None:
                reqs_clean.append("{} happiness".format(requirements["min_happiness"]))
            if requirements["gender"] != None:
                reqs_clean.append("Male" if requirements["gender"] == "m" else "Female")
            if requirements["held_item"] != None:
                reqs_clean.append("Traded")
                if not requirements["held_item"] == "":
                    items.append(requirements["held_item"])
                    reqs_clean.append("Holding {}".format(requirements["held_item"].replace("_", " ").capitalize()))
            if requirements["item"] != None:
                items.append(requirements["item"])
                reqs_clean.append(requirements["item"].replace("_", " ").capitalize())
            if requirements["known_move"] != None:
                reqs_clean.append("Knows {}".format(requirements["known_move"]))
            evolutions.append({
                "name": consts.POKEMON[pokemon]["name"],
                "dex": pokemon,
                "requirements": reqs_clean,
                "items": items
            })
        return evolutions





    def get_valid_evolutions(self):
        # Case where it doesn't evolve
        valid_evolutions = []
        if consts.EVOLUTIONS[self.dex] is None:
            return valid_evolutions

        for pokemon, requirements in consts.EVOLUTIONS[self.dex].items():
            # Check level requirement
            if requirements["min_level"] != None:
                if self.level < requirements["min_level"]:
                    continue

            # Check happiness requirement
            if requirements["min_happiness"] != None:
                if self.happiness < requirements["min_happiness"]:
                    continue

            # Check gender requirement
            if requirements["gender"] != None:
                if str(self.sex) != str(requirements["gender"]):
                    continue

            # Check traded requirement
            if requirements["held_item"] != None:
                if not self.traded:
                    continue
                if str(self.held_item) != str(requirements["held_item"]) and str(requirements["held_item"]) != "":
                    continue

            # Check move requirement
            if requirements["known_move"] != None:
                if not requirements["known_move"] in self.get_moves().values():
                    continue

            # Check item requirement
            if requirements["item"] != None:
                if not self.trainer.has_item(requirements["item"]):
                    continue
            valid_evolutions.append(pokemon)

        return valid_evolutions

    def evolve(self, evo_dex):
        """
        Evolve to the specified Pokemon
        """
        old_pokemon = self.name
        if evo_dex in self.get_valid_evolutions():
            try:
                with transaction.atomic():
                    # Consume held item if applicable
                    if consts.EVOLUTIONS[self.dex][evo_dex]["held_item"] not in [None, ""]:
                        self.held_item = None

                     # Consume item if applicable
                    if consts.EVOLUTIONS[self.dex][evo_dex]["item"] is not None:
                        self.trainer.consume_item(consts.EVOLUTIONS[self.dex][evo_dex]["item"])

                    # Evolve and save
                    self.dex_number = evo_dex
                    self.recalculate_stats(skip_save=True)
                    self.full_heal()
                    self.save()

            except IntegrityError:
                return (False, "Failed to evolve! Please make sure you have the needed items and your Pokemon meets evolution requirements.")

            return (True, "Your {} has evolved into a {}!".format(old_pokemon, self.name))

        else:
            return (False, "Cannot evolve to the Pokemon!")

    def change_nature(self):
        raise NotImplementedError()


    def get_info(self):
        """
        Function to return generic Pokemon info in a dict format
        """
        pokemon_info = {
            "dex": self.dex,
            "level": self.level,
            "experience_progress": get_progress_to_next_level(self.level, self.experience, consts.POKEMON[self.dex]["experience_growth"]),
            "experience": self.experience,
            "to_next": get_xp_for_level(self.level + 1, consts.POKEMON[self.dex]["experience_growth"]) - self.experience if self.level < 100 else None,
            "sex": self.sex,
            "ability": self.ability,
            "happiness_percent": self.happiness / 2.55,
            "happiness": self.happiness,
            "held_item": self.held_item,
            "status": self.status,
            "current_hp": self.current_hp,
            "hp_percent": self.current_hp / self.hp_stat * 100,
            "nature": self.nature.capitalize(),
            "ball": self.ball,
            "shiny": self.shiny
        }
        return pokemon_info


    def get_metadata(self):
        """
        Function to return Pokemon metadata in a dict format
        """
        metadata = {
            "owner": self.trainer.user.username,
            "original_trainer": self.original_trainer.user.username,
            "owner_id": self.trainer.user.pk,
            "ot_id": self.original_trainer.user.pk,
            "caught_date": self.caught_date.date,
            "location": self.location,
            "tag": self.box_tag,
            "locked": self.locked,
            "id": self.pk
        }
        return metadata


    def get_stats(self):
        """
        Function to return Pokemon info in a dict format
        """
        stats = {
            "HP": (self.hp_stat, self.hp_iv, self.hp_ev),
            "Attack": (self.atk_stat, self.atk_iv, self.atk_ev),
            "Defense": (self.def_stat, self.def_iv, self.def_ev),
            "Special Attack": (self.spa_stat, self.spa_iv, self.spa_ev),
            "Special Defense": (self.spd_stat, self.spd_iv, self.spd_ev),
            "Speed": (self.spe_stat, self.spe_iv, self.spe_ev)
        }
        return stats


    def get_moves(self, pp=False):
        """
        Function to return Pokemon info in a dict format
        """
        moveset = {
            "move1": consts.MOVES.get(self.move1, None),
            "move2": consts.MOVES.get(self.move2, None),
            "move3": consts.MOVES.get(self.move3, None),
            "move4": consts.MOVES.get(self.move4, None),
        }
        if pp:
            for move, data in moveset.items():
                if data is not None:
                    moveset[move]["current_pp"] = getattr(self, "{}_pp".format(move))

        return moveset

