from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
import items.views as item_views
import map.views as map_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("battle/", include("battle.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("pokemon/", include("pokemon.urls")),
    #path("map/", include("map.urls")),
    path("map/", map_views.map, name="map"),
    path("world_map/", map_views.world_map, name="world_map"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Account related views
    # Trainer related views
    # Battle related views
    #path('', include('users.urls'))
    # AJAX requests
    path("map_data/", map_views.map_data, name="map_data")
]
