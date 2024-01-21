import json
import sys


with open(sys.argv[1]) as f:
    data = json.load(f)

with open(sys.argv[2],"w") as fout:
    for d in data:
        fout.write(d["text_result"] + "\n")
