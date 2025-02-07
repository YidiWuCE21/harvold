
import random

from harvoldsite import consts
from .trainer_names import  gen_name
from pokemon.models import create_pokemon

class Trainer():
    def __init__(self, sprite, team, name=None):
        self.sprite = sprite
        self.name = name if name is not None else gen_name(sprite)
        self.team = team
        self.randObj = random.Random(sprite)


    def get_team(self):
        """Get team battle info as needed"""

        return [
            create_pokemon(
                dex_number=consts.DEX_LOOKUP[pokemon],
                nature_override=self.randObj.choice(consts.NATURES.keys()),
                ev_override={stat: 0 for stat in consts.STATS},
                iv_override={stat: self.randObj.randrange(0, 31) for stat in consts.STATS},
                level=level, sex="m", skip_save=True)
            for pokemon, level in self.team
        ]