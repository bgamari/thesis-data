#!/usr/bin/python

import squmfit
import squmfit.plot
import numpy as np
from photon_tools.fcs_models import *
import matplotlib.pyplot as pl

def load_corr(fname):
    return np.genfromtxt(fname, dtype=None, names='lag,G,var')

def load_runs(runs):
    return [load_corr('2015-05-13-run_%03d.timetag.xcorr-0-1' % i)
            for i in runs]

def fit(curves):
    fit = squmfit.Fit()
    lag = squmfit.Argument('lag')
    aspect = fit.param('aspect', initial=10)
    tauD = fit.param('tauD', initial=100)
    tauF = fit.param('tauF', initial=1)
    for i, curve in enumerate(curves):
        n = fit.param('n%d' % i, initial=1)
        F = fit.param('F%d' % i, initial=0.1)
        model = three_dim_diffusion(lag, tauD, aspect, n) * triplet_correction(lag, F, tauF)
        fit.add_curve('curve%d' % i, model, curve['G'] - 1, weights=1/np.sqrt(curve['var']), lag=curve['lag'] / 1e-6)

    res = fit.fit()
    squmfit.plot.plot_fit('lag', res, xscale='log')
    pl.show()
    print res.params
    return res

fit(load_runs([14, 15, 16, 17, 18, 19]))
