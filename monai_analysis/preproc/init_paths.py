import platform

def main():
    global DATA_HOME
    hostname = platform.node()
    if hostname == "rhinocampus":
        DATA_HOME = "/home/hemondlab/MONAI/flair"
    else:       
        DATA_HOME = "/mnt/t/Data/MONAI/flair"

if __name__ == "__main__":
    main()