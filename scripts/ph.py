from scipy.optimize import curve_fit
from numpy import exp, sqrt
import numpy as np
from matplotlib import pyplot as pl
import re
from photon_tools import anisotropy
from photon_tools.anisotropy import Aniso, FitSet
import squmfit.pretty
import cPickle

def sigmoid(x, x0, y0, c, k):
    return c / (1 + 10**(-k * (x+x0))) + y0

def fit_ph(ph, amp1, amp2):
    p = curve_fit(sigmoid, ph, amp1 / amp2)

    x0, x1 = (min(ph) - 1, max(ph) + 1)
    xs = np.linspace(x0, x1)
    pl.scatter(ph, amp)
    pl.plot(xs, sigmoid(xs, *p))
    pl.show()

def read_hist(fname):
    return np.genfromtxt(fname, dtype=None, names='time,counts')

def read_run(basename):
    par = read_hist('%s.ch1.txt' % basename)
    perp = read_hist('%s.ch2.txt' % basename)
    return Aniso(par, perp)

def go(irfs, files, root, run=True, ncomps=2, periods=2, jiffy_ps=8, exc_period=1560):
    n = periods * exc_period
    files = files.items()
    irfs = anisotropy.normalize_irfs(irfs.map(lambda x: x[:n]['counts']))
    corrs = [FitSet('%d' % i, irfs, read_run('run_%03d.pt3' % i).map(lambda x: x[:n]['counts']))
            for i,_ in files]
    if run:
        res0, res = anisotropy.fit(corrs, jiffy_ps=jiffy_ps,
                                   exc_period=exc_period, periods=periods,
                                   n_components=ncomps)
        cPickle.dump(res, open('%s.pickle' % root, 'w'))
        open('%s.mkd' % root, 'w').write(squmfit.pretty.markdown_fit_result(res))
        fig = pl.figure(figsize=(4,12))
        anisotropy.plot(fig, corrs, jiffy_ps, res, sep_resid=True)
        pl.savefig('%s.png' % root)
    else:
        res = cPickle.load('%s.pickle' % root)

    taus = [1/res.params['lambda%d' % i] for i in range(ncomps)]
    amps = [[res.params['%s_amplitude%d' % (pair.name, i)] * tau
            for i,tau in enumerate(taus)]
            for pair in corrs]
    frac = [a/(a+b) for a,b in amps]
    phs = [ph for _,ph in files]
    return np.rec.fromarrays([frac, phs], dtype=[('ph','f4'), ('frac','f4')])

def analyze(phs):
    pl.plot(phs['ph'], phs['frac'], '+')
    pl.xlabel('pH')
    pl.ylabel('population fraction')
    pl.savefig('%s-ph.png' % root)

    from scipy.optimize import curve_fit
    p0 = [4, 0, 1, 1]
    p = curve_fit(sigmoid, phs['ph'], frac['frac'], p0)
    print p
