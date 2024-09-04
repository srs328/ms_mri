import nibabel as nib
import numpy as np

def dice_score(seg1, seg2):
    intersection = np.sum((seg1 > 0) & (seg2 > 0))
    volume_sum = np.sum(seg1 > 0) + np.sum(seg2 > 0)
    if volume_sum == 0:
        return 1.0
    return 2.0 * intersection / volume_sum

# # Load your MRI segmentations
# seg1 = nib.load('path_to_segmentation1.nii').get_fdata()
# seg2 = nib.load('path_to_segmentation2.nii').get_fdata()

# # Calculate Dice score
# score = dice_score(seg1, seg2)
# print(f'Dice Score: {score}')