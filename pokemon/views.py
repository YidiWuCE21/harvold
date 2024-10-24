import json
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound

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
        pkmn = create_pokemon(request.GET.get("dex").zfill(3), int(request.GET.get("level")), request.GET.get("sex"), shiny=request.GET.get("shiny", False) == "on", nature_override=request.GET.get("nature", None),
                              iv_advantage=3)
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
    # Get the pokemon
    if "id" in request.GET:
        pokemon_id = request.GET.get("id")
    elif "id" in request.POST:
        pokemon_id = request.POST.get("id")
    else:
        return HttpResponseNotFound("Cannot find Pokemon!")
    pokemon = Pokemon.objects.get(pk=pokemon_id)

    # Check for actions
    message = None
    if "action" in request.POST:
        action = request.POST.get("action")
        if action == "release":
            if request.user.profile == pokemon.trainer:
                pokemon.release(request.user.profile)
                return render(request, "common/message.html", {"message": "Successfully released {}".format(pokemon.name), "links": {"Return to Box": ""}, "title": "Released"})
        elif action == "add_party":
            message = request.user.profile.add_to_party(pokemon)
        elif action == "remove_party":
            message = request.user.profile.remove_from_party(pokemon)
        elif action == "evolve":
            evolution_target = request.POST.get("evolve_to")
            message = pokemon.evolve(evolution_target)[1]
        elif action == "teach_move":
            new_move = request.POST.get("move")
            slot = request.POST.get("replace_slot")
            message = pokemon.learn_move(new_move, slot)

    pokemon_info = pokemon.get_info()
    metadata = pokemon.get_metadata()
    stats = pokemon.get_stats()
    learnset = {move: consts.MOVES[move] for move in populate_moveset(pokemon.dex, pokemon.level, last_four=False)}
    moveset = pokemon.get_moves(pp=True)
    pokemon_data = consts.POKEMON[pokemon_info["dex"]]

    # Get the evolutions
    evolutions = pokemon.get_all_evolutions()
    valid_evolutions = pokemon.get_valid_evolutions()

    html_render_variables = {
        "message": message,
        "info": pokemon_info, # Pokemon-specific
        "data": pokemon_data, # Generic to species
        "metadata": metadata,
        "stats": stats,
        "learnset": learnset,
        "moveset": moveset,
        "in_box": bool(pokemon.location == "box"),
        "evolutions": evolutions,
        "valid_evolutions": valid_evolutions,
        "owned": pokemon.trainer == request.user.profile
    }

    return render(request, "pokemon/detailed.html", html_render_variables)


def pokecenter(request):
    html_render_variables = {
        "swarm_dex": "100",
        "time_of_day": "day",
        "next_time_of_day": "evening",
        "time_countdown": datetime.timedelta(minutes=6)
    }
    return render(request, "pokemon/pokecenter.html", html_render_variables)


def pokecenter_heal(request):
    # Check if user is eligible for heal
    if request.user.profile.state == "idle":
        party = request.user.profile.get_party()
        for pkmn in party:
            pkmn.full_heal()
        return JsonResponse({"msg": "Your party has been healed!"})
    else:
        return JsonResponse({"msg": "You cannot heal in a battle!"})
def pokemart(request):
    html_render_variables = {
    }
    return render(request, "pokemon/pokemart.html", html_render_variables)