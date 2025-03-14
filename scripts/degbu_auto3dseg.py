from pathlib import Path
import sys


base_dir = Path(
    "/home/srs-9/Projects/ms_mri/training_work_dirs/choroid_pineal_pituitary_T1-1/swinunetr_0"
)
sys.path.insert(0, str(base_dir / "scripts"))

from train import run

config_dir = base_dir / "configs"
configs = [
    config_dir / 'hyper_parameters.yaml',
    config_dir / 'network.yaml',
    config_dir / 'transforms_train.yaml',
    config_dir / 'transforms_validate.yaml',
    config_dir / 'transforms_infer.yaml'
]

configs = [str(conf) for conf in configs]

run(configs)

# python -m scripts.train run --config_file "['configs/hyper_parameters.yaml','configs/network.yaml','configs/transforms_train.yaml','configs/transforms_validate.yaml']"