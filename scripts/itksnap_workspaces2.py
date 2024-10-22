from loguru import logger
import os
from subprocess import run
import sys
from pathlib import Path

from mri_data.file_manager import parse_image_name, nifti_name
from monai_training.preprocess import load_dataset


def convert_to_winroot(path: Path):
    return Path("H:/") / path.relative_to("/mnt/h")


# test that this would work with single label/image datasets
def create_workspace(scan, save_dir):
    label_path = convert_to_winroot(scan.label_path)
    image_names = parse_image_name(scan.image)
    root = Path(scan.root)
    image_paths = [(root / name).with_suffix(".nii.gz") for name in image_names]
    image_paths = [convert_to_winroot(p) for p in image_paths]

    main_image = "-layers-set-main {} -tags-add {}-MRI".format(
        image_paths[0], image_names[0].upper()
    )
    extra_images = " ".join(
        [
            "-layers-add-anat {} -tags-add {}-MRI".format(path, name.upper())
            for path, name in zip(image_paths[1:], image_names[1:])
        ]
    )
    seg = "-layers-add-seg {} -tags-add {}".format(label_path, nifti_name(scan.label))

    save_path = os.path.join(save_dir, f"sub-ms{scan.subid}-ses-{scan.sesid}.itksnap")
    save = f"-o {save_path}"

    command_parts = ["itksnap-wt.exe", main_image, extra_images, seg, save]
    command = " ".join(command_parts)
    run(command)
    return command


if __name__ == "__main__":
    args = sys.argv[1:]
    dataroot = args[0]
    inference_root = args[1]
    workspace_root = args[3]
    dataset_name = args[4]

    save_dir = os.path.join(workspace_root, dataset_name)
    if not os.path.exists(save_dir):
        logger.info()
        os.makedirs(save_dir)

    commands = []
    for scan in dataset:
        commands.append(create_workspace(scan, workspace_root, dataset_name) + "\n")

    current_dir = Path(__file__).absolute().parent
    with open(current_dir / "create-workspaces2.sh", "w") as f:
        f.writelines(commands)

"""
python scripts/itksnap_workspaces.py "/mnt/h/training_work_dirs/choroid_pineal_pituitary2/dataset.json" "/home/srs-9/Projects/ms_mri/itksnap_workspaces" "choroid_pineal_pituitary2"
"""
