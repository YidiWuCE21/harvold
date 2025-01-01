import requests
from bs4 import BeautifulSoup
import json


with open("families.json") as f:
    fam = json.load(f)
with open("pokemon.json") as f:
    pokemon = json.load(f)
for dex in pokemon:
    pokemon[dex]["family"] = fam[dex]
with open("pkmn2.json", "w+") as f:
    json.dump(pokemon, f)
