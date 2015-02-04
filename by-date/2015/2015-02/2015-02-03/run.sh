#!/bin/bash

irf=000

corrs="001 002 003 004 005" # Oregon Green 488
corrs="006 007 008 009 010" # BCECF

files="--irf=run${irf}.pt3.ch1.txt --irf=run${irf}.pt3.ch2.txt"
for c in $corrs; do
        files="$files run${c}.pt3.ch1.txt run${c}.pt3.ch2.txt"
done

python ~/lori/analysis/photon-tools/anisotropy $files -p2 -c2 -o fits.png >| fits.txt

