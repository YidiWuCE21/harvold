"""
Python file for defining all the move-specific functions
"""
import random
from functools import partial

def generic_weather(obj, player, weather, description, booster):
    # Check for air lock
    if player.opponent.get_current_pokemon().ability in ["Air Lock", "Cloud Nine"] or obj.weather == weather:
        obj.output.append({"text": "But it failed!"})
        return
    if "{}" in description:
        description.format(player.get_current_pokemon().name)
    obj.output.append({"text": description})
    obj.weather = weather
    if player.opponent.get_current_pokemon().held_item == booster:
        obj.weather_turns = random.randint(6, 9)
    else:
        obj.weather_turns = 6


def attempt_defense(obj, player, defense_type):
    # Roll successful defense
    successes = player.misc.get("successful_defense", 0)
    fail_chance = -1
    if successes > 0:
        fail_chance = (1 / 3) ** successes * 100
    if random.randrange(100) < fail_chance:
        obj.output.append({"text": "But it failed!"})
    else:
        player.defense_active = defense_type

SUPPORTED_MOVES = {
    "raindance": partial(generic_weather, weather="rain", description="It started to rain!", booster="damp-rock"),
    "sunnyday": partial(generic_weather, weather="sun", description="The sunlight got bright!", booster="heat-rock"),
    "sandstorm": partial(generic_weather, weather="sand", description="A sandstorm brewed!", booster="smooth-rock"),
    "hail": partial(generic_weather, weather="hail", description="It started to hail!", booster="icy-rock"),
    "protect": partial(attempt_defense, defense_type="protect"),
    "detect": partial(attempt_defense, defense_type="protect"),
    "endure": partial(attempt_defense, defense_type="endure")
}

def intimidate(obj, player):
    obj.output.append({"text": "{} is intimidated by {}!".format(player.opponent.get_current_pokemon().name, player.get_current_pokemon().name)})
    obj.apply_boosts(player, "growl")

SUPPORTED_ABILITIES = {
    "Drizzle": partial(generic_weather, weather="rain", description="{}'s Drizzle made it rain!", booster="damp-rock"),
    "Drought": partial(generic_weather, weather="sun", description="{}'s Drought intensified the sun's rays!", booster="heat-rock"),
    "Sand Stream": partial(generic_weather, weather="sand", description="{}'s Sand Stream whipped up a sandstorm!", booster="smooth-rock"),
    "Snow Warning": partial(generic_weather, weather="hail", description="{}'s Snow Warning whipped up a hailstorm!", booster="icy-rock"),
    "Intimidate": intimidate
}