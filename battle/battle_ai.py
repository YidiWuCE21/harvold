import random
from harvoldsite import consts
from functools import partial

def get_move(battle_state, ai="first_move"):
    ai_choices = {
        "first_move": first_move,
        "strongest_move": strongest_move,
        "random_move": random_move
    }
    return ai_choices[ai](battle_state)


def get_valid_choices(battle_state):
    valid_choices = []
    for move in battle_state.player_2.get_current_pokemon().moves:
        if move["pp"] != None:
            if move["pp"] > 0:
                valid_choices.append(move["move"])
    return valid_choices

def first_move(battle_state):
    return {"action": "attack", "move": battle_state.player_2.get_current_pokemon().moves[0]["move"]}

def strongest_move(battle_state):
    valid_choices = get_valid_choices(battle_state)
    best_move = random.choice(valid_choices)
    highest_damage = 0
    for move in valid_choices:
        move_data = consts.MOVES[move]
        damage = battle_state.move_damage(
            battle_state.player_2,
            battle_state.player_2.get_current_pokemon(),
            battle_state.player_1.get_current_pokemon(),
            move_data["type"],
            move_data["power"],
            move_data["damage_class"],
            1
        )
        if damage > highest_damage:
            highest_damage = damage
            best_move = move
    return {"action": "attack", "move": best_move}

def random_move(battle_state):
    valid_choices = get_valid_choices(battle_state)
    return {"action": "attack", "move": random.choice(valid_choices)}