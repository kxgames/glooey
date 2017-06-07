#!/usr/bin/env bash
set -euo pipefail

name=${1%.py}
script="$name.py"
image="$name.png"

chmod u+x $script
./$script &
import $image

# Close the GUI once we have the screenshot.
pkill -P $$


