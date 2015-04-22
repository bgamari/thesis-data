#!/usr/bin/python

import matplotlib.pyplot as pl
import subprocess
import sys
import numpy as np

def go(path, channel):
    out = '%s.ch%d.txt' % (path, channel)
    subprocess.check_call(['picoquant-export', 'histogram', '-o', out,
                           '-c%d' % channel, path])
    return np.genfromtxt(out, dtype=None, names='time,count')

for f in sys.argv[1:]:
    pl.clf()
    for c in [1,2]:
        a = go(f, c)
        print '%s channel %d: %d photons' % (f, c, np.sum(a['count']))
        pl.semilogy(a['time'] / 1000., a['count'], label='channel %d' % c)

    pl.suptitle(f) 
    pl.xlim(0, 25)
    pl.legend()
    pl.xlabel('time (ns)')
    pl.ylabel('counts')
    pl.savefig(f+'.svg')
