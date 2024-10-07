# import preprocess
# import train
# import data_file_manager as dfm
# from train import cli
import json

# data = "/home/srs-9/Projects/ms_mri/tests/data"

# dataset, info = cli.prepare_dataset(data, ("flair", "t1"), "pituitary")

# cli.save_dataset(dataset, "test.json", info)

pituitary_file = "/home/srs-9/Projects/ms_mri/notes/tmp_pituitary.txt"
choroid_file = "/home/srs-9/Projects/ms_mri/notes/tmp_choroid.txt"

pituitary = set()
choroid = set()
with open(pituitary_file, "r") as f:
    for line in f.readlines():
        pituitary.add(line.strip())
with open(choroid_file, "r") as f:
    for line in f.readlines():
        choroid.add(line.strip())

diff = choroid - pituitary
print(len(diff))
print(diff)
