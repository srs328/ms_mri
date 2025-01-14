#!/bin/bash


root="/media/smbshare" # edit this to be smbshare root
default_app=fsleyes


# -------------------------------------

usage() {
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

subid=${script_args[0]}

if [ -z $subid ]; then
    echo "Error: no subject id"
    exit 1
fi

if [ -z $app ]; then
    app=$default_app
fi
echo "Using $app" 


dataroot="$root/3Tpioneer_bids"
inf_root="$root/3Tpioneer_bids_predictions"

if [ ! -d $dataroot ]; then
    echo "$dataroot does not exist, check script"
    exit 1
fi

inf_filename=flair.t1_choroid_pineal_pituitary3_pred.nii.gz

subj_dir="sub-ms${subid}"

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
    diff=$(( ($(date -d "$ses" +%s) - $(date -d "$first_ses" +%s)) ))
    if [[ $diff < 0 ]]; then
        first_ses=ses
    fi
done

ses_dir="ses-$first_ses"

scan_path="$dataroot/$subj_dir/$ses_dir"
inf_path="$inf_root/$subj_dir/$ses_dir"

if [ ! -f "$inf_path/$inf_filename" ]; then  
    echo "$inf_path/$inf_filename does not exist"
    echo "The subject you entered may not have an inference"
    exit 1
fi

if [ $app == "itksnap" ]; then
    itksnap -g "$scan_path/flair.nii.gz" -o "$scan_path/t1.nii.gz" -s "$inf_path/$inf_filename"
elif [ $app == "fsleyes" ]; then
    fsleyes "$scan_path/t1.nii.gz" "$scan_path/flair.nii.gz" "$inf_path/$inf_filename" -ot label -l freesurfercolorlut
fi
