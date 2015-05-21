#!/bin/bash

for i in $(find .. -mindepth 3 -maxdepth 3 -type d); do
        ln -s $i $(basename $i)
        git add $(basename $i)
done
