import subprocess
import time

work_dir = "/mnt/h/srs-9/longitudinal/sub1225"
subid = "1225"
script = "/home/srs-9/Projects/ms_mri/choroid_thalamus_project/scripts/antsRegister.sh"

cmd = ["bash", script, subid, work_dir]

start = time.time()
subprocess.run(cmd)

print(time.time() - start)