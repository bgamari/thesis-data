#!/usr/bin/python

import os
import json
import numpy as np
from photon_tools.bin_photons import bin_photons
from photon_tools.io import read_photons

import matplotlib.pyplot as pl

def find_runs(xs):
        runs = np.nonzero(np.diff(xs))[0] + 1
        if xs[0]:
                runs = np.append(0, runs)
        if xs[-1]:
                runs = np.append(runs, len(xs))
        return runs.reshape(-1, 2) - [0,1]

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='+', help='Timestamp files')
parser.add_argument('-w', '--bin-width', type=float, default=1,
                    help='Bin width in seconds')
parser.add_argument('-b', '--buffer', type=float, default=0.05,
                    help='Amount of time around burst to drop')
parser.add_argument('-t', '--threshold', type=float, default=3,
                    help='Threshold (multiple of the median count')
args = parser.parse_args()

for fname in args.file:
    f = read_photons.open(fname)
    bins = bin_photons(f.channel(0), bin_width=args.bin_width / f.jiffy, include_zeros=False)
    counts = bins['count']
    t = bins['start_t']
    thresh = args.threshold * np.median(counts)

    bursts = np.array(find_runs(counts > thresh))
    starts = t[bursts[:,0]] - args.buffer / f.jiffy
    ends = t[bursts[:,1]] + args.buffer / f.jiffy
    pl.plot(t, counts, '+')
    for start,end in zip(starts, ends):
        pl.axvspan(start, end, alpha=0.3)
    pl.savefig(fname+'-bursts.png')

    config = json.load(open('config.json')) if os.path.isfile('config.json') else {}
    config.setdefault(fname, {})['exclude'] = zip(starts * f.jiffy, ends * f.jiffy)
    json.dump(config, open('config.json', 'w'))
