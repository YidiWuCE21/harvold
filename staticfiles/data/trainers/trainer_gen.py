import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "harvoldsite.settings")
django.setup()
from pokemon import models
from harvoldsite import consts
payout_table = {
    "picnicker_m": 16,
    "picnicker_f": 16,
    "bug_catcher": 16,
    "lass": 16,
    "kimono_girl": 120,
    "beauty": 56,
    "biker": 16,
    "bird_keeper": 32,
    "blackbelt": 24,
    "ace_trainer_m": 60,
    "ace_trainer_f": 60,
    "cool_trainer_m": 60,
    "cool_trainer_f": 60,
    "hiker": 32,
    "backpacker_m": 24,
    "backpacker_f": 24,
    "scientist_m": 24,
    "scientist_f": 24,
    "firebreather": 32,
    "policeman": 40,
    "roughneck": 24,
    "parasol_lady": 24,
    "gentleman": 200,
    "socialite": 200,
    "clerk_m": 40,
    "clerk_f": 40,
    "clerk_b": 80
}

map = "synecdoche_city"
trainer = "sc_boss"
name = "Boss Scott"
sprite = "clerk_b"
lose = "I'm going to take my frustration out on my employees!"
reward = payout_table[sprite]


iv_advantage = 1
evs = {stat: 0 for stat in consts.STATS}
p1 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Slaking"], level=32, sex="m", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)

p2 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Slowking"], level=32, sex="m", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)
p3 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Snorlax"], level=32, sex="g", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)
p4 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Nidoqueen"], level=52, sex="m", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)
p5 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Mismagius"], level=55, sex="g", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)
p6 = models.create_pokemon(dex_number=consts.DEX_LOOKUP["Caterpie"], level=100, sex="m", skip_save=True, iv_advantage=iv_advantage, ev_override=evs)
team = [p1, p2, p3]

team = {
    "name": name,
    "team": team,
    "reward": {"base_payout": payout_table[sprite]},
    "map": map,
    "sprite": sprite,
    "lines": {
        "lose": lose
    }
}

with open("{}.json".format(trainer), "w+") as f:
    json.dump(team, f)