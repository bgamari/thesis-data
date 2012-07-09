#!/bin/bash

rsync -a --progress ~lab/data/peker/Droplet_Stuff/ droplet-stuff
git add `find -iname README`
git commit -m "peker: Add READMEs"
git annex add .
git commit -m "peker: Add other files"

