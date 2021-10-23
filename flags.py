import os
import json

flags_dir = os.path.join("flags", "1x1")

f = []
for (dirpath, dirnames, filenames) in os.walk(flags_dir):
    f.extend(filenames)
    break

codes = [name.replace('.svg', '') for name in f]

country_json = open("country.json")
flags = json.load(country_json)
flags.sort(key=lambda x: x["flag_1x1"])

with open('country.json', 'w') as output:
    json.dump(flags, output, indent=2, sort_keys=True)


# Check if all files have names
countries = [flag["flag_1x1"][10:].replace('.svg', '') for flag in flags]

all_good = True

for code in codes:
  if code not in countries:
    print('Code not found in country.json:', code)
    all_good = False

for code in countries:
  if code not in codes:
    print('Flag icon not found for:', code)
    all_good = False


if all_good:
  print('All flag icons and country.json are in sync.')
