import json
import os
import random
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse

# Create your views here.

from harvoldsite import consts
from pokemon.models import create_pokemon

# Create your views here.
@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
@csrf_exempt
def update_pos(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data from the request body
            position = json.loads(request.body)['pos']
            player = request.user.profile
            map = position.pop('map')
            if map != player.current_map:
                return HttpResponse(status=400)
            player.current_pos = position
            print(position)
            player.save()
            print(position)
            print("saved")
            # Update your database with the data here (e.g., saving to models)
            # Example: MyModel.objects.create(field1=data['field1'], field2=data['field2'])

            # Since you don't need any content in the response, return 204 No Content
            return HttpResponse(status=204)
        except Exception as e:
            # You can return an error status if needed, but as per your request, we don't need to send back any response.
            return HttpResponse(status=400)  # Bad request in case of error

    return HttpResponse(status=405)


@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
def map(request):
    default_map = request.user.profile.current_map
    map = request.POST.get("map", default_map)
    if map not in consts.MAPS:
        return HttpResponseNotFound("Invalid map")
    with open(os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map)), encoding="utf-8") as map_file:
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
        "character": user.char_id,
        "position": json.dumps(user.current_pos if "map" not in request.POST else None)
    }
    return render(request, "map/map.html", html_render_variables)

@login_required
@user_passes_test(consts.user_not_in_battle, login_url="/battle")
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
    with open(os.path.join(consts.STATIC_PATH, "data", "maps", "{}.json".format(map)), encoding="utf-8") as map_file:
        map_data = json.load(map_file)
    # Update current location of user
    user = request.user.profile
    user.current_map = map
    user.current_pos = None
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
    dex_number = consts.DEX_LOOKUP[wild_pokemon[0]]

    # Roll for level, sex, and shininess
    level = random.randrange(wild_pokemon[1], wild_pokemon[2])
    shiny = random.random() < 0.001
    percentage_male = consts.POKEMON[dex_number]["percentage_male"]
    sex = "g" if percentage_male < 0 else "m" if random.random() * 100 < percentage_male else "f"

    # If there is an existing wild opponent, delete it
    user.wild_opponent = {"dex": dex_number, "level": level, "shiny": shiny, "sex": sex}
    user.save()

    # Send the Pokemon species, level, and shininess
    pokeinfo = {
        "dex_number": dex_number,
        "name": consts.POKEMON[dex_number]["name"],
        "level": level,
        "sex": sex,
        "shiny": shiny
    }
    print("Completed in: {}".format((datetime.datetime.now() - now).total_seconds()))
    return JsonResponse(pokeinfo)