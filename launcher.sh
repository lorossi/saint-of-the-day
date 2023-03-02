#!/bin/bash
cd /home/pi/scripts/saint-of-the-day
venv/bin/python3 instagram-handler.py &
venv/bin/python3 telegram-handler.py &