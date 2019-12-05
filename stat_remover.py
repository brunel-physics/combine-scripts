import json
import sys

with open(sys.argv[1], "r") as data_file:
    data = json.load(data_file)

for element in data["params"]:
    element.pop("hours", None)

data["params"] = [x for x in data["params"] if not x["name"].startswith("prop_bin")]

with open(sys.argv[1], "w") as data_file:
    data = json.dump(data, data_file)
