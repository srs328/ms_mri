# To Do List

## File Management

- [ ] Inferred labels should be named in such a way that indicates which training
  they were produced from
- [ ] The new Scan class should have a function that returns all niftis in
  its root folder
- [ ] The new Scan class should have a function that returns all subdirectories
  in its root folder
- [ ] Rename all the inferred labels with something more descriptive of which training
  they were produced from (e.g. t1_pituitary_pred → t1_pituitary1_pred)
- [ ] The trainings for pituitary1 and choroid1 were via the old notebook. Convert exactly what
  was done into a command with associated datalist and dataset
- [x] Make a function and format saved datasets/datalist to be more easily usable
  across devices where the paths are different

## Logging

- [ ] See if I can capture Monai logs using `| tee`. Might need to do something extra
  to capture stderr ([look here](https://serverfault.com/questions/201061/capturing-stderr-and-stdout-to-file-using-tee))

## Code Style

- [ ] Find any instance where I use a list comprehension as a function argument
  or in constructer and change to generator expression (see [PEP 289](https://peps.python.org/pep-0289/))
