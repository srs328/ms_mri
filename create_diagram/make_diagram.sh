#!/bin/bash

# Usage: ./make_diagram.sh path/to/color_assignment.csv [output_path]
# if output_path is not specified, the diagram is saved as "thalamus_diagram.png"

if [ $# -ne 1 ]; then
    echo "Usage: $0 path/to/color_assignment.csv"
    exit 1
fi

if [ $# -lt 2 ]; then
    save_path=thalamus_diagram.png
else
    save_path=$2
fi

docker run --rm \
    -v "$(pwd)":/app \
    diagram-maker "$1" "$save_path"