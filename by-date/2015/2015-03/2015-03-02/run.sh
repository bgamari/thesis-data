#!/bin/bash

irf=004

# Citrate: run005 is funny
cit_corrs="006 007 008 009 010 011"
cir_corrs="$cit_corrs 022 023 024 025 026 027 028"
# Phosphate
phos_corrs="012 013 014 015 016"
phos_corrs="$phos_corrs 017 018 019 020 021"


function run() {
    files="--irf=run${irf}.pt3.ch1.txt --irf=run${irf}.pt3.ch2.txt"
    for c in $corrs; do
            files="$files run${c}.pt3.ch1.txt run${c}.pt3.ch2.txt"
    done
    args="-p2 -c2 -g1.14"
    python ~/lori/analysis/photon-tools/anisotropy $args $files -o $out.png -J $out.json >| $out.txt
}

corrs="$cit_corrs" out=fit-cit run
corrs="$phos_corrs" out=fit-phos run
corrs="$cit_corrs $phos_corrs" out=fit run
