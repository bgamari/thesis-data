from scipy.optimize import curve_fit
from numpy import exp, sqrt
import numpy as np
from matplotlib import pyplot as pl
import re
from photon_tools import anisotropy
from photon_tools.anisotropy import Aniso, FitSet
import squmfit.pretty
import pickle

use_cache = True

def sigmoid(x, x0, y0, c, k):
    return c / (1 + 10**(-k * (x-x0))) + y0

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

def go(irfs, files, root, *args, **kwargs):
    if use_cache:
        try:
            return pickle.load(open('%s.pickle' % root, 'rb'))
        except:
            pass

    return run(irfs, files, root, *args, **kwargs)

def run_fit(irfs, files, root, run=True, ncomps=2,
            periods=2, jiffy_ps=8, exc_period=1560, params0={}, with_bounds=False):
    n = periods * exc_period
    files = files.items()
    irfs = anisotropy.normalize_irfs(irfs.map(lambda x: x[:n]['counts']))
    corrs = [FitSet('%d' % i, irfs, read_run('run_%03d.pt3' % i).map(lambda x: x[:n]['counts']))
            for i,_ in files]

    res0, res, desc = anisotropy.fit(corrs, jiffy_ps=jiffy_ps,
                                     exc_period=exc_period, periods=periods,
                                     n_components=ncomps, params0=params0)
    open('%s.mkd' % root, 'w').write(squmfit.pretty.markdown_fit_result(res))
    pickle.dump(res.params, open("%s.fit.pickle" % root, 'wb'))
    fig = pl.figure(figsize=(4,12))
    anisotropy.plot(fig, corrs, jiffy_ps, res, sep_resid=True)
    pl.savefig('%s.png' % root)
    return res, corrs

def run(irfs, files, root, ncomps=2, *args, **kwargs):
    res, corrs = run_fit(irfs, files, root, ncomps=ncomps, *args, **kwargs)
    taus = [1/res.params['lambda%d' % i] for i in range(ncomps)]
    amps = [[res.params['%s_amplitude%d' % (pair.name, i)] * tau
            for i,tau in enumerate(taus)]
            for pair in corrs]
    frac = [a/(a+b) for a,b in amps]
    phs = [ph for _,ph in files]
    res = np.rec.fromarrays([phs, frac], dtype=[('ph','f4'), ('frac','f4')])
    pickle.dump(res, open('%s.pickle' % root, 'wb'))
    return res

def analyze(phs, root, sign=+1):
    from scipy.optimize import curve_fit
    p0 = [4, 0, 1, sign]
    p,pcov = curve_fit(sigmoid, phs['ph'], phs['frac'], p0)
    print(root)
    print(p)
    print(pcov)
    print()

    xs = np.linspace(0.5, 8, 500)
    pl.figure()
    pl.plot(phs['ph'], phs['frac'], '+')
    pl.plot(xs, sigmoid(xs, *p))
    pl.xlabel('pH')
    pl.ylabel('population fraction')
    pl.savefig('%s-ph.png' % root)

def analyze2(phs, root, sign=+1):
    import squmfit, squmfit.plot
    fit = squmfit.Fit()
    ph = squmfit.Argument('ph')
    model =   sigmoid(ph, fit.param('pka1', initial=2), 0,
                      fit.param('amp1', initial=0.5),
                      fit.param('scale1', initial=sign)) \
            + sigmoid(ph, fit.param('pka2', initial=3), 0,
                      fit.param('amp2', initial=0.5),
                      fit.param('scale2', initial=sign))
    fit.add_curve('hi', model, data=phs['frac'], ph=phs['ph'])
    res = fit.fit()
    squmfit.plot.plot_fit('ph', res, marker='o')
    print(squmfit.pretty.markdown_fit_result(res))
    pl.savefig('%s-ph.png' % root)
