#!/bin/bash -e

# ```
# Report git cached and modified files.
# ```

exec "(git diff --cached --name-only; git ls-files -m) | sort | uniq | perl -ne 'print if /\S/'"
#git status --porcelain 2>&1 | grep -v "?" | cut -f 3 -d ' '
