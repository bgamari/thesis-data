#!/usr/bin/python

import numpy as np
from numpy import exp, log, log10
import scipy.signal
import matplotlib.pyplot as pl
from mpl_toolkits.axes_grid1 import Grid
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

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
    taus, corr = autocorr(d, dt)
    ax = pl.gca()
    ax.plot(taus, corr, **kwargs)
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

pl.hist(d['time'][1:] - d['time'][:-1], range=(-1e-3, 1e-2))
pl.xlabel('inter-sample time (s)')
pl.ylabel('counts')
pl.savefig('jitter.png')
pl.clf()

print 'mean extension', np.mean(d['ext'][:1000]), np.mean(d['ext'][-1000:])
def plot_smoothed(x, y, window, **kwargs):
    s = np.r_[y, y[-1:-window:-1]]
    w = np.ones(window, 'd')
    smoothed = np.convolve(w/sum(w), s, mode='valid')
    pl.plot(x, smoothed, **kwargs)

def plot_timeseries(x, y, window, bins):
    pl.xscale('linear')
    pl.hist2d(x, y, bins=bins, alpha=0.5)
    plot_smoothed(x, y, window, c='k')
    pl.axhline(np.mean(y), c='k')
    
dt = 5e-3

xs = np.arange(min(d['time']), max(d['time']), dt)
interp = interp1d(d['time'], d['ext'], kind='linear')(xs)
correlation_plot(interp, dt=dt, c='b', marker='+', label='ext')
#pl.show()

def ornstein_uhlenbeck(tau, taud, offset):
    amp = 1
    return offset + amp * exp(-tau/taud)

taus, corr = autocorr(interp, dt)
((taud,offset), cov) = curve_fit(ornstein_uhlenbeck,
                                 taus[taus<1e1], corr[taus<1e1],
                                 p0=[1e-3, 0])
taus_ = np.logspace(-3, log10(max(taus)), 1000)
print 'tau_d', taud
pl.plot(taus_, ornstein_uhlenbeck(taus_, taud, offset), '-k', label='Model')
pl.show()
