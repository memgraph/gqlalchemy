#!/bin/bash

# Get the new changes from get_changelog.sh
changelog=$(./scripts/get_changelog.sh "$1" "$2")

# Get today's date in the format Month DD, YYYY
today=$(date "+%B %d, %Y")

# Create the new section with version and date
new_section="## v$3 - ${today}\n\n### Features and improvements\n\n${changelog}\n"

# Create a temporary file
temp_file=$(mktemp)

# Read the first line (# Changelog) and write it to temp file
head -n 1 docs/changelog.md > "$temp_file"

# Add a blank line after the header
echo "" >> "$temp_file"

# Add the new section
echo -e "$new_section" >> "$temp_file"

# Add the rest of the original file (skipping the first line)
tail -n +2 docs/changelog.md >> "$temp_file"

# Replace the original file with the new content
mv "$temp_file" docs/changelog.md
