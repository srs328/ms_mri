param(
    [string]$subid
)

$root = "H:/"
$dataroot = "$root/3Tpioneer_bids"
$inf_root = "$root/srs-9/3Tpioneer_bids_predictions"

if (!(Test-Path -Path $dataroot)) {
    Write-Output "$dataroot doesn't exist, check script"
}

$subj_dir = "sub-ms${subid}"

$sessions = @()
Get-ChildItem "$dataroot/$subj_dir" | ForEach-Object {
     $_.Name -match "ses-(\d{8})" | Out-Null
     $sessions += $Matches[1]
}

$first_ses = $sessions[0]
ForEach ($ses in $sessions) {
    if ((Get-Date ([int]$ses)) -lt (Get-Date ([int]$first_ses))) {
        $first_ses = $ses
    }
}

$ses_dir = "ses-$first_ses"

$scan_path = "$dataroot/$subj_dir/$ses_dir"
$inf_path = "$inf_root/$subj_dir/$ses_dir"

$flair_t1_inf_filename = "flair.t1_choroid_pineal_pituitary3_pred.nii.gz"
$t1_inf_filename = "t1_choroid_pineal_pituitary_T1-1_pred.nii.gz"
$flair_inf_filename = "flair_choroid_pineal_pituitary_FLAIR-1_pred.nii.gz"

$flair_scan = "$scan_path/flair.nii.gz"
$t1_scan = "$scan_path/t1.nii.gz"

$flair_t1_inference = "$inf_path/$flair_t1_inf_filename"
$t1_inference = "$inf_path/$t1_inf_filename"
$flair_inference = "$inf_path/$flair_inf_filename"

$notexist_count = 0
if (!(Test-Path $flair_t1_inference)) {
    Write-Warning "Inference on flair.t1 does not exist"
    Write-Warning "$t1_inference does not exist"
    $notexist_count += 1
}

if (!(Test-Path $t1_inference)) {
    Write-Warning "Inference on flair.t1 does not exist"
    Write-Warning "$t1_inference does not exist"
    $notexist_count += 1
}

if (!(Test-Path $flair_inference)) {
    Write-Warning "Inference on flair.t1 does not exist"
    Write-Warning "$t1_inference does not exist"
    $notexist_count += 1
}

if ($notexist_count -eq 3) {
    throw "No inferences exist"
}

itksnap -g "$flair_scan" -o "$t1_scan" -s "$t1_inference" "flair_inference" "$flair_t1_inference" 