import os
from harvoldsite import consts
from django.conf import settings

def asset_paths(request):
    return {
        "asset_paths": consts.ASSET_PATHS,
    }


def uid(request):
    try:
        return {
            "id_self": request.user.profile.pk
        }
    except AttributeError:
        return {
            "id_self": ""
        }


def party(request):
    try:
        party = request.user.profile.get_party(return_none=True)
        party = [pkmn.get_party_info() if pkmn is not None else None for pkmn in party]
        return {
            "party": party
        }
    except AttributeError:
        return {
            "party": None
        }


def inbox(request):
    try:
        return {"message_flash": request.user.profile.inbox_flag}
    except AttributeError:
        return {"message_flash": False}


def devtools(request):
    return {"devtools": os.environ.get("DEBUG")}