import nibabel as nibabel
import random
from data_file_manager import DataSet
from dataclasses import dataclass


# test_fract, n_folds, max_epochs, work_dir, label names

@dataclass
class Config:
    work_dir: str
    test_fract: float = 0.2
    n_folds: int = 5
    max_epochs: int = 100
    info: dict = dict()


def train(dataset: DataSet, config: Config):
    dataset = assign_conditions(dataset, config.test_fract)
    train_data = []
    test_data = []
    for scan in dataset:
        if scan.cond == 'tr' and scan.has_label():
            train_data.append({"image": str(scan.image), "label": str(scan.label)})
        elif scan.cond == 'ts' and scan.has_label():
            test_data.append({"image": str(scan.image), "label": str(scan.label)})

    print(f"Train num total: {len(train_data)}")
    print(f"Test num: {len(test_data)}")
    
    datalist = {
        "work_dir": config.work_dir,
        "dataroot": dataset.dataroot,
        "testing": test_data,
        "training": [{"fold": i % config.n_folds, "image": c["image"], "label": c["label"]} for i,c in enumerate(train_data)]
    }
    datalist.update(config.info)
    
    
    
def assign_conditions(dataset: DataSet, fraction_ts) -> DataSet:
    scans_no_label = []
    for i, scan in enumerate(dataset):
        if not scan.has_label():
            scans_no_label.append(i)

    n_scans = len(dataset)
    n_ts = int(fraction_ts * n_scans)
    inds = [i for i in range(n_scans)]
    random.shuffle(inds)

    for i in scans_no_label:
        inds.remove(i)
        inds.insert(0, i)

    for i in inds[:n_ts]:
        dataset[i].cond = "ts"
    for i in inds[n_ts:]:
        dataset[i].cond = "tr"

    return dataset