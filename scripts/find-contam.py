#!/usr/bin/python

import numpy as np
from photon_tools.bin_photons import bin_photons
from photon_tools.io import read_photons
import matplotlib.pyplot as pl
from config_file import Config

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
parser.add_argument('-w', '--bin-width', type=float, default=0.1,
                    help='Bin width in seconds')
parser.add_argument('-b', '--buffer', type=float, default=0.2,
                    help='Amount of time before and after burst to drop')
parser.add_argument('-t', '--threshold', type=float, default=10,
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
    print '%s: Found %d bursts above threshold of %f / bin' % (fname, len(bursts), thresh)

    pl.clf()
    pl.plot(t * f.jiffy, counts, '+')
    for start,end in zip(starts, ends):
        pl.axvspan(start * f.jiffy, end * f.jiffy, alpha=0.3, color='k')
    pl.savefig(fname+'-bursts.png')

    with Config() as config:
        config.setdefault(fname, {})['exclude'] = {
                'intervals': zip(starts * f.jiffy, ends * f.jiffy),
                'buffer': args.buffer,
                'threshold': thresh,
                'threshold-factor': args.threshold,
        }
