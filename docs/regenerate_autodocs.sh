#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

rm -rf api
sphinx-autogen -s txt -t .templates api.txt
make
