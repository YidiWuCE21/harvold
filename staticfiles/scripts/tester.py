import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "harvoldsite.settings")
django.setup()
from pokemon import models

trainer = "erika_gym"
name = "Erika"
reward = 400

p1 = models.create_pokemon(dex_number="114", level=14, sex="m", skip_save=True)
p2 = models.create_pokemon(dex_number="044", level=15, sex="f", skip_save=True)
p3 = models.create_pokemon(dex_number="188", level=18, sex="m", skip_save=True)
p4 = models.create_pokemon(dex_number="070", level=20, sex="f", skip_save=True)
p5 = models.create_pokemon(dex_number="470", level=21, sex="f", skip_save=True)
team = [p1, p3, p4]

team = {"name": name, "team": team, "reward": reward}

with open("{}.json", "w+") as f:
    json.dump(team, f)