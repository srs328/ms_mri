import data_file_manager as datafm
from pathlib import Path
from pprint import pp
import copy
import platform




base_path = Path("/mnt/f/Data/ms_mri/lesjak_2017")
data_dir = base_path / "data"

lesjak_datafm = datafm.LesjakData(data_dir)
subjects = lesjak_datafm.subjects["name"]
pp(subjects)


subjects_copy = copy.copy(subjects)
labels = datafm.assign_train_test(subjects, 0.2)
pp(labels)

