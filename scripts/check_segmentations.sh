#!/bin/bash


root="/mnt/h" # edit this to be smbshare root
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

if [ -z "$subid" ]; then
    echo "Error: no subject id"
    exit 1
fi

if [ -z "$app" ]; then
    app=$default_app
fi
echo "Using $app" 


dataroot="$root/3Tpioneer_bids"
inf_root="$root/srs-9/3Tpioneer_bids_predictions"
# inf_root="$root/srs-9/analysis/choroid_pineal_pituitary-crosstrain"

if [ ! -d $dataroot ]; then
    echo "$dataroot does not exist, check script"
    exit 1
fi

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
    diff=$(( $(date -d "$ses" +%s) - $(date -d "$first_ses" +%s) ))
    if [[ $diff -lt 0 ]]; then
        first_ses=ses
    fi
done

ses_dir="ses-$first_ses"

scan_path="$dataroot/$subj_dir/$ses_dir"
inf_path="$inf_root/$subj_dir/$ses_dir"

flair_t1_inf_filename=flair.t1_choroid_pineal_pituitary3_pred.nii.gz
t1_inf_filename=t1_choroid_pineal_pituitary_T1-1_pred.nii.gz
flair_inf_filename=flair_choroid_pineal_pituitary_FLAIR-1_pred.nii.gz

flair_scan="$scan_path/flair.nii.gz"
t1_scan="$scan_path/t1.nii.gz"

flair_t1_inference="$inf_path/$flair_t1_inf_filename"
t1_inference="$inf_path/$t1_inf_filename"
flair_inference="$inf_path/$flair_inf_filename"

if [ ! -f "$flair_t1_inference" ]; then  
    echo "Inference on flair.t1 does not exist"
    echo "$flair_t1_inference not found"
    echo "The subject you entered may not have an inference"
    exit 1
fi

if [ ! -f "$t1_inference" ]; then  
    echo "Inference on t1 does not exist"
    echo "$t1_inference not found"
    echo "The subject you entered may not have an inference done on the t1 alone"
fi

if [ "$app" == "itksnap" ]; then
    itksnap -g "$flair_scan" -o "$t1_scan" -s "$t1_inference" "$flair_t1_inference"
elif [ "$app" == "fsleyes" ]; then
    fsleyes "$flair_scan" "$t1_scan" \
        "$t1_inference" -ot label -l freesurfercolorlut \
        "$flair_inference" -ot label -l freesurfercolorlut
fi
