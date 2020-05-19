#!bin/bash
# The source file exports the path of directory containing python scripts.
# 

# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
# The line below was also referred in GipsyX software.
GCTSdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# export GCTS_1.0 path
export pyGCTS=$GCTSdir
export PATH=$pyGCTS/bin:$PATH



