# UTILITY SCRIPT FOR SPRITE FILE RENAMING

import os, re

path = os.getcwd()
path = os.path.join(path, "pokemon", "front")
# icons
#pattern = "^ico-a_old_([0-9]+).gif$"
# front
#pattern = "^spr_bw_([0-9]+).png$"
# front shiny
#pattern = "^spr_bw-S_([0-9]+).png$"
replace = r"\1-S.gif"

comp = re.compile(pattern)
for f in os.listdir(path):
    full_path = os.path.join(path, f)
    if os.path.isfile(full_path):

        match = comp.search(f)
        if not match:
            continue

        try:
            new_name = match.expand(replace)
            new_name = os.path.join(path, new_name)
        except re.error:
            continue

        if os.path.isfile(new_name):
            print('%s -> %s skipped' % (f, new_name))
        else:
            os.rename(full_path, new_name)