from harvoldsite import consts
from django.conf import settings

def asset_paths(request):
    return {
        "asset_paths": consts.ASSET_PATHS,
    }