import platform

def main():
    global DATA_HOME
    hostname = platform.node()
    if hostname == "rhinocampus":
        DATA_HOME = "/home/hemondlab/MONAI/flair"
    else:       
        DATA_HOME = "/mnt/t/Data/3Tpioneer_bids"

if __name__ == "__main__":
    main()