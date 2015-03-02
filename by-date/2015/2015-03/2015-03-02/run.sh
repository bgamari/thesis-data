#!/bin/bash

irf=004

corrs="005 006 007 008 009 010 011" # Citrate
corrs="$corrs 012 013 014 015 016" # Phosphate

files="--irf=run${irf}.pt3.ch1.txt --irf=run${irf}.pt3.ch2.txt"
for c in $corrs; do
        files="$files run${c}.pt3.ch1.txt run${c}.pt3.ch2.txt"
done

python ~/lori/analysis/photon-tools/anisotropy $files -p2 -c2 -o fits.png >| fits.txt
