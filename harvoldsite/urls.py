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
    path("bag", account_views.bag, name="bag"),
    path("pokemart", account_views.pokemart, name="pokemart"),
    # Trainer related views
    path("box", pokemon_views.box, name="box"),
    path("pokemon", pokemon_views.pokemon, name="pokemon"),
    path("pokedex", pokemon_views.pokedex, name="pokedex"),
    path("make", pokemon_views.make, name="make"),
    path("pokecenter", pokemon_views.pokecenter, name="pokecenter"),
    # Battle related views
    path("gyms", battle_views.gyms, name="gyms"),
    path("battle", battle_views.battle, name="battle"),
    path("battle_create", battle_views.battle_create, name="battle_create"),
    #path('', include('users.urls'))
    # AJAX/fetch requests
    path("map_data/", map_views.map_data, name="map_data"),
    path("pokedex_detailed", pokemon_views.pokedex_detailed, name="pokedex_detailed"),
    path("wild_battle/", map_views.wild_battle, name="wild_battle"),
    path("pokecenter_heal", pokemon_views.pokecenter_heal, name="pokecenter_heal"),
    path("update_pos", map_views.update_pos, name="update_pos")
]
