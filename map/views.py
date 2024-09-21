import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

from harvoldsite import consts

# Create your views here.

@login_required
def map(request):
    box = request.user.profile.get_pokemon(filter_by={"trainer": request.user.profile, "location": "box"})
    # Convert to JSON
    box = [json.dumps(pkmn) for pkmn in box]
    html_render_variables = {
        "box": box
    }
    return render(request, "map.html", html_render_variables)