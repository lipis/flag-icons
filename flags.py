import os
import json

flags_dir = os.path.join("flags", "4x3")

f = []
for (dirpath, dirnames, filenames) in os.walk(flags_dir):
    f.extend(filenames)
    break

codes = [name.replace('.svg', '') for name in f]

country_json = open("country.json")
flags = json.load(country_json)
flags.sort(key=lambda x: x["flag_1x1"])

with open('country.json', 'w') as output:
    json.dump(flags, output, indent=2)
