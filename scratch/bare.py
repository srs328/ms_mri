from subprocess import run

itksnap = "'/mnt/c/Program Files/ITK-SNAP 4.2/bin/ITK-SNAP.exe'"
cmd = "-g H:/3Tpioneer_bids/sub-ms1071/ses-20161201/flair.nii.gz -o H:/3Tpioneer_bids/sub-ms1071/ses-20161201/t1.nii.gz -s H:/3Tpioneer_bids_predictions/sub-ms1071/ses-20161201/choroid_resegment1.pineal1.pituitary1.nii.gz"

cmd_parts = [itksnap] + cmd.split(" ")
print(cmd_parts)

# run(cmd_parts, shell=True)
run(["/bin/bash", "-c", itksnap + " " + cmd])
