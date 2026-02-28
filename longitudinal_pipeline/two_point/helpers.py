import subprocess

def fslstats(mask_file, stat_flags, index_mask=None):
        """
        Run fslstats and return results as a list of floats.
        
        Parameters
        ----------
        mask_file : str
            Path to the input image
        stat_flags : str or list
            Stats flags e.g. '-M' or ['-M', '-S']
        index_mask : str, optional
            Path to index mask file (for -K option)
        
        Returns
        -------
        list of float (single stat) or list of lists (multiple stats per label)
        """
        if isinstance(stat_flags, str):
            stat_flags = stat_flags.split()
        
        cmd = ['fslstats']
        if index_mask:
            cmd += ['-K', index_mask]
        cmd += [mask_file] + stat_flags
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        
        parsed = []
        for line in lines:
            values = [float(v) for v in line.split()]
            if len(values) == 1:
                parsed.append(values[0])
            elif len(values) == 0:
                parsed.append([None])
            else:
                parsed.append(values)
        if len(parsed) == 0:
            parsed = [None]
        return parsed
