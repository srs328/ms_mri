#!/bin/bash


root="/media/smbshare" # edit this to be smbshare root
default_app=itksnap


# -------------------------------------

usage() {
    echo "Opens the manual pineal segmentation (either pineal-SRS_T1 or pineal-SRS)"
    echo "Usage: [-a] [-h] <subid>"
    echo "  -a          Which app to use (default: $default_app)"
    echo "                  options: fsleyes, itksnap"
    echo "  -h          Display this help message."
    echo "  <subid>     Subject ID to open (just four digits)"
    exit 0
}

# parse arguments
script_args=()
while [ $OPTIND -le "$#" ]
do
    if getopts :a:h opt
    then
        case $opt in
            a)
                app=$OPTARG
                ;;
            h)
                usage ;;
        esac
    else
        script_args+=("${!OPTIND}")
        ((OPTIND++))
    fi
done

dataroot="$root/3Tpioneer_bids"
if [ ! -d $dataroot ]; then
    printf "Can't find %s \nedit 'root' at top of script\n" $dataroot
    exit 1
fi

subid=${script_args[0]}

if [ -z "$subid" ]; then
    echo "Error: no subject id"
    exit 1
fi

if [ -z "$app" ]; then
    app=$default_app
fi
echo "Using $app" 


# get the subject+session root (scan_path)
subj_dir="sub-ms${subid}"

# find the first session
ses_dirs=$(ls "$dataroot/$subj_dir")

ses=()
for ses_dir in "${ses_dirs[@]}"
do
    if [[ "${ses_dir}" =~ ^ses-([0-9]{8}) ]]; then 
        sessions+=("${BASH_REMATCH[1]}")
    fi
done

first_ses=${sessions[0]}

for ses in "${sessions[@]:1}"
do
    diff=$(( $(date -d "$ses" +%s) - $(date -d "$first_ses" +%s) ))
    if [[ $diff -lt 0 ]]; then
        first_ses=ses
    fi
done

ses_dir="ses-$first_ses"
scan_path="$dataroot/$subj_dir/$ses_dir"

label_name="pineal-SRS_T1.nii.gz"
if [ -f "$scan_path/$label_name" ]; then
    label="$scan_path/$label_name"
else
    label="$scan_path/pineal-SRS.nii.gz"
fi
if [ ! -f "$label" ]; then
    echo "Subject $subid does not have a pineal label"
    exit 1
fi
echo "Found $(basename "$label")"

t1="$scan_path/t1.nii.gz"
flair="$scan_path/flair.nii.gz"
t1_gd="$scan_path/t1_gd.nii.gz"

scans=()
for scan in $t1 $flair $t1_gd
do
    if [ -f "$scan" ]; then
        scans+=("$scan")
    fi
done

scans_to_show=$(basename "${scans[0]}")
for scan in "${scans[@]:1}"
do
    scans_to_show+=", $(basename "$scan")"
done
echo "Found ${scans_to_show[*]}"

if [ "$app" == "itksnap" ]; then
    itksnap -g "${scans[0]}" -o "${scans[@]:1}" -s "$label"
elif [ "$app" == "fsleyes" ]; then
    fsleyes "${scans[@]}" \
        "$label" -ot label -l freesurfercolorlut
fi
