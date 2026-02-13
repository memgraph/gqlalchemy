#!/bin/bash

# Initialize changelog with header
CHANGELOG=""

# Get commits with PR numbers and append them to changelog
while IFS= read -r line; do
    CHANGELOG="${CHANGELOG}\n${line}"
done < <(git log --pretty=format:"* %s" "$1..$2" | grep -E ".*\(#[0-9]+\).*$")

# Output in GitHub Actions format
echo -e "$CHANGELOG"
