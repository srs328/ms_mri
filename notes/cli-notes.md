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

Figure out how to deal with git and logs. I want some logs to be ignored and some
not. e.g. new_files.log is very large should should be ignored

### utils.py

Just `info` and `root`
