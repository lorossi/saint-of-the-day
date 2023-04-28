#!/bin/bash

# Colors
green_bold="\033[1;32m"
red_bold="\033[1;31m"
reset="\033[0m"


# Loop through all the python files in the current directory
for file in *.py
do
    # Get the PID of the process
    pid=$(pgrep -f $file)
    if [ ! -z $pid ]
    then
        # Kill the process
        echo -e "$green_bold $file has PID: $pid. Killing it... $reset"
        kill $pid
    else
        # If the process is not running, print a message
        echo -e "$red_bold $file is not running. $reset"
    fi
done


