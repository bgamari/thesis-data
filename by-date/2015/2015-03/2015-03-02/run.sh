#!/bin/bash

irf=004

# run005 is funny
corrs="           006 007 008 009 010 011" # Citrate
corrs="$corrs 012 013 014 015 016"         # Phosphate
corrs="$corrs 017 018 019 020 021"         # Phosphate
corrs="$corrs 022 023 024 025 026 027 028" # Citrate

files="--irf=run${irf}.pt3.ch1.txt --irf=run${irf}.pt3.ch2.txt"
for c in $corrs; do
        files="$files run${c}.pt3.ch1.txt run${c}.pt3.ch2.txt"
done

python ~/lori/analysis/photon-tools/anisotropy $files -p2 -c2 -o fits.png >| fits.txt
