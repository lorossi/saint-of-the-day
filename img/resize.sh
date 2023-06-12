#!/bin/bash

# resize all the images that don't start with "resized" in the current directory
for i in $(ls | grep -E '^[^A-Za-z\-]+.*.png$')
do
    echo "resizing $i"
    convert -geometry x400 $i resized-$i
done

echo "done"