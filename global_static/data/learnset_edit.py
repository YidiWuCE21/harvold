import json

with open('learnsets.json') as ls:
    data = json.load(ls)
with open('moves.json') as ls:
    moves = json.load(ls)

moves = {move_data["ename"].replace(" ", "").lower(): move_data for move_data in moves}
moves = {k: {d: l for d, l in v.items() if d not in ["cname", "jname", "category"]} for k, v in moves.items()}
moves = {k: {d if d != "ename" else "name": l for d, l in v.items()} for k, v in moves.items()}
print()

"""dex = {str(k).zfill(3): v for k, v in dex.items()}
with open('pokemon.json', "w+") as pkpk:
    json.dump(dex, pkpk)"""

"""id_map = {id: str(id) for id, asd in dex.items()}
new_data = {}
for poke in data:
    data[poke]["level"].sort(key=lambda x: int(x[0]))
    if poke in id_map:
        new_data[str(id_map[poke]).zfill(3)] = data[poke]
with open('learnsets.json', "w+") as ls:
    json.dump(new_data, ls)"""