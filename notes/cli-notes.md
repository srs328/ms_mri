# CLI Notes

## Refactor Scan

### file_manager.py

- find_label()

Is this wonky?

```python
def asdict(self):
    dict_form = {k: getattr(self, k) for k in self._field_names()}
    for k, v in dict_form.items():
        if isinstance(v, Path):
            dict_form[k] = str(v)
    dict_form["root"] = dict_form.popitem("_root")
    return dict_form
```

Add a function to make it easy to see all the predictions that have been produced

Figure out how to deal with git and logs. I want some logs to be ignored and some
not. e.g. new_files.log is very large should should be ignored

### utils.py

Just `info` and `root`

Refactor `DataSetProcessor` and `scan_3Tpioneer_bids` because they could be better

- Filter functions should take just a scan and return `True` or `False`
- Maybe `scan_3Tpioneer_bids` should be where filtering occurs?
  - If not, then filter functions should be defined in `preprocess.py`

## Training CLI

### File System

Image naming conventions:

- All lowercase letters
- Multiple modality names separated by '.'

Label naming convention

- Multiple labels separated by '.'
- Initials capitalized and separated from label name with '-'

### preprocess

In DataSetProcessor, don't know which factory function to go with. If I go with
the long one, will need to think about what happens to a fully specified object
if the prepare functions are called
