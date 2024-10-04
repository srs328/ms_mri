import errno
import os
import subprocess

def merge_images(image_paths, merged_path, return_on_error=False):
    
    image_paths = [str(p) for p in image_paths]
    for p in image_paths:
        if not os.path.isfile(p):
            if return_on_error:
                return None
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)
            
    cmd_parts = ["fslmerge", "-a", str(merged_path), " ".join(image_paths)]
    
    print(" ".join(cmd_parts))
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def merge_labels(label_paths, merged_path, return_on_error=False):
    label_paths = [str(p) for p in label_paths]
    for p in label_paths:
        if not os.path.isfile(p):
            if return_on_error:
                return None
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p)
    
    label_inputs = [label_paths[0]]
    for path in label_paths[1:]:
        label_inputs.extend(["-add", path])
    cmd_parts = ["fslmaths", *label_inputs, merged_path]
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
    return merged_path


def set_label_value(image_path, output_path, val):
    cmd_parts = ["fslmaths", str(image_path), "-bin", "-mul", val, str(output_path)]
    subprocess.run(cmd_parts, check=True, stderr=True, stdout=True)
    return output_path