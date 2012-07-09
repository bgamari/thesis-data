#!/bin/bash

rsync -a --progress ~lab/data/peker/Droplet_Stuff/ droplet-stuff
git add `find -iname README`

