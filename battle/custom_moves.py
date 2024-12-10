"""
Python file for defining all the move-specific functions
"""
import random

def raindance(obj, player):
    # Check for air lock
    if player.opponent.get_current_pokemon().ability in ["Air Lock", "Cloud Nine"] or obj.weather == "rain":
        obj.output.append({"text": "But it failed!"})
        return
    obj.output.append({"text": "It started to rain!"})
    obj.weather = "rain"
    if player.opponent.get_current_pokemon().held_item == "damp-rock":
        obj.weather_turns = random.randint(6, 9)
    else:
        obj.weather_turns = 6

SUPPORTED_MOVES = {
    "raindance": raindance
}