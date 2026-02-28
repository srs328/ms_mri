# Notes

## Generate Crop

`pipeline_root=/home/srs-9/Projects/ms_mri/longitudinal_pipeline/custom_pipeline`

- `ORIG_TEMPLATE`: Used to ants register template to subject
  - `ORIG_TEMPLATE=$pipeline_root/resources/origtemplate.nii.gz` used to ants register template to subject
- `MASK_93B`: A mask with dimensions of `ORIG_TEMPLATE` that encompasses the cropped box
  - `MASK_93B=$pipeline_root/resources/mask_templ_93x187x68_B.nii.gz`
- `TEMPLATE_93B`: Cropped version of `ORIG_TEMPLATE` based on `MASK_93B`
  - `TEMPLATE_93B=$pipeline_root/resources/templ_113x207x88.nii.gz`

1. Rigid register the template to subject: `ants_new_rigid_registration(ORIG_TEMPLATE, orig_input_image)`
   - Saves `rigidGeneric0Affine.txt` and `rigid.nii.gz` in top level
2. Transform template mask to subject: `ants_ApplyInvTransforms(mask, orig_input_image, mask_input)`
    - `mask` is the template mask, `mask_input` will be the input image's mask
3. Run `fslcpgeom {orig_input_image} {mask_input}` to match the sform of `mask_input` to `orig_input_image`
4. Run `bias_correction`


```bash
docker run -it --rm \
    --name sthomas \
    -v ${PWD}:/data \
    -w /data \
    --user ${UID}:$(id -g) \
    anagrammarian/sthomas \
    hipsthomas.sh -v -t1 -co -d -i t1.nii.gz
```

### Helpers

- `make_partial_command()`
- `command()`

### HIPS-THOMAS Behavior

```python
file_name = os.path.basename(orig_input_image)
base_name = file_name.replace('.gz','').replace('.nii','')

ants_new_rigid_registration(ORIG_TEMPLATE, orig_input_image)
print("Completed a quick rigid affine registration of input and full template")
mask_input = os.path.join(os.path.dirname(orig_input_image), 'mask_inp.nii.gz')
ants_ApplyInvTransforms(mask, orig_input_image, mask_input)
print("Completed transforming the mask from template space to input space")

# correction to match mask input to input image sform.
do_command(f'fslcpgeom {orig_input_image} {mask_input}')
input_image = os.path.join(os.path.dirname(orig_input_image), 'crop_'+base_name+'.nii.gz')
do_command(crop_by_mask_cmd(orig_input_image, input_image, mask_input, 1, UNCROP_PADDING))
print('Completed cropping the input. Elapsed: %s' % timedelta(seconds=time.time()-t))

#! SRS-sanitization step omitted here, skipping for now

bias_correct(input_image, input_image, **exec_options)
print('Contrast adjusting cropped image cubic stretch')
remap_image(input_image, input_image, 3, 1, "WM")
```

`ants_new_rigid_registration(ORIG_TEMPLATE, orig_input_image)` defined in `ants_tools.py`

```python
def ants_new_rigid_registration(fixed, moving, cost='MI', **exec_options):
    cmd = 'antsRegistration -d 3 --float 0 --output rigid --interpolation Linear --use-histogram-matching 0 --winsorize-image-intensities [ 0.005,0.995 ] -r [%s,%s,1] -t Rigid[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 7e-7,10] -v -f 12x8x4x2 -s 4x3x2x1vox -t Affine[0.1] --metric MI[%s,%s,1,32,Regular,0.25] --convergence [1000x500x250x100, 4e-7,10] -v -f 12x8x4x2 -s 4x3x2x1vox  ' % (fixed, moving, fixed, moving, fixed, moving)
    
    output_warp = 'rigid.nii.gz'
    output_rigid = 'rigidGeneric0Affine.txt'
    command(cmd, **exec_options)
    return output_warp, output_rigid, cmd


def ants_ApplyInvTransforms(input_image, reference, output_image, **exec_options):
    cmd = 'antsApplyTransforms -d 3 -i %s -r %s -o %s -t [rigid0GenericAffine.mat , 1]' % (input_image, reference, output_image)
    command(cmd, **exec_options)
    return output_image, cmd


def bias_correct(input_image, output_image, **exec_options):
    cmd = 'N4BiasFieldCorrection -d 3 -i %s -o %s -b [200] -s 3 -c [50x50x30x20,1e-6]' % (input_image, output_image)
    command(cmd, **exec_options)
    return output_image, cmd
```


From `parallel.py`

```python
def command(cmd, debug=False, suppress=False, verbose=False, env=None):
    if (debug or verbose):
        print('Executing: %s' % cmd)
    if suppress:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=env)
        _, stderr = p.communicate()
        if stderr:
            print(stderr)
        return p.returncode
    # sp_cmd = cmd.split(' ')
    # return subprocess.call(sp_cmd)
    return subprocess.call(cmd, shell=True, env=env)
```
