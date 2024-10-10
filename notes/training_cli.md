# Training CLI

## File System

Image naming conventions:

- All lowercase letters
- Multiple modality names separated by '.'

Label naming convention

- Multiple labels separated by '.'
- Initials capitalized and separated from label name with '-'

## preprocess

In DataSetProcessor, don't know which factory function to go with. If I go with
the long one, will need to think about what happens to a fully specified object
if the prepare functions are called
