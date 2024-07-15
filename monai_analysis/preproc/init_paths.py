import platform

def main():
    hostname = platform.node()
    if hostname == "rhinocampus":
        global DATA_HOME
        DATA_HOME = "/home/hemondlab/MONAI/flair"

if __name__ == "__main__":
    main()