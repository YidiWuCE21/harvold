from django.shortcuts import render

# Create your views here.

from harvoldsite import consts
from .models import Pokemon, populate_moveset, get_progress_to_next_level


# Additional models required for signup


def pokemon(request):
    pokemon_id = request.GET.get("id")
    pokemon = Pokemon.objects.get(pk=pokemon_id)
    pokedex_info = consts.POKEMON[pokemon.dex_number]

    metadata = {
        "Level": pokemon.level,
        "Experience": get_progress_to_next_level(pokemon.level, pokemon.experience, pokedex_info["experience_growth"]),
        "Sex": pokemon.sex,
        "Ability": pokemon.ability,
        "Owner": pokemon.trainer.user.username,
        "Original Trainer": pokemon.original_trainer.user.username,
        "Date Caught": pokemon.caught_date,
        "Happiness": pokemon.happiness,
        "Held Item": pokemon.held_item
    }
    stats = {
        "HP": (pokemon.hp_stat, pokemon.hp_iv, pokemon.hp_ev),
        "Attack": (pokemon.atk_stat, pokemon.atk_iv, pokemon.atk_ev),
        "Defense": (pokemon.def_stat, pokemon.def_iv, pokemon.def_ev),
        "Special Attack": (pokemon.spa_stat, pokemon.spa_iv, pokemon.spa_ev),
        "Special Defense": (pokemon.spd_stat, pokemon.spd_iv, pokemon.spd_ev),
        "Speed": (pokemon.spe_stat, pokemon.spe_iv, pokemon.spe_ev)
    }
    learnset = populate_moveset(pokemon.dex_number, pokemon.level, last_four=False)
    moveset = {
        "move1": pokemon.move1,
        "move2": pokemon.move2,
        "move3": pokemon.move3,
        "move4": pokemon.move4,
    }
    html_render_variables = {
        "dex": "001",
        "name": "Steelix",
        "metadata": metadata,
        "stats": stats,
        "learnset": learnset,
        "moveset": moveset,
        "in_box": bool(pokemon.location == "box")
    }

    return render(request, "pokemon/detailed.html", html_render_variables)