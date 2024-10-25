# Constants for account registration
import os
import json
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from pokemon import utils
from harvoldsite import settings

# Large files
ASSETS_PATH = os.path.join(settings.BASE_DIR, "global_static")
with open(os.path.join(ASSETS_PATH, "data", "learnsets.json")) as learnset_file:
    LEARNSETS = json.load(learnset_file)
with open(os.path.join(ASSETS_PATH, "data", "pokemon.json")) as pokemon_file:
    POKEMON = json.load(pokemon_file)
with open(os.path.join(ASSETS_PATH, "data", "moves.json")) as pokemon_file:
    MOVES = json.load(pokemon_file)
with open(os.path.join(ASSETS_PATH, "data", "exp_curves.json")) as pokemon_file:
    EXP_CURVES = json.load(pokemon_file)
with open(os.path.join(ASSETS_PATH, "data", "pokemart.json")) as mart:
    MART = json.load(mart)
with open(os.path.join(ASSETS_PATH, "data", "trainers.json")) as trainers:
    TRAINERS = json.load(trainers)
with open(os.path.join(ASSETS_PATH, "data", "wild.json")) as wild:
    WILD = json.load(wild)
with open(os.path.join(ASSETS_PATH, "data", "evolutions.json")) as evo:
    EVOLUTIONS = json.load(evo)
with open(os.path.join(ASSETS_PATH, "data", "items.json"), encoding="utf-8") as items:
    ITEMS = json.load(items)

# Asset paths
ASSET_PATHS = {
    # Pokemon sprites
    "icon": os.path.join("assets", "pokemon", "icon"),
    "art": os.path.join("assets", "pokemon", "art"),
    "front": os.path.join("assets", "pokemon", "front"),
    # Player sprites
    "player_sprite": os.path.join("assets", "player", "sprite"),
    "player_art": os.path.join("assets", "player", "art"),
    "player_ow": os.path.join("assets", "player", "overworld"),
    # NPC sprites
    "trainer_sprite": os.path.join("assets", "npc", "sprite"),
    "trainer_ow": os.path.join("assets", "npc", "overworld"),
    # Misc assets
    "typing": os.path.join("assets", "pokemon", "type"),
    "item": os.path.join("assets", "items"),
    "moves": os.path.join("assets", "pokemon", "moves"),
    "badges": os.path.join("assets", "badges"),
    "misc": os.path.join("assets", "misc")
}

# Login-related choicesf
STARTER_CHOICES = [
    # Kanto
    ("001", "Bulbasaur"),
    ("004", "Charmander"),
    ("007", "Squirtle"),
    ("152", "Chikorita"),
    ("155", "Cyndaquil"),
    ("158", "Totodile"),
    ("252", "Treecko"),
    ("255", "Torchic"),
    ("258", "Mudkip"),
    ("387", "Turtwig"),
    ("390", "Chimchar"),
    ("393", "Piplup"),
    ("495", "Snivy"),
    ("498", "Tepig"),
    ("501", "Oshawott"),
]

TRAINER_CHOICES = [
    ("01", "01"),
    ("02", "02"),
    ("03", "03"),
    ("04", "04"),
    ("05", "05"),
    ("06", "06"),
    ("07", "07"),
    ("08", "08"),
    ("09", "09"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
    ("13", "13"),
    ("14", "14"),
    ("15", "15"),
]

STATS = ["hp", "atk", "def", "spa", "spd", "spe"]
NATURES = {
    "adamant": {"atk": 1.1, "spa": 0.9},
    "lonely": {"atk": 1.1, "def": 0.9},
    "brave": {"atk": 1.1, "spe": 0.9},
    "naughty": {"atk": 1.1, "spd": 0.9},
    "modest": {"spa": 1.1, "atk": 0.9},
    "mild": {"spa": 1.1, "def": 0.9},
    "rash": {"spa": 1.1, "spd": 0.9},
    "quiet": {"spa": 1.1, "spe": 0.9},
    "timid": {"spe": 1.1, "atk": 0.9},
    "jolly": {"spe": 1.1, "spa": 0.9},
    "hasty": {"spe": 1.1, "def": 0.9},
    "naive": {"spe": 1.1, "spd": 0.9},
    "bold": {"def": 1.1, "atk": 0.9},
    "impish": {"def": 1.1, "spa": 0.9},
    "lax": {"def": 1.1, "spd": 0.9},
    "relaxed": {"def": 1.1, "spe": 0.9},
    "calm": {"spd": 1.1, "atk": 0.9},
    "careful": {"spd": 1.1, "spa": 0.9},
    "gentle": {"spd": 1.1, "def": 0.9},
    "sassy": {"spd": 1.1, "spe": 0.9},
    "serious": {},
    "docile": {},
    "bashful": {},
    "hardy": {},
    "quirky": {},
}

TAGS = ["circle", "star", "square", "diamond"]

MAPS = [
    "oak_village",
    "kaguya_town",
    "synecdoche_city",
    "route_1",
    "route_2",
    "route_3",
    "route_4",
    "route_5",
    "route_6",
    "route_7",
    "vitur_forest",
]

GYM_LEADERS = {
    "grass": {"npc": "erika", "name": "Erika", "reg": "070", "elite": "003", "level": 21},
    "electric": {"npc": "volkner", "name": "Volkner", "reg": "404", "elite": "466", "level": 28},
    "water": {"npc": "wallace", "name": "Wallace", "reg": "364", "elite": "130", "level": 35},
    "ground": {"npc": "giovanni", "name": "Giovanni", "reg": "095", "elite": "530", "level": 42},
    "fighting": {"npc": "bruno", "name": "Bruno", "reg": "107", "elite": "534", "level": 49},
    "fire": {"npc": "blaine", "name": "Blaine", "reg": "126", "elite": "059", "level": 56},
    "ghost": {"npc": "shauntal", "name": "Shauntal", "reg": "356", "elite": "609", "level": 63},
    "psychic": {"npc": "caitlin", "name": "Caitlin", "reg": "281", "elite": "579", "level": 70},
    "steel": {"npc": "steven", "name": "Steven", "reg": "305", "elite": "376", "level": 77},
    "dragon": {"npc": "clair", "name": "Clair", "reg": "148", "elite": "445", "level": 84}
}