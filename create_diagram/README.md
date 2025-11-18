# README

To use this, you need to create a `csv` file with your color assignments. Look at `sample_color_assignments.csv` to see the format.

To build the doccker image, navigate to this directory in your terminal and run:

`docker build -t diagram-maker .`

To run in Windows command prompt:

`docker run --rm -v "%cd%:/app" diagram-maker sample_color_assignments.csv`

To run in Windows Powershell

`docker run --rm -v "${PWD}:/app" diagram-maker sample_color_assignments.csv`

To run on macOS/Linux:

`docker run --rm -v "$(pwd):/app" diagram-maker sample_color_assignments.csv`
