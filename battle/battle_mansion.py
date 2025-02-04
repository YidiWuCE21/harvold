import os
import random
import copy
import json

from harvoldsite import consts
from pokemon.models import create_pokemon
from trainer_names import gen_name
from models import create_gauntlet, create_battle

class MansionTrainer():
    floor_ev = {
        "floor_1": {stat: 0 for stat in consts.STATS},
        "floor_2": {stat: 40 if stat == "hp" else 0 for stat in consts.STATS},
        "floor_3": {stat: 40 if stat in ["hp", "def", "spd"] else 0 for stat in consts.STATS},
        "floor_4": {stat: 80 if stat in ["hp", "def", "spd"] else 0 for stat in consts.STATS},
        "floor_5": {stat: 120 if stat != "spe" else 0 for stat in consts.STATS}
    }
    def __init__(self, sprite, team, floor):
        self.name = gen_name(sprite)
        self.sprite = sprite
        self.floor = floor
        # Generate the team
        self.team = team


    @classmethod
    def from_json(cls, json_obj):
        return cls(json_obj["sprite"], json_obj["team"], json_obj["floor"])


    def jsonify(self):
        return {
            "name": self.name,
            "sprite": self.sprite,
            "team": self.team,
            "floor": self.floor
        }


    def get_team(self):
        """Get team battle info as needed"""
        return [
            create_pokemon(
                dex_number=consts.DEX_LOOKUP[pokemon],
                ev_override=self.floor_ev[self.floor],
                level=100, sex="m", skip_save=True)
            for pokemon in self.team
        ]


class MansionFloor():
    # Trainers
    with open(os.path.join(consts.STATIC_PATH, "data", "battle_mansion_trainers.json")) as trainer_file:
        trainers_pool = json.load(trainer_file)
    def __init__(self, trainer_1=None, trainer_2=None, trainer_3=None):
        self.trainer_1 = trainer_1
        self.trainer_2 = trainer_2
        self.trainer_3 = trainer_3


    @classmethod
    def generate(cls, floor):
        if floor not in cls.trainers_pool:
            raise ValueError("Floor must be between 1 and 5")
        # Generate 3 random trainers
        floor_pool = cls.trainers_pool[floor]
        floor_trainers = [MansionTrainer(trainer, random.sample(floor_pool[trainer], 3), floor) for trainer in random.sample(floor_pool, 3)]
        return cls(*floor_trainers)

    def get_trainer(self, trainer_no):
        if trainer_no == 1:
            return self.trainer_1
        if trainer_no == 2:
            return self.trainer_1
        if trainer_no == 3:
            return self.trainer_1

    @classmethod
    def from_json(cls, json_obj):
        floor_obj = cls()
        floor_obj.trainer_1 = MansionTrainer.from_json(json_obj["trainer_1"])
        floor_obj.trainer_2 = MansionTrainer.from_json(json_obj["trainer_2"])
        floor_obj.trainer_3 = MansionTrainer.from_json(json_obj["trainer_3"])
        return floor_obj


    def jsonify(self):
        return {
            "trainer_1": self.trainer_1.jsonify(),
            "trainer_2": self.trainer_2.jsonify(),
            "trainer_3": self.trainer_3.jsonify()
        }


class BattleMansion():
    bm_prizes = {
        "t1": ["protein", "iron", "hp-up", "zinc", "carbos", "calcium"],
        "t2": ["qualot-berry", "tamato-berry", "grepa-berry", "hondew-berry", "kelpsy-berry", "pomeg-berry"],
        "t3": ["electirizer", "magmarizer", "kings-rock", "metal-coat", "protector", "oval-stone",
               "deep-sea-tooth", "deep-sea-scale", "prism-scale", "razor-claw", "razor-fang", "reaper-cloth"],
        "completion": [
            "tm002", # Dragon Claw
            "tm013", # ice beam
            "tm019", # roost
            "tm024", # thunderbolt
            "tm026", # earthquake
            "tm029", # psychic
            "tm030", # shadow ball
            "tm031", # brick break
            "tm035", # flamethrower
            "tm036", # sludge bomb
            "tm053", # energy ball
            "tm080", # rock slide
            "tm081", # x scissor
            "tm091", # flash cannon
            "tm099" # dazzling gleam
        ]
    }
    prize_qty = {
        "t1": (1, 3),
        "t2": (5, 7),
        "t3": (1, 1),
        "t4": (1, 1)
    }
    def __init__(self, floor_1=None, floor_2=None, floor_3=None, floor_4=None, floor_5=None):
        self.floor_1 = floor_1
        self.floor_2 = floor_2
        self.floor_3 = floor_3
        self.floor_4 = floor_4
        self.floor_5 = floor_5
        self.invent = {}
        self.progress = {}
        self.challenger = None

    @classmethod
    def generate(cls):
        floors = [MansionFloor.generate("floor_{}".format(floor)) for floor in range(1, 6)]
        invent = {}
        progress = {"floor": 1, "trainer": 1, "prizes": {}}
        return cls(*floors, invent, progress)

    def set_challenger(self, player_id):
        if self.challenger is None:
            self.challenger = player_id
        else:
            raise ValueError("Challenger cannot be changed!")

    def get_floor(self, floor_no):
        if floor_no == 1:
            return self.floor_1
        if floor_no == 2:
            return self.floor_1
        if floor_no == 3:
            return self.floor_1
        if floor_no == 4:
            return self.floor_1
        if floor_no == 5:
            return self.floor_1

    @classmethod
    def from_json(cls, json_obj):
        mansion_obj = cls()
        mansion_obj.floor_1 = MansionFloor.from_json(json_obj["floor_1"])
        mansion_obj.floor_2 = MansionFloor.from_json(json_obj["floor_2"])
        mansion_obj.floor_3 = MansionFloor.from_json(json_obj["floor_3"])
        mansion_obj.floor_4 = MansionFloor.from_json(json_obj["floor_4"])
        mansion_obj.floor_5 = MansionFloor.from_json(json_obj["floor_5"])
        mansion_obj.invent = json_obj["invent"]
        mansion_obj.progress = json_obj["progress"]
        return mansion_obj


    def jsonify(self):
        return {
            "floor_1": self.floor_1.jsonify(),
            "floor_2": self.floor_2.jsonify(),
            "floor_3": self.floor_3.jsonify(),
            "floor_4": self.floor_4.jsonify(),
            "floor_5": self.floor_5.jsonify(),
            "invent": self.invent
        }


    def add_item(self, item, quantity):
        if item in self.invent:
            self.invent[item] += quantity
        else:
            self.invent[item] = quantity


    def consume_item(self, item, quantity):
        if item in self.invent:
            if self.invent[item] >= quantity:
                self.invent[item] -= quantity
                return True
        return False


    def fight_trainer(self):
        """
        Returns the data of the current trainer
        """
        trainer_no = self.progress["trainer"]
        floor_no = self.progress["floor"]
        if not 1 <= trainer_no <= 3:
            return None
        if not 1 <= floor_no <= 5:
            return None
        mansion_floor = self.get_floor(floor_no)
        trainer_obj = mansion_floor.get_trainer(trainer_no)
        opp_info = {
            "name": trainer_obj.name,
            "team": trainer_obj.team
        }
        battle = create_battle(self.challenger, "mansion_trainer_{}_{}".format(floor_no, trainer_no), opp_override=opp_info)
        return battle


    def beat_trainer(self):
        """
        Update the progress after a trainer was beat

        Return True if complete, otherwise False
        """
        trainer_no = self.progress["trainer"]
        floor_no = self.progress["floor"]
        trainer_no += 1
        if trainer_no > 3:
            trainer_no = 1
            floor_no += 1
            self.progress["trainer"] = trainer_no
            self.progress["floor"] = floor_no
            if floor_no == 6:
                return "complete"
            else:
                return "new_floor"
        self.progress["trainer"] = trainer_no
        return "continue"


    def generate_prize(self, floor):
        """
        Generate a random prize based on the floor
        """


    def cash_out(self):
        """
        Return the rewards
        """
        default_prize = {}
        return self.progress.get("prizes", default_prize)


def start_battle_mansion(player):
    # Check if player has completed their daily mansion run
    if "battle_mansion" in player.trainers_beat:
        return False, "You have already used up your battle mansion runs for today"
    # Attempt to create a battle mansion run
    battle_mansion = BattleMansion.generate()
    battle_mansion_state = battle_mansion.jsonify()
    success, message = create_gauntlet(player, "mansion", battle_mansion_state)
    if not success:
        return False, message