import os
import json

from django.templatetags.static import static
# Generic helper function file

def get_pokemon_sprite(dex, shiny=False, sprite_type="front", get_path=False):
    """
    Helper function to retrieve sprite files

    Valid sprite types are front, back, icon, overworld
    """
    ext = "png"
    if sprite_type in ["icon"]:
        ext = "gif"
    if shiny:
        sprite_file = "{}-S.{}".format(dex, ext)
    else:
        sprite_file = "{}.{}".format(dex, ext)
    file_path = os.path.join("assets", "pokemon", sprite_type, sprite_file)
    full_path = os.path.join(os.getcwd(), "global_static", file_path)

    if os.path.isfile(full_path):
        return full_path if get_path else file_path
    return None

