import json
import os
import random
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse

# Create your views here.

from harvoldsite import consts
from pokemon.models import create_pokemon, swarm

# Create your views here.
def helper_check_map_access(map, user, msg=False):
    messages = {
        "surf": "The route ahead is filled with water. I should have a Pokémon with Surf before venturing onwards.",
        "cut": "The forest is thick with vines and cobwebs. I should have a Pokémon with Cut before venturing onwards.",
        "rocksmash": "The cave is blocked by debris. I should have a Pokémon with Rock Smash before venturing onwards.",
        "dive": "The water is too deep. I should have a Pokémon with Dive before venturing onwards.",
        "flash": "The cave is too dark to see in. I should have a Pokémon with Flash before venturing onwards.",
        "fly": "Can't."
    }
    for hm, maps in consts.MAP_REQS.items():
        if map in maps:
            if not user.can_use_hm(hm):
                if msg:
                    return messages[hm]
                return False
    return True


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
@csrf_exempt
def update_pos(request):
    """
    Function to update a player's position on its current map
    """
    if request.method == 'POST':
        try:
            position = json.loads(request.body)['pos']
            player = request.user.profile
            map = position.pop('map')
            # Check that player is still on the map
            if map != player.current_map:
                return HttpResponse(status=400)
            player.current_pos = position
            player.save()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponse(status=400)

    return HttpResponse(status=405)


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def map(request):
    """
    Function to open the map. Defaults to current map, but also checks session for new map in case was sent here from world map

    If map is not accessible, boot the user back to the last city and clear the current position
    """
    user = request.user.profile
    default_map = user.current_map
    # Check if we have a map stored from redirecting from world map
    map = request.session.get("map", default_map)
    # Go to last city if we are on inaccessible map
    if not helper_check_map_access(map, user):
        map = user.last_city
        user.current_pos = None
    # Update current location of user
    user.current_map = map
    if map in consts.CITIES:
        user.last_city = map
    if "map" in request.session:
        user.current_pos = None
        del request.session["map"]
    user.save()
    if map not in consts.MAPS:
        return HttpResponseNotFound("Invalid map")
    with open(os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map)), encoding="utf-8") as map_file:
        map_data = json.load(map_file)
    # Add the map name
    map_data["map_name"] = map.replace("_", " ").title()
    # Check for map access permission
    # HM usage
    hms = {
        "surf": user.can_use_hm("surf"),
        "flash": user.can_use_hm("flash"),
        "cut": user.can_use_hm("cut"),
        "dive": user.can_use_hm("dive"),
        "rocksmash": user.can_use_hm("rocksmash")
    }
    # Convert to JSON
    html_render_variables = {
        "map": map,
        "map_name": map.replace("_", " ").title(),
        "map_data": json.dumps(map_data),
        "character": user.char_id,
        "position": json.dumps(user.current_pos),
        "hms": json.dumps(hms)
    }
    return render(request, "map/map.html", html_render_variables)

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def world_map(request):
    """
    Function to open the world map. Can also be used to redirect to a specific map via session info
    """
    map = request.POST.get("map", None)
    if map is not None:
        request.session["map"] = map
        return redirect("map")
    html_render_variables = {
        "maps": consts.MAPS,
        "cities": consts.CITIES
    }
    return render(request, "map/world_map.html", html_render_variables)

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@user_passes_test(consts.user_not_in_gauntlet, login_url="/gauntlet")
def swarm_map(request):
    """
    Function to open the swarm map.
    """
    swarm_pokemon, route = swarm(datetime.now())
    request.session["map"] = route
    return redirect("map")


@login_required
def map_data(request):
    """
    Function for map transition while already on map
    """
    map = request.GET.get("payload[map]")
    user = request.user.profile
    msg = helper_check_map_access(map, user, msg=True)
    if msg is not True:
        return JsonResponse({"error": msg}, status=400)
    if map not in consts.MAPS:
        return JsonResponse({"error": "Invalid map"}, status=500)
    with open(os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map)), encoding="utf-8") as map_file:
        map_data = json.load(map_file)
    # Update current location of user
    user.current_map = map
    if map in consts.CITIES:
        user.last_city = map
    user.current_pos = None
    user.save()
    # Add the map name
    map_data["map_name"] = map.replace("_", " ").title()

    return JsonResponse(map_data)


@login_required
def wild_battle(request):
    """
    Function to generate a wild battle
    """
    map = request.GET.get("payload[map]")
    area = request.GET.get("payload[area]")
    user = request.user.profile

    # Find the list of available Pokemon and get one randomly
    if area not in consts.WILD[map]:
        return JsonResponse({"status": "false", "message": "{} not recognized as a valid area".format(area)}, status=500)

    try:
        wild_choices = consts.WILD[map][area]["pokemon"]
        weights = consts.WILD[map][area]["weights"]

        # Check if swarming, append swarm to list
        swarm_pokemon, route = swarm(datetime.now())
        if route == map and area != "water":
            wild_choices.append(consts.POKEMON[swarm_pokemon]["name"])
            # 1/5a chance of swarm appearing
            weights.append(sum(weights) / 4)

        wild_pokemon = random.choices(wild_choices, weights)
        dex_number = consts.DEX_LOOKUP[wild_pokemon[0]]
        bg = consts.WILD[map][area].get("bg", "water" if area == "water" else "grass")

        # Roll for level, sex, and shininess
        level = random.randrange(consts.WILD[map]["levels"][0], consts.WILD[map]["levels"][1])
        shiny = random.random() < 0.001
        percentage_male = consts.POKEMON[dex_number]["percentage_male"]
        sex = "g" if percentage_male < 0 else "m" if random.random() * 100 < percentage_male else "f"

        # If there is an existing wild opponent, delete it
        user.wild_opponent = {"dex": dex_number, "level": level, "shiny": shiny, "sex": sex, "bg": bg}
        user.save()
    except Exception as e:
        JsonResponse({"status": "false", "message": str(e)})

    # Send the Pokemon species, level, and shininess
    pokeinfo = {
        "dex_number": dex_number,
        "name": consts.POKEMON[dex_number]["name"],
        "level": level,
        "sex": sex,
        "shiny": shiny
    }
    return JsonResponse(pokeinfo)


@login_required
def map_editor_select(request):
    if os.environ.get("DEBUG") != "True":
        return HttpResponseNotFound("Enable debug mode to access this.")
    html_render_variables = {
        "maps": consts.MAPS
    }
    return render(request, "map/editor_select.html", html_render_variables)


@login_required
def map_editor(request):
    if os.environ.get("DEBUG") != "True":
        return HttpResponseNotFound("Enable debug mode to access this.")
    wild_info = consts.WILD.get(request.GET.get("map"), {"levels": "None"})
    map = request.GET.get("map")

    # Get the existing data
    """map_file = os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map))
    with open(map_file, "r", encoding='utf-8') as f:
        map_data = json.load(f)
        trainers = map_data["trainers"]"""


    html_render_variables = {
        "map": request.GET.get("map"),
        "trainers": [[f[:-4], f[:-4]] for f in os.listdir(os.path.join("global_static", consts.ASSET_PATHS["trainer_ow"])) if f.endswith('.png')],
        "pokemon": [[dex, data["name"]] for dex, data in consts.POKEMON.items()],
        "level": wild_info["levels"],
        "wild": [pkmn["pokemon"] for area, pkmn in wild_info.items() if area != "levels"],
        "prevData": json.dumps(trainers)
    }
    return render(request, "map/editor.html", html_render_variables)


@login_required
def submit_edit(request):
    if os.environ.get("DEBUG") != "True":
        return HttpResponseNotFound("Enable debug mode to access this.")

    map = request.POST.get("map")
    INSERT_MODE = True
    npc_data = json.loads(request.POST.get("npc_data"))
    battlers = []
    npc_list = []
    # Extract data
    for npc in npc_data:
        npc_list.append(npc["map"])
        if "gen" in npc:
            battlers.append(npc["gen"])

    # Edit the map file with trainers
    map_file = os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map))
    with open(map_file, "r", encoding='utf-8') as f:
        map_data = json.load(f)
        if INSERT_MODE:
            map_data["trainers"] += npc_list
        else:
            map_data["trainers"] = npc_list
    with open(map_file, "w+", encoding='utf-8') as f:
        json.dump(map_data, f)

    # For each trainer with battles, create a battle file
    battle_dir = os.path.join(consts.STATIC_PATH, "data", "trainers", map)
    os.makedirs(battle_dir, exist_ok=True)
    for battler in battlers:
        if not battler["team"]:
            continue
        team = []
        for pkmn in battler["team"]:
            team.append(create_pokemon(pkmn["dex"], level=pkmn["level"], sex="g", skip_save=True))
        battler_data = {
            "name": battler["name"],
            "bg": battler["bg"],
            "team": team,
            "reward": {"base_payout": consts.PAYOUTS.get(battler["sprite"], 16)},
            "map": map,
            "sprite": battler["sprite"],
            "lines": {
                "lose": battler["lose"]
            }
        }
        with open(os.path.join(battle_dir, "{}.json".format(battler["file"])), "w+", encoding='utf-8') as f:
            json.dump(battler_data, f)

    request.session["map"] = map
    return redirect("map")