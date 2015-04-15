#!/usr/bin/python

from __future__ import division
from matplotlib import pyplot as pl
import numpy as np
from numpy import newaxis
import argparse
import scipy.optimize
from scipy.stats import lognorm
from scipy.integrate import quad
from photon_tools.fcs_mem import fcs_mem

def parse_runs(runs):
    def parse_range(r):
        i = r.find('-')
        if i != -1:
            a = int(r[:i])
            b = int(r[i+1:])
            if a > b:
                raise RuntimeError('lower range bound must be less than or equal to upper bound')
            return range(a,b+1)
        else:
            return [int(r)]

    return [i for r in runs.split(',') for i in parse_range(r)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('-r', '--runs', type=str, required=True, help='run numbers (ranges and lists supported; e.g. "--runs=1-4,5,8")')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help='output plot file name')
    parser.add_argument('-n', '--nu', type=float, default=5e-6, help='regularizer strength')
    args = parser.parse_args()

    n_models = 800

    runs = parse_runs(args.runs)

    curvesP = pl.subplot(311)
    residualsP = pl.subplot(312)
    weightsP = pl.subplot(313)

    a = np.genfromtxt(args.file, skip_header=1, usecols=range(8,8+2*192), delimiter='\t')
    for color, i in zip(pl.rcParams['axes.color_cycle'], runs):
        taus = a[i,0:192].T
        Gs = a[i,192:192*2].T

        model_taus = np.logspace(0, 7, n_models)
        models = np.exp(-taus[newaxis,:] / model_taus[:,newaxis])
        sigma = np.ones_like(Gs) * 1e-2
        weights = fcs_mem(Gs, models, sigma, nu=args.nu)
        mixture = np.sum(weights[:,newaxis] * models, axis=0)

        curvesP.errorbar(taus, Gs, label='run %d' % i, yerr=sigma, c=color)
        curvesP.plot(taus, mixture, c=color)
        residualsP.scatter(taus, (Gs - mixture) / sigma, c=color)
        weightsP.scatter(model_taus, weights, c=color)

        avg = np.average(model_taus, weights=weights)
        weightsP.axvline(avg, alpha=0.5, c=color)
        print i, 'Z average=%f us, mode=%f' % (avg, model_taus[np.argmax(weights)])

    residualsP.axhline(0, c='k')
    residualsP.set_xscale('log')
    residualsP.set_ylabel('residuals')
    weightsP.set_xscale('log')
    weightsP.set_xlabel('$\\tau$ (microseconds)')
    weightsP.set_ylim(0, None)
    weightsP.set_xlim(*curvesP.get_xbound())
    weightsP.set_ylabel('weight')
    curvesP.set_xscale('log')
    curvesP.legend()
    curvesP.set_xlabel('$\\tau$ (microseconds)')
    curvesP.set_ylabel('$G(\\tau)$')
    curvesP.axhline(0, c='k')
    if args.output is not None:
        pl.savefig(args.output.name)
    else:
        pl.show()

if __name__ == '__main__':
    main()
