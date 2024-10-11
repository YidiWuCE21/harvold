import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

from harvoldsite import consts
from .models import Pokemon, populate_moveset, get_progress_to_next_level, create_pokemon


# Additional models required for signup
@login_required
def box(request):
    box = request.user.profile.get_pokemon(filter_by={"trainer": request.user.profile, "location": "box"})
    # Convert to JSON
    box = [json.dumps(pkmn) for pkmn in box]
    html_render_variables = {
        "box": box
    }
    return render(request, "pokemon/box_view.html", html_render_variables)


@login_required
def make(request):
    render_vars = {"made": False}
    if request.GET.get("dex") is not None:
        pkmn = create_pokemon(request.GET.get("dex").zfill(3), int(request.GET.get("level")), request.GET.get("sex"), shiny=False)
        pkmn.assign_trainer(request.user.profile)
        pkmn.save()
        render_vars["made"] = True
    return render(request, "pokemon/make.html", render_vars)



def pokemon(request):
    """
    Get the detailed view for a single Pokemon

    Only Pokemon with assigned trainers should be viewable to prevent
    peeking wild Pokemon stats
    """
    pokemon_id = request.GET.get("id")
    pokemon = Pokemon.objects.get(pk=pokemon_id)

    pokemon_info = pokemon.get_info()
    metadata = pokemon.get_metadata()
    stats = pokemon.get_stats()
    learnset = populate_moveset(pokemon.dex, pokemon.level, last_four=False)
    moveset = pokemon.get_moves()

    # Get the evolutions
    evolutions = pokemon.get_all_evolutions()
    valid_evolutions = pokemon.get_valid_evolutions()

    html_render_variables = {
        "dex": "001",
        "name": "Steelix",
        "info": pokemon_info,
        "metadata": metadata,
        "stats": stats,
        "learnset": learnset,
        "moveset": moveset,
        "in_box": bool(pokemon.location == "box"),
        "evolutions": evolutions,
        "valid_evolutions": valid_evolutions
    }

    return render(request, "pokemon/detailed.html", html_render_variables)