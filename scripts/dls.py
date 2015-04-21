#!/usr/bin/python

from __future__ import division
from matplotlib import pyplot as pl
import numpy as np
from numpy import newaxis
import argparse
import scipy.optimize
from scipy.stats import lognorm
from scipy.integrate import quad
from photon_tools.utils import parse_int_list

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

def cumulant(tau, amp, gamma, *cumulants):
    cumulants = np.array(cumulants)
    idxs = np.arange(2, len(cumulants)+2)
    signs = np.array([+1 if i % 2 == 0 else -1 for i in idxs])
    #terms = signs * cumulants / np.factorial(idxs) * tau**idxs
    terms = signs[newaxis,:] * cumulants[newaxis,:] * tau[:,newaxis]**idxs[newaxis,:]
    return amp * np.exp(-tau * gamma) * (1 + np.sum(terms, axis=1))

def fit_lognormal(taus, Gs, sigma):
    p0 = [1, 2, 1]
    res = scipy.optimize.minimize(squared_error(lognormal_diff, taus, Gs, sigma), p0,
                                  bounds=[(0,None), (0, None), (0, None)],
                                  method='l-bfgs-b')
    return res.x

def fit_cumulants(taus, Gs, sigma, nCum=1):
    p0 = [1, 1e-3] + [0] * nCum
    p, pcov = scipy.optimize.curve_fit(cumulant, taus, Gs, p0)
    return p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Export file from Malvern ZetaSizer software')
    parser.add_argument('-r', '--runs', type=str, required=True, help='run numbers (ranges and lists supported; e.g. "--runs=1-4,5,8")')
    args = parser.parse_args()

    runs = parse_int_list(args.runs)
    fit_type = 'lognorm'
    assert fit_type in ['cum', 'lognorm']

    a = np.genfromtxt(args.file, skip_header=1, usecols=range(8,8+2*192), delimiter='\t')
    for i in runs:
        taus = a[i,0:192].T
        Gs = a[i,192:192*2].T
        sigma = 1e-2
        pl.errorbar(taus, Gs, label='run %d' % i, yerr=sigma)
        if fit_type == 'lognorm':
            p = fit_lognormal(taus, Gs, sigma)
            pl.plot(taus, lognormal_diff(taus, *p))
        elif fit_type == 'cum':
            p = fit_cumulants(taus, Gs, sigma, nCum=2)
            pl.plot(taus, cumulant(taus, *p))
        print p

    pl.xscale('log')
    pl.legend()
    pl.xlabel('$\\tau$ (microseconds)')
    pl.ylabel('$G(\\tau)$')
    pl.axhline(0, c='k')
    pl.show()

if __name__ == '__main__':
    main()
