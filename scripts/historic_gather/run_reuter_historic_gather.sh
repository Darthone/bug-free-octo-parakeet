#!/usr/bin/env bash

# change to directory of this script
cd "$(dirname "$0")"
source ../../venv/bin/activate
python ./gather_historic_reuter.py

