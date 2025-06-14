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
    path("credits", TemplateView.as_view(template_name="common/credits.html"), name="credits"),
    #path("map/", include("map.urls")),
    path("map", map_views.map, name="map"),
    path("swarm_map", map_views.swarm_map, name="swarm_map"),
    path("world_map", map_views.world_map, name="world_map"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Account related views
    path("profile", account_views.view_profile, name="view_profile"),
    path("bag", account_views.bag, name="bag"),
    path("pokemart", account_views.pokemart, name="pokemart"),
    path("inbox", account_views.inbox, name="inbox"),
    # Trainer related views
    path("box", pokemon_views.box, name="box"),
    path("pokemon", pokemon_views.pokemon, name="pokemon"),
    path("pokedex", pokemon_views.pokedex, name="pokedex"),
    path("pokecenter", pokemon_views.pokecenter, name="pokecenter"),
    path("pokelab", pokemon_views.pokelab, name="pokelab"),
    path("revive_fossil", pokemon_views.revive_fossil, name="revive_fossil"),
    # Battle related views
    path("gyms", battle_views.gyms, name="gyms"),
    path("ev_dojo", battle_views.ev_dojo, name="ev_dojo"),
    path("battle", battle_views.battle, name="battle"),
    path("gauntlet", battle_views.gauntlet, name="gauntlet"),
    path("battle_create", battle_views.battle_create, name="battle_create"),
    path("battle_mansion_start", battle_views.battle_mansion_start, name="battle_mansion_start"),
    path("battle_mansion", battle_views.battle_mansion_page, name="battle_mansion"),
    # Devtools
    path("make", pokemon_views.make, name="make"),
    path("map_editor_select", map_views.map_editor_select, name="map_editor_select"),
    path("map_editor", map_views.map_editor, name="map_editor"),
    path("submit_edit", map_views.submit_edit, name="submit_edit"),
    #path('', include('users.urls'))
    # AJAX/fetch requests
    path("map_data/", map_views.map_data, name="map_data"),
    path("pokedex_detailed", pokemon_views.pokedex_detailed, name="pokedex_detailed"),
    path("wild_battle/", map_views.wild_battle, name="wild_battle"),
    path("pokecenter_heal", pokemon_views.pokecenter_heal, name="pokecenter_heal"),
    path("update_pos", map_views.update_pos, name="update_pos"),
    path("remove_party_ajax", account_views.remove_party_ajax, name="remove_party_ajax"),
    path("reorder_party_ajax", account_views.reorder_party_ajax, name="reorder_party_ajax"),
    path("teach_tm_ajax", account_views.teach_tm_ajax, name="teach_tm_ajax"),
    path("use_bag_item_ajax", account_views.use_bag_item_ajax, name="use_bag_item_ajax"),
    path("take_held_item_ajax", account_views.take_held_item_ajax, name="take_held_item_ajax"),
    path("give_held_item_ajax", account_views.give_held_item_ajax, name="give_held_item_ajax"),
    path("read_message_ajax", account_views.read_message_ajax, name="read_message_ajax")
]
