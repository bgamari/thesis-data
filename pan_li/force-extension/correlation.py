#!/usr/bin/python

import numpy as np
from numpy import exp, log, log10, newaxis, abs
import scipy.signal
import matplotlib.pyplot as pl
from mpl_toolkits.axes_grid1 import Grid
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from statsmodels.tsa.stattools import acf

# left, bottom, width, height
rect = (0.18, 0.20, 0.75, 0.73)

def read_traj(fname):
    return np.genfromtxt(fname, names='time,force,ext')

def autocorr(d, dt=6e-3):
    d = d - np.mean(d)
    a = fft(d)
    b = ifft(a * np.conj(a))
    corr = np.real(b)[:len(d)/2]
    taus = np.arange(len(d)/2) * dt
    norm = np.std(d)**2 * len(d)
    return taus, corr/norm

def correlation_plot(d, dt=6e-3, **kwargs):
    corr, conf = acf(d, nlags=len(d)-1, alpha=0.05)
    taus = dt*np.arange(0, len(d))
    ax = pl.gca()
    ax.plot(taus, corr, **kwargs)
    ax.fill_between(taus, y1=conf[:,0], y2=conf[:,1], color='k', alpha=0.2, lw=0)
    ax.set_xscale('log')
    ax.set_xlabel(r'$\tau$ (seconds)')
    ax.set_ylabel(r'$G(\tau)$')
    ax.grid()

d = read_traj('hopdata.txt')

def plot_force_extension(d):
    from mpl_toolkits.axes_grid1 import AxesGrid
    grid = AxesGrid(pl.figure(), 111, nrows_ncols=(2,1), aspect=False)
    grid[0].plot(d['time'], d['ext'])
    grid[0].set_ylabel('extension (nm)')
    grid[1].plot(d['time'], d['force'])
    grid[1].set_ylabel('force')
    grid[1].set_xlabel('time (s)')

#pl.clf()
#pl.hist(d['time'][1:] - d['time'][:-1], range=(-1e-3, 1e-2))
#pl.xlabel('inter-sample time (s)')
#pl.ylabel('counts')
#pl.savefig('jitter.png')
#pl.clf()

def smooth(x, window):
    s = np.r_[x, x[-1:-window:-1]]
    w = np.ones(window, 'd')
    return np.convolve(w/sum(w), s, mode='valid')

def plot_smoothed(x, y, window, **kwargs):
    pl.plot(x, smooth(y, window), **kwargs)

def plot_timeseries(x, y, window, bins):
    pl.xscale('linear')
    pl.hist2d(x, y, bins=bins, alpha=0.5)
    plot_smoothed(x, y, window, c='k')
    pl.axhline(np.mean(y), c='k')
    pl.xlabel('time (s)')
    pl.ylabel('extension (nm)')

plot_timeseries(d['time'], d['ext'], 1000, (100,100))
pl.savefig('extension-timeseries.png')
    
dt = 5e-3

xs = np.arange(min(d['time']), max(d['time']), dt)
interp = interp1d(d['time'], d['ext'], kind='linear')(xs)
pl.figure()
correlation_plot(interp, dt=dt, c='darkblue', marker=',', linestyle=' ', label='ext')

def ornstein_uhlenbeck(tau, taud, offset=0, alpha=1, amp=1):
    return offset + amp * exp(-(tau/taud)**alpha)

taus, corr = autocorr(interp, dt)
fit_taus = taus[taus<1e1]
fit_corr = corr[taus<1e1]
(params, cov) = curve_fit(ornstein_uhlenbeck,
                          fit_taus, fit_corr,
                          p0=[1e-3, 0, 1, 1])
print 'Chi^2', np.sum((ornstein_uhlenbeck(fit_taus, *params) - fit_corr)**2)

(taud,offset,alpha,amp) = params
print params
taus_ = np.logspace(-3, log10(max(taus)), 1000)
pl.semilogx(taus_, ornstein_uhlenbeck(taus_, *params), '-k', label='Model')
pl.show()

