import os
import json

dir_1x1 = os.path.join("flags", "1x1")
dir_4x3 = os.path.join("flags", "4x3")

files = []
for (dirpath, dirnames, filenames) in os.walk(dir_1x1):
    files.extend(filenames)
    break


def add_ids(directory):
    for f in files:
        filename = os.path.join(directory, f)
        update = False
        flag_id = "flag-icons-%s" % (f.replace(".svg", ""))
        with open(filename, "r") as flag:
            lines = flag.readlines()
            if lines[0].find("id") == -1 and lines[0].find("viewBox") > 0:
                lines[0] = lines[0].replace("viewBox", 'id="%s" viewBox' % flag_id)
                update = True

        if update:
            print("Adding ID to", filename)
            with open(filename, "w") as flag:
                flag.writelines(lines)


add_ids(dir_1x1)
add_ids(dir_4x3)
