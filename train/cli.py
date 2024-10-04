from pathlib import Path

import data_file_manager as dfm
import preprocess
import train

# later make the label use a glob in case there are initials after label name
def main(dataroot, modality, label, config=None):
    if len(modality) > 1:
        modality.sort()
        image_name = "_".join(modality) + ".nii.gz"
    else: 
        image_name = f"{modality}.nii.gz"
    if len(label) > 1:
        label.sort()
        label_name = "_".join(label) + ".nii.gz"
    else:
        label_name = f"{label}.nii.gz"
        
    dataset = dfm.scan_3Tpioneer_bids(dataroot, modality, label)
    for scan in dataset:
        if scan.image is None:
            base_images = [scan.root / f"{mod}.nii.gz" for mod in modality]
            merged_image = scan.root / image_name


if merged_path is None:
    image_names = [p.stem for p in image_paths]
    image_names.sort()
    merged_name = "_".join(image_names) + image_names[0].ext
    merged_path = image_paths[0].parent / merged_name
    
if merged_path is None:
    label_names = [p.stem for p in label_paths]
    label_names.sort()
    merged_name = "_".join(label_names) + label_names[0].ext
    merged_path = label_paths[0].parent / merged_name
    
    
# remember to add function that fixes the label values 