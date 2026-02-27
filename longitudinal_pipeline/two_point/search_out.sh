#!/bin/bash

# Usage: ./search_out.sh <directory> <job_id> <search_term>

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <directory> <job_id> <search_term>"
    echo "Example: $0 /path/to/logs 12345 TERM_RUNLIMIT"
    exit 1
fi

DIR="$1"
JOB_ID="$2"
SEARCH_TERM="$3"

if [ ! -d "$DIR" ]; then
    echo "Error: Directory '$DIR' does not exist."
    exit 1
fi

# Find matching .out files for the given job ID
FILES=$(find "$DIR" -maxdepth 1 -name "${JOB_ID}*.out" | sort)

if [ -z "$FILES" ]; then
    echo "No .out files found for job ID '$JOB_ID' in '$DIR'"
    exit 1
fi

echo "Searching for '$SEARCH_TERM' in .out files for job '$JOB_ID'..."
echo "------------------------------------------------------------"

MATCH_COUNT=0
FILE_COUNT=0

for FILE in $FILES; do
    FILE_COUNT=$((FILE_COUNT + 1))
    if grep -q "$SEARCH_TERM" "$FILE"; then
        MATCH_COUNT=$((MATCH_COUNT + 1))
        BASENAME=$(basename "$FILE")
        # Try to extract the sub-job index from the filename
        SUBJOB=$(echo "$BASENAME" | grep -oP '(?<='"$JOB_ID"')[._-]?\K[0-9]+' || echo "?")
        echo "  [MATCH] $BASENAME (sub-job index: $SUBJOB)"
        # Optionally show the matching lines
        grep --color=never -n "$SEARCH_TERM" "$FILE" | sed 's/^/    /'
    fi
done

echo "------------------------------------------------------------"
echo "Matched: $MATCH_COUNT / $FILE_COUNT files"