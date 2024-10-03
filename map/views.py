import json
import os

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

from harvoldsite import consts

# Create your views here.

@login_required
def map(request):
    map = request.GET.get("map", "oak_village")
    # Check for map access permission
    # Convert to JSON
    html_render_variables = {
        "map": map
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
    return JsonResponse(map_data)