from mri_data import data_file_manager as dfm

dataroot = "/home/srs-9/Projects/ms_mri/data/3Tpioneer_bids"


def initialize_dataset():
    return dfm.scan_3Tpioneer_bids(dataroot)


def get_scan(image=None, label=None):
    subid = 1010
    sesid = 20180208
    scan = dfm.Scan.new_scan(dataroot, subid, sesid)
    if image is not None:
        scan.set_image(image)
    if label is not None:
        scan.set_label(label)
    return scan


"""
import checking
scan = checking.get_scan()
"""
