# Notes

Tried running it but got error

- Command: `sudo docker run -v /home/hemondlab/Dev/ms_mri/chp_seg/ins/:/data/in -v /home/hemondlab/Dev/ms_mri/chp_seg/outs/:/data/out kilianhett/chp_seg:1.0.0 --sequence_type flair --name_pattern sub-ms*`
- Error:

```
Number of data to process = 1
['sub-ms1019-ses-20190608.nii.gz']
sub-ms1019-ses-20190608
Running computation on cpu
Traceback (most recent call last):
  File "./serialize_process", line 40, in <module>
    run_segmentation.execute(path_in=path_i, path_out=path_out, path_mdl=os.path.join('module_ai/mdl/'), overwrite=overwrite, seq_type=seq_type)
  File "/app/run_segmentation.py", line 47, in execute
    run_inference.run(path_img=t2mni, anat_prior='Data/cp_skeleton.nii', path_mdl=mdl, path_out=folder)
  File "/app/module_ai/run_inference.py", line 44, in run
    net.load_state_dict(torch.load(os.path.join(path_mdl,'patch_mdl.pth'), map_location=device))
  File "/usr/local/lib/python3.6/dist-packages/torch/serialization.py", line 594, in load
    with _open_file_like(f, 'rb') as opened_file:
  File "/usr/local/lib/python3.6/dist-packages/torch/serialization.py", line 230, in _open_file_like
    return _open_file(name_or_buffer, mode)
  File "/usr/local/lib/python3.6/dist-packages/torch/serialization.py", line 211, in __init__
    super(_open_file, self).__init__(open(name, mode))
FileNotFoundError: [Errno 2] No such file or directory: 'module_ai/mdl/flair/patch_mdl.pth'
```