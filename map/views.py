import json
import os
import random
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound

# Create your views here.

from harvoldsite import consts
from pokemon.models import create_pokemon

# Create your views here.

@login_required
def map(request):
    map = request.POST.get("map", "oak_village")
    if map not in consts.MAPS:
        return HttpResponseNotFound("Invalid map")
    with open(os.path.join(consts.ASSETS_PATH, "data", "maps", "{}.json".format(map))) as map_file:
        map_data = json.load(map_file)
    # Update current location of user
    user = request.user.profile
    user.current_map = map
    user.save()
    # Add the map name
    map_data["map_name"] = map.replace("_", " ").title()
    # Check for map access permission
    # Convert to JSON
    html_render_variables = {
        "map": map,
        "map_name": map.replace("_", " ").title(),
        "map_data": json.dumps(map_data),
        "character": user.char_id
    }
    return render(request, "map/map.html", html_render_variables)

@login_required
def world_map(request):
    html_render_variables = {
        "maps": consts.MAPS
    }
    return render(request, "map/world_map.html", html_render_variables)


@login_required
def map_data(request):
    map = request.GET.get("payload[map]")
    if map not in consts.MAPS:
        return JsonResponse({"status": "false", "message": "Invalid map"}, status=500)
    with open(os.path.join(consts.ASSETS_PATH, "data", "maps", "{}.json".format(map))) as map_file:
        map_data = json.load(map_file)
    # Update current location of user
    user = request.user.profile
    user.current_map = map
    user.save()
    # Add the map name
    map_data["map_name"] = map.replace("_", " ").title()

    return JsonResponse(map_data)


@login_required
def wild_battle(request):
    map = request.GET.get("payload[map]")
    area = request.GET.get("payload[area]")
    user = request.user.profile
    now = datetime.datetime.now()

    # Check if user is actually on the map
    if user.current_map != map:
        return JsonResponse({"status": "false", "message": "You are not on this map!"}, status=500)

    # Find the list of available Pokemon and get one randomly
    if area not in consts.WILD[map]:
        return JsonResponse({"status": "false", "message": "{} not recognized as a valid area".format(area)}, status=500)

    wild_pokemon = random.choices(consts.WILD[map][area]["pokemon"], consts.WILD[map][area]["weights"])[0]
    dex_number = wild_pokemon[0]

    # Roll for level, sex, and shininess
    level = random.randrange(wild_pokemon[1], wild_pokemon[2])
    shiny = random.random() < 0.001
    percentage_male = consts.POKEMON[dex_number]["percentage_male"]
    sex = "g" if percentage_male < 0 else "m" if random.random() * 100 < percentage_male else "f"
    print("Gen rand in: {}".format((datetime.datetime.now() - now).total_seconds()))

    # If there is an existing wild opponent, delete it
    print("Delete wild in: {}".format((datetime.datetime.now() - now).total_seconds()))

    # Set the Pokemon as the current wild opponent; prevents client-side manipulation
    pokemon = create_pokemon(dex_number, level, sex, shiny)
    print("Create pokemon in: {}".format((datetime.datetime.now() - now).total_seconds()))
    user.wild_opponent = pokemon
    user.save()
    print("Save wild in: {}".format((datetime.datetime.now() - now).total_seconds()))

    # Send the Pokemon species, level, and shininess
    pokeinfo = {
        "dex_number": dex_number,
        "name": pokemon.name,
        "level": level,
        "sex": sex,
        "shiny": shiny,
        "id": pokemon.pk
    }
    print("Completed in: {}".format((datetime.datetime.now() - now).total_seconds()))
    return JsonResponse(pokeinfo)