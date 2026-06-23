#!/bin/bash

# Initialize changelog with header
CHANGELOG=""

# The end ref ($2) may be a version tag that does not exist yet (e.g. while
# preparing a release, before the tag is created in the publish phase). Fall
# back to HEAD so the range covers everything up to the current commit.
end="$2"
if ! git rev-parse --verify --quiet "${end}^{commit}" >/dev/null; then
    end="HEAD"
fi

# Get commits with PR numbers and append them to changelog
while IFS= read -r line; do
    CHANGELOG="${CHANGELOG}\n${line}"
done < <(git log --pretty=format:"* %s" "$1..$end" | grep -E ".*\(#[0-9]+\).*$")

# Output in GitHub Actions format
echo -e "$CHANGELOG"
