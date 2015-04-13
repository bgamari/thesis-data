#!/usr/bin/python

from __future__ import division
from matplotlib import pyplot as pl
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file')
args = parser.parse_args()

a = np.genfromtxt(args.file, skip_header=1, usecols=range(8,8+2*192), delimiter='\t')
for i in range(a.shape[0]):
    taus = a[i,0:192].T
    Gs = a[i,192:192*2].T
    pl.plot(taus, Gs, '+', label='run %d' % i)
    f = lambda taud: 1. / (1 + taus / taud)
    pl.plot(taus, f(1e3))

pl.xscale('log')
pl.legend()
pl.xlabel('$\\tau$ (microseconds)')
pl.ylabel('$G(\\tau)$')
pl.show()
