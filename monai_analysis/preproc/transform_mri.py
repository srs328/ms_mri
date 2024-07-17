from __future__ import annotations
import nibabel as nib
import numpy as np
from pathlib import Path

def load_scan(scan_path: Path) -> np.ndarray:
    img = nib.load(scan_path)
    return np.array(img.dataobj)

def change_shape(image: np.ndarray, target: np.ndarray) -> np.ndarray:
    pass