# Constants for account registration
import os
import json
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from pokemon import utils
from harvoldsite import settings

# Large files
STATIC_PATH = os.path.join(settings.BASE_DIR, "global_static")
with open(os.path.join(STATIC_PATH, "data", "learnsets.json")) as learnset_file:
    LEARNSETS = json.load(learnset_file)
with open(os.path.join(STATIC_PATH, "data", "pokemon.json")) as pokemon_file:
    POKEMON = json.load(pokemon_file)
    DEX_LOOKUP = {pkmn["name"]: dex for dex, pkmn in POKEMON.items()}
with open(os.path.join(STATIC_PATH, "data", "moves.json")) as pokemon_file:
    MOVES = json.load(pokemon_file)
with open(os.path.join(STATIC_PATH, "data", "exp_curves.json")) as pokemon_file:
    EXP_CURVES = json.load(pokemon_file)
with open(os.path.join(STATIC_PATH, "data", "pokemart.json")) as mart:
    MART = json.load(mart)
with open(os.path.join(STATIC_PATH, "data", "trainers.json")) as trainers:
    TRAINERS = json.load(trainers)
with open(os.path.join(STATIC_PATH, "data", "wild.json")) as wild:
    WILD = json.load(wild)
with open(os.path.join(STATIC_PATH, "data", "evolutions.json")) as evo:
    EVOLUTIONS = json.load(evo)
with open(os.path.join(STATIC_PATH, "data", "items.json"), encoding="utf-8") as items:
    ITEMS = json.load(items)
with open(os.path.join(STATIC_PATH, "data", "item_usage.json"), encoding="utf-8") as item_usage:
    ITEM_USAGE = json.load(item_usage)
with open(os.path.join(STATIC_PATH, "data", "pokemon_descriptions.json"), encoding="utf-8") as desc:
    DESCRIPTIONS = json.load(desc)
with open(os.path.join(STATIC_PATH, "data", "battle_mansion_trainers.json")) as trainer_file:
    BM_POOL = json.load(trainer_file)

# Asset paths
ASSET_PATHS = {
    # Pokemon sprites
    "icon": os.path.join("assets", "pokemon", "icon"),
    "art": os.path.join("assets", "pokemon", "art"),
    "front": os.path.join("assets", "pokemon", "front"),
    "back": os.path.join("assets", "pokemon", "back"),
    "ow": os.path.join("assets", "pokemon", "overworld"),
    # Player sprites
    "player_sprite": os.path.join("assets", "player", "sprite"),
    "player_art": os.path.join("assets", "player", "art"),
    "player_ow": os.path.join("assets", "player", "overworld"),
    "player_back": os.path.join("assets", "player", "back"),
    # NPC sprites
    "trainer_sprite": os.path.join("assets", "npc", "sprite"),
    "trainer_ow": os.path.join("assets", "npc", "overworld"),
    # Audio assets
    "music": os.path.join("assets", "audio", "music"),
    "cries": os.path.join("assets", "audio", "cries"),
    "move_sounds": os.path.join("assets", "audio", "moves"),
    # Misc assets
    "typing": os.path.join("assets", "pokemon", "type"),
    "item": os.path.join("assets", "items"),
    "moves": os.path.join("assets", "pokemon", "moves"),
    "badges": os.path.join("assets", "badges"),
    "misc": os.path.join("assets", "misc"),
    "scene": os.path.join("assets", "scene"),
    "ui_scene": os.path.join("assets", "ui_scene"),
    "status": os.path.join("assets", "status"),
    "demo": os.path.join("assets", "demo"),
    "menu": os.path.join("assets", "menu")
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
    "zubrowka_city",
    "port_inisherin",
    "baxter_city",
    "juvet_town",
    "fletcher_village",
    "vanya_town",
    "port_endurance",
    "grenoble_city",
    "sen_village",
    "vitur_forest",
    "pacific_lake",
    "mountain_grove",
    "snorlax_island",
    "drilbur_cave_1f",
    "drilbur_cave_2f",
    "blackwood",
    "hidden_pond",
    "baxter_graveyard",
    "abandoned_mineshaft_1f",
    "oshi_tunnel",
    "desert_oasis",
    "ancient_forest",
    "dragons_den_1f",
    "mount_beoning_1f",
    "sky_tower_entrance",
    "route_1",
    "route_2",
    "route_3",
    "route_4",
    "route_5",
    "route_6",
    "route_7",
    "route_8",
    "route_9",
    "route_10",
    "route_11",
    "route_12",
    "route_13",
    "route_14",
    "route_15",
    "route_16",
    "route_17",
    "route_18",
    "route_19",
    "route_20",
    "route_21",
    "route_22",
    "route_23",
    "route_24",
    "route_25",
    "route_26",
    "route_27",
    "route_28",
    "route_29",
    "route_30",
    "route_31",
    "route_32",
    "route_33",
    "route_34",
    "route_35"
]

SWARMS = [
    "083", # Farfetch'd
    "088", # Grimer
    "100", # Voltorb
    "109", # Koffing
    "128", # Tauros
    "201", # Unown
    "360", # Wynaut
    "203", # Girafarig
    "206", # Dunsparce
    "209", # Snubbull
    "302", # Sableye
    "311", # Plusle
    "312", # Minun
    "351", # Castform
    "417", # Pachirisu
    "479", # Rotom
    "511", # Pansage
    "513", # Pansear
    "515", # Panpour
    "561", # Sigilyph
    "568", # Trubbish
    "587", # Emolga
    "588", # Karrablast
    "592", # Frillish
    "599", # Klink
    "605", # Elgyem
    "616", # Shelmet
    "626", # Bouffalant
    "631", # Heatmor
    "632" # Durant
]

SWARM_ROUTES = [
    "route_1",
    "route_2",
    "route_3",
    "route_4",
    "route_5",
    "route_6",
    "route_7",
    "route_8",
    "route_9",
    "route_10",
    "route_11",
    "route_12",
    "route_13",
    "route_14",
    "route_15",
    "route_22",
    "route_23"
]

CITIES = {
    "oak_village": {
        "position": {"x": 119, "y": 95},
        "size": {"x": 20, "y": 12},
        "name": "Oak Village"
    },
    "kaguya_town": {
        "position": {"x": 91, "y": 95},
        "size": {"x": 12, "y": 20},
        "name": "Kaguya Town"
    },
    "synecdoche_city": {
        "position": {"x": 119, "y": 131},
        "size": {"x": 28, "y": 28},
        "name": "Synecdoche City"
    },
    "zubrowka_city": {
        "position": {"x": 67, "y": 139},
        "size": {"x": 20, "y": 20},
        "name": "Zubrowka City"
    },
    "port_inisherin": {
        "position": {"x": 195, "y": 147},
        "size": {"x": 28, "y": 20},
        "name": "Port Inisherin"
    },
    "baxter_city": {
        "position": {"x": 135, "y": 199},
        "size": {"x": 28, "y": 20},
        "name": "Baxter City"
    },
    "juvet_town": {
        "position": {"x": 83, "y": 27},
        "size": {"x": 20, "y": 12},
        "name": "Juvet Town"
    },
    "fletcher_village": {
        "position": {"x": 125, "y": 45},
        "size": {"x": 20, "y": 12},
        "name": "Fletcher Village"
    },
    "vanya_town": {
        "position": {"x": 135, "y": 267},
        "size": {"x": 28, "y": 20},
        "name": "Vanya Town"
    },
    "port_endurance": {
        "position": {"x": 287, "y": 147},
        "size": {"x": 20, "y": 20},
        "name": "Port Endurance"
    },
    "grenoble_city": {
        "position": {"x": 339, "y": 163},
        "size": {"x": 28, "y": 20},
        "name": "Grenoble City"
    },
    "sen_village": {
        "position": {"x": 365, "y": 213},
        "size": {"x": 20, "y": 12},
        "name": "Sen Village"
    }
}

MAP_REQS = {
    "surf": ["route_16", "route_17", "snorlax_island"],
    "flash": ["drilbur_cave_1f", "drilbur_cave_2f"],
    "cut": ["vitur_forest"],
    "rocksmash": [],
    "dive": []
}

GYM_LEADERS = {
    "grass": {"npc": "erika", "name": "Erika", "reg": "070", "elite": "003", "level": 15},
    "electric": {"npc": "elesa", "name": "Elesa", "reg": "522", "elite": "466", "level": 22},
    "water": {"npc": "marlon", "name": "Marlon", "reg": "364", "elite": "130", "level": 28},
    "ground": {"npc": "giovanni", "name": "Giovanni", "reg": "031", "elite": "530", "level": 35},
    "fighting": {"npc": "bruno", "name": "Bruno", "reg": "107", "elite": "534", "level": 41},
    "fire": {"npc": "blaine", "name": "Blaine", "reg": "059", "elite": "257", "level": 48},
    "ghost": {"npc": "shauntal", "name": "Shauntal", "reg": "609", "elite": "094", "level": 54},
    "psychic": {"npc": "caitlin", "name": "Caitlin", "reg": "518", "elite": "488", "level": 61},
    "steel": {"npc": "steven", "name": "Steven", "reg": "227", "elite": "376", "level": 67},
    "dragon": {"npc": "clair", "name": "Clair", "reg": "621", "elite": "445", "level": 74}
}

EV_COACHES = {
    "hp": {"npc": "norman", "name": "HP Training", "pokemon": "242", "level": 25},
    "atk": {"npc": "chuck", "name": "Attack Training", "pokemon": "068", "level": 25},
    "def": {"npc": "brock", "name": "Defense Training", "pokemon": "306", "level": 25},
    "spa": {"npc": "sabrina", "name": "Special Attack Training", "pokemon": "065", "level": 25},
    "spd": {"npc": "wake", "name": "Special Defense Training", "pokemon": "272", "level": 25},
    "spe": {"npc": "winona", "name": "Speed Training", "pokemon": "018", "level": 25}
}

STAT_BOOSTS = {
    6: 4,
    5: 3.5,
    4: 3,
    3: 2.5,
    2: 2,
    1: 1.5,
    0: 1,
    -1: 2/3,
    -2: 2/4,
    -3: 2/5,
    -4: 2/6,
    -5: 2/7,
    -6: 2/8
}

PLAYER_STATE = {
    "current_pokemon": 0,
    "contributors": [],
    "stat_boosts": {
        "attack": 0,
        "defense": 0,
        "special_attack": 0,
        "special_defense": 0,
        "speed": 0,
        "accuracy": 0,
        "evasion": 0
    },
    "entry_hazards": [],
    "confusion": 0,
    "locked_moves": [],
    "defense_active": [],
    "tailwind": None,
    "name": None,
    "trapped": 0,
    "choice": None,
    "inventory": None,
    "participants": [],
    "misc": {}
}

TYPE_EFFECTIVENESS = {
    ("normal", "rock"): 0.5,
    ("normal", "ghost"): 0,
    ("normal", "steel"): 0.5,
    ("fire", "fire"): 0.5,
    ("fire", "water"): 0.5,
    ("fire", "grass"): 2,
    ("fire", "ice"): 2,
    ("fire", "bug"): 2,
    ("fire", "rock"): 0.5,
    ("fire", "dragon"): 0.5,
    ("fire", "steel"): 2,
    ("water", "fire"): 2,
    ("water", "water"): 0.5,
    ("water", "grass"): 0.5,
    ("water", "ground"): 2,
    ("water", "rock"): 2,
    ("water", "dragon"): 0.5,
    ("grass", "fire"): 0.5,
    ("grass", "water"): 2,
    ("grass", "grass"): 0.5,
    ("grass", "poison"): 0.5,
    ("grass", "ground"): 2,
    ("grass", "flying"): 0.5,
    ("grass", "bug"): 0.5,
    ("grass", "rock"): 2,
    ("grass", "dragon"): 0.5,
    ("grass", "steel"): 0.5,
    ("electric", "water"): 2,
    ("electric", "grass"): 0.5,
    ("electric", "electric"): 0.5,
    ("electric", "ground"): 0,
    ("electric", "flying"): 2,
    ("electric", "dragon"): 0.5,
    ("ice", "fire"): 0.5,
    ("ice", "water"): 0.5,
    ("ice", "grass"): 2,
    ("ice", "ice"): 0.5,
    ("ice", "ground"): 2,
    ("ice", "flying"): 2,
    ("ice", "dragon"): 2,
    ("ice", "steel"): 0.5,
    ("fighting", "normal"): 2,
    ("fighting", "ice"): 2,
    ("fighting", "poison"): 0.5,
    ("fighting", "flying"): 0.5,
    ("fighting", "psychic"): 0.5,
    ("fighting", "bug"): 0.5,
    ("fighting", "rock"): 2,
    ("fighting", "ghost"): 0,
    ("fighting", "dark"): 2,
    ("fighting", "steel"): 2,
    ("fighting", "fairy"): 0.5,
    ("poison", "grass"): 2,
    ("poison", "poison"): 0.5,
    ("poison", "ground"): 0.5,
    ("poison", "rock"): 0.5,
    ("poison", "ghost"): 0.5,
    ("poison", "steel"): 0,
    ("poison", "fairy"): 2,
    ("ground", "fire"): 2,
    ("ground", "grass"): 0.5,
    ("ground", "electric"): 2,
    ("ground", "poison"): 2,
    ("ground", "flying"): 0,
    ("ground", "bug"): 0.5,
    ("ground", "rock"): 2,
    ("ground", "steel"): 2,
    ("flying", "grass"): 2,
    ("flying", "electric"): 0.5,
    ("flying", "fighting"): 2,
    ("flying", "bug"): 2,
    ("flying", "rock"): 0.5,
    ("flying", "steel"): 0.5,
    ("psychic", "fighting"): 2,
    ("psychic", "poison"): 2,
    ("psychic", "psychic"): 0.5,
    ("psychic", "dark"): 0,
    ("psychic", "steel"): 0.5,
    ("bug", "fire"): 0.5,
    ("bug", "grass"): 2,
    ("bug", "fighting"): 0.5,
    ("bug", "poison"): 0.5,
    ("bug", "flying"): 0.5,
    ("bug", "psychic"): 2,
    ("bug", "ghost"): 0.5,
    ("bug", "dark"): 2,
    ("bug", "steel"): 0.5,
    ("bug", "fairy"): 0.5,
    ("rock", "fire"): 2,
    ("rock", "ice"): 2,
    ("rock", "fighting"): 0.5,
    ("rock", "ground"): 0.5,
    ("rock", "flying"): 2,
    ("rock", "bug"): 2,
    ("rock", "steel"): 0.5,
    ("ghost", "normal"): 0,
    ("ghost", "psychic"): 2,
    ("ghost", "ghost"): 2,
    ("ghost", "dark"): 0.5,
    ("dragon", "dragon"): 2,
    ("dragon", "steel"): 0.5,
    ("dragon", "fairy"): 0,
    ("dark", "fighting"): 0.5,
    ("dark", "psychic"): 2,
    ("dark", "ghost"): 2,
    ("dark", "dark"): 0.5,
    ("dark", "fairy"): 0.5,
    ("steel", "fire"): 0.5,
    ("steel", "water"): 0.5,
    ("steel", "electric"): 0.5,
    ("steel", "ice"): 2,
    ("steel", "rock"): 2,
    ("steel", "steel"): 0.5,
    ("steel", "fairy"): 2,
    ("fairy", "fire"): 0.5,
    ("fairy", "fighting"): 2,
    ("fairy", "poison"): 0.5,
    ("fairy", "dragon"): 2,
    ("fairy", "dark"): 2,
    ("fairy", "steel"): 0.5
}

# Functions for checking that the user passes some test
def user_not_in_battle(user):
    if user.profile.current_battle is not None:
        return False
    return True


def user_not_in_gauntlet(user):
    if user.profile.current_gauntlet is not None:
        return False
    return True