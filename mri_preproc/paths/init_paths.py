import platform

def main():
    global DATA_HOME
    hostname = platform.node()
    if hostname == "rhinocampus":
        DATA_HOME = "/home/hemondlab/MONAI/flair"
    elif hostname == "srs-9-ThinkPad-X1":
        DATA_HOME = "/media/srs-9/WD_BLACK_5TB/Data/3Tpioneer_bids"
    else:       
        DATA_HOME = "/mnt/t/Data/3Tpioneer_bids"

if __name__ == "__main__":
    main()