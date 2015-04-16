#!/usr/bin/python

from __future__ import division
from matplotlib import pyplot as pl
import numpy as np
from numpy import newaxis
import argparse
import scipy.optimize
from scipy.stats import lognorm
from scipy.integrate import quad

parser = argparse.ArgumentParser()
parser.add_argument('file')
args = parser.parse_args()

def lognormal_diff(tau, amp, mu, sigma):
    print amp, mu, sigma
    dist = lognorm([sigma], loc=mu*1000)
    n = 10000
    #taus = dist.rvs(n)
    #(a,b) = dist.interval(0.9)
    (a,b) = (max(1e-4, mu - sigma), mu + 100*sigma)
    taus = np.logspace(np.log(a), np.log(b), n)
    G = amp * np.sum(dist.pdf(taus) * np.exp(-tau[:,newaxis] / taus[newaxis,:]), axis=1)
    return G

def squared_error(f, x, y, sigma):
    def go(*ps):
        res = np.sum(((f(x, *ps[0]) - y) / sigma)**2)
        print res
        return res
    return go

def f(tau, taud, amp):
    return amp / (1 + tau / taud)

a = np.genfromtxt(args.file, skip_header=1, usecols=range(8,8+2*192), delimiter='\t')
for i in [24]: #range(a.shape[0]):
    taus = a[i,0:192].T
    Gs = a[i,192:192*2].T
    sigma = 1e-2
    pl.errorbar(taus, Gs, label='run %d' % i, yerr=sigma)
    #p, pcov = scipy.optimize.curve_fit(f, taus, Gs, [1e-3, 1])
    p0 = [1, 2, 1]
    p=p0
    #p, pcov = scipy.optimize.curve_fit(lognormal_diff, taus, Gs, p0, sigma=sigma)
    res = scipy.optimize.minimize(squared_error(lognormal_diff, taus, Gs, sigma), p0,
                                  bounds=[(0,None), (0, None), (0, None)],
                                  method='l-bfgs-b')
    p = res.x
    pl.plot(taus, lognormal_diff(taus, *p))
    print p
    #print pcov

pl.xscale('log')
pl.legend()
pl.xlabel('$\\tau$ (microseconds)')
pl.ylabel('$G(\\tau)$')
pl.axhline(0, c='k')
pl.show()
