import json
import datetime
import pandas as pd
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseNotFound

# Create your views here.

from harvoldsite import consts
from .models import Pokemon, populate_moveset, get_progress_to_next_level, create_pokemon
from battle import battle_manager


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
    if os.environ.get("DEBUG") != "True":
        return HttpResponseNotFound("Enable debug mode to access this.")
    render_vars = {"made": False, "pkmn": {idx: pkmn["name"] for idx, pkmn in consts.POKEMON.items()}}
    if request.GET.get("dex") is not None:
        pkmn = create_pokemon(request.GET.get("dex").zfill(3), int(request.GET.get("level")), request.GET.get("sex"), shiny=request.GET.get("shiny", False) == "on", nature_override=request.GET.get("nature", None),
                              iv_advantage=3)
        pkmn.assign_trainer(request.user.profile)
        pkmn.save()
        render_vars["made"] = True
    return render(request, "pokemon/make.html", render_vars)



@login_required
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
    if pokemon.trainer is None:
        return HttpResponseNotFound("This Pokemon was released!")

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


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def pokecenter(request):
    html_render_variables = {
        "swarm_dex": "100",
        "time_of_day": "day",
        "next_time_of_day": "evening",
        "time_countdown": datetime.timedelta(minutes=6)
    }
    return render(request, "pokemon/pokecenter.html", html_render_variables)


@login_required
def pokecenter_heal(request):
    # Check if user is eligible for heal
    if request.user.profile.state == "idle" and request.user.profile.current_battle is None:
        party = request.user.profile.get_party()
        for pkmn in party:
            pkmn.full_heal()
        return JsonResponse({"msg": "Your party has been healed!"})
    else:
        return JsonResponse({"msg": "You cannot heal in a battle!"})

@login_required
def pokedex(request):
    pokedex_dict = {
        "<p>{dex}</p><img src='/static/{path}/{dex}.gif'>".format(path=consts.ASSET_PATHS["icon"], dex=dex): {
            "Name": "<a onclick=\"getDex({{dex: '{dex}'}})\">{name}</a>".format(name=data["name"], dex=dex),
            "Type": "".join(["<p><img src='/static/{path}/{type}.png'></p>".format(path=consts.ASSET_PATHS["typing"], type=type) for type in data["typing"]]),
            "HP": data["hp"],
            "Atk": data["attack"],
            "Def": data["defense"],
            "SpA": data["sp_attack"],
            "SpD": data["sp_defense"],
            "Spe": data["speed"],
            "BST": data["base_total"]
        } for dex, data in consts.POKEMON.items()
    }
    html_render_variables = {
        "pokedex_table": pd.DataFrame(pokedex_dict.values(), index=pokedex_dict.keys()).to_html(escape=False, table_id="pokedex", classes=["display", "compact"])
    }
    return render(request, "pokemon/pokedex.html", html_render_variables)

@login_required
def pokedex_detailed(request):
    dex = request.GET.get("payload[dex]")
    if dex not in consts.POKEMON:
        return HttpResponseNotFound("Not a valid number!")
    dex_data = consts.POKEMON[dex]
    maps = [route for route, spawns in consts.WILD.items() if any([dex_data["name"] in [wildspawn[0] for wildspawn in spawn_list["pokemon"]] for spawn_area, spawn_list in spawns.items()])]
    html_render_variables = {
        "dex_data": dex_data,
        "maps": maps,
        "dex": dex,
        "moves": {level: consts.MOVES[move] for level, move in consts.LEARNSETS[dex]["level"]},
        "description": consts.DESCRIPTIONS[dex]
    }
    return render(request, "pokemon/pokedex_detailed.html", html_render_variables)