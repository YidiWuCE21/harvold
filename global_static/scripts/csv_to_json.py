import pandas as pd
import json

with open('pokemon.csv') as pkmn:
    data = pd.read_csv(pkmn, encoding='cp850')

data = data[data["generation"] < 6]
data["abilities"] = data["abilities"].apply(lambda x: eval(x))
data["typing"] = data.apply(lambda x: [x["type1"], x["type2"]] if not pd.isna(x["type2"]) else [x["type1"]], axis=1)
data = data.drop(["del1", "del2", "type1", "type2"], axis=1)

nan_rows = data.isna().any(axis=1)
pokemon_nan = data[nan_rows]["pokedex_number"]
data.fillna(42069, inplace=True)
data = data.set_index("pokedex_number").to_dict("index")

with open('../data/pokemon.json', "w+") as pkmnn:
    json.dump(data, pkmnn)
print()