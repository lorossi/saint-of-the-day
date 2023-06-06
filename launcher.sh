#!/bin/bash
# change to the script directory
cd "$( dirname "${BASH_SOURCE[0]}" )"
# launch the scripts in the virtual environment
venv/bin/python3 saint-handler.py &
venv/bin/python3 instagram-handler.py &
venv/bin/python3 telegram-handler.py &
