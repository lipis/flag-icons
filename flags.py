from __future__ import print_function
import os
import sys
import json

flags_dir = os.path.join("flags", "1x1")

files = []
for (dirpath, dirnames, filenames) in os.walk(flags_dir):
    files.extend(filenames)
    break

file_codes = [name.replace(".svg", "") for name in files]

country_json = open("country.json")
flags = json.load(country_json)
flags.sort(key=lambda x: x["code"])
country_codes = [flag["code"] for flag in flags]

with open("country.json", "w") as output:
    json.dump(flags, output, indent=2, sort_keys=True)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


all_good = True

# Check if all files have names
for code in file_codes:
    if code not in country_codes:
        eprint("Code not found in country.json:", code)
        all_good = False

# Check if all countries have files
for code in country_codes:
    if code not in file_codes:
        eprint("Flag icon not found for:", code)
        all_good = False


if all_good:
    print("All flag icons and country.json are in sync.")
    exit(0)

exit(1)
