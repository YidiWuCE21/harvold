from harvoldsite import consts
from django.conf import settings

def asset_paths(request):
    return {
        "asset_paths": consts.ASSET_PATHS,
    }


def party(request):
    try:
        party = request.user.profile.get_party()
        party = [pkmn.get_party_info() if pkmn is not None else None for pkmn in party]
        return {
            "party": party
        }
    except AttributeError:
        return {
            "party": None
        }