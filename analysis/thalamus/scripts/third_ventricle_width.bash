mask=thirdvent_mask_RAS.nii.gz
Ny=$(c3d "$mask" -info | awk -F'[][ ,]+' '/dim =/ {print $6}')  # 2nd dim

maxw=0
best=-1
# tmp=$(mktemp --suffix=.nii.gz)

for ((k=0; k<Ny; k++)); do
  echo $k
  # extract the kth coronal slice as a 2-D image
  c3d "$mask" -slice y $k -o "$tmp"

  # 2-D label geometry -> FeretDiameter is the max caliper width in that plane (mm)
  w=$(LabelGeometryMeasures 2 "$tmp" | sed -E 's/\[([0-9.]+),[[:space:]]+([0-9.]+)\]/[\1,\2]/g' | awk 'NR>1 {print $10; exit}' | awk -F'[][,]' '{print $3}')

  # keep the maximum
  awk -v w="$w" -v mx="$maxw" 'BEGIN{ if (w>mx) print 1; else print 0 }' | read gt
  if [ "$gt" -eq 1 ]; then maxw=$w; best=$k; fi
done

echo "Max coronal-plane width: ${maxw} mm at coronal slice index ${best}"
