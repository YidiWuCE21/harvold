from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
import map.views as map_views
import pokemon.views as pokemon_views
import accounts.views as account_views
import battle.views as battle_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    #path("map/", include("map.urls")),
    path("map", map_views.map, name="map"),
    path("world_map", map_views.world_map, name="world_map"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Account related views
    path("profile", account_views.view_profile, name="view_profile"),
    # Trainer related views
    path("box", pokemon_views.box, name="box"),
    path("pokemon", pokemon_views.pokemon, name="pokemon"),
    path("make", pokemon_views.make, name="make"),
    path("pokecenter", pokemon_views.pokecenter, name="pokecenter"),
    path("pokemart", pokemon_views.pokemart, name="pokemart"),
    # Battle related views
    path("gyms", battle_views.gyms, name="gyms"),
    #path('', include('users.urls'))
    # AJAX requests
    path("map_data/", map_views.map_data, name="map_data"),
    path("wild_battle/", map_views.wild_battle, name="wild_battle"),
    path("pokecenter_heal", pokemon_views.pokecenter_heal, name="pokecenter_heal")
]
