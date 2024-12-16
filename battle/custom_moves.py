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
    obj.output.append({"text": description})
    obj.weather = weather
    if player.opponent.get_current_pokemon().held_item == booster:
        obj.weather_turns = random.randint(6, 9)
    else:
        obj.weather_turns = 6

SUPPORTED_MOVES = {
    "raindance": partial(generic_weather, weather="rain", description="It started to rain!", booster="damp-rock"),
    "sunnyday": partial(generic_weather, weather="sun", description="The sunlight got bright!", booster="heat-rock"),
    "sandstorm": partial(generic_weather, weather="sand", description="A sandstorm brewed!", booster="smooth-rock"),
    "hail": partial(generic_weather, weather="hail", description="It started to hail!", booster="icy-rock"),
}