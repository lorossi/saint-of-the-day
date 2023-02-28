#!/bin/bash
cd /home/pi/scripts/saint-of-the-day
venv/bin/python3 instagram-poster.py &
venv/bin/python3 saint-of-the-day.py &