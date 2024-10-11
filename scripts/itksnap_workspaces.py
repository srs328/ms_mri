import os
from subprocess import run
import sys
from pathlib import Path

from mri_data.file_manager import parse_image_name, nifti_name
from monai_training.preprocess import load_dataset


# test that this would work with single label/image datasets
def create_workspace(scan, workspace_root, dataset_name):
    image_names = parse_image_name(scan.image)
    root = Path(scan.root)
    image_paths = [(root / name).with_suffix(".nii.gz") for name in image_names]

    main_image = "-layers-set-main {} -tags-add {}-MRI".format(
        image_paths[0], image_names[0].upper()
    )
    extra_images = [
        "-layers-add-anat {} -tags-add {}-MRI".format(path, name.upper())
        for path, name in zip(image_paths[1:], image_names[1:])
    ]
    seg = "-layers-add-seg {} -tags-add {}".format(
        scan.label_path, nifti_name(scan.label)
    )
    save_path = os.path.join(workspace_root, dataset_name)
    save = f"-o {save_path}"

    command_parts = ["itksnap-wt", main_image, extra_images, seg, save]
    command = " ".join(command_parts)
    print(command)
    # run(command)


if __name__ == "__main__":
    args = sys.argv[1:]
    dataset_file = args[0]
    workspace_root = args[1]
    dataset_name = args[2]

    dataset, _ = load_dataset(dataset_file)
    for scan in dataset:
        create_workspace(scan, workspace_root, dataset_name)
