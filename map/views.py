import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

from harvoldsite import consts

# Create your views here.

@login_required
def map(request):
    map = request.POST.get("map", "oak_village")
    # Check for map access permission
    # Convert to JSON
    html_render_variables = {
        "map": map
    }
    return render(request, "map.html", html_render_variables)