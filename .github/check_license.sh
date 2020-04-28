#!/bin/bash

echo
echo "==========================="
echo "Check SPDX identifier"
echo "==========================="
echo

ERROR_FILES=""
FILES_TO_CHECK=`find . \
    -size +0 -type f \( -name '*.sh' -o -name '*.py' -o -name 'Makefile' \) \
    \( -not -path "*/.*/*" -not -path "*/third_party/*" \)`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    grep -q "SPDX-License-Identifier" $file || ERROR_FILES="$ERROR_FILES $file"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    return 1
fi
