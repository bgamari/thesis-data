#!/usr/bin/python

import itertools
import numpy as np
from numpy import array, linspace, arange, min, max, mean, dot
from scipy.optimize import leastsq

from matplotlib import pylab as pl
from mpl_toolkits.mplot3d import Axes3D

import warnings
warnings.filterwarnings("always")

def guess_size(data):
        return [ len(np.unique(data[axis])) for axis in 'x y z'.split() ]
                        
def read_rough(filename, size='guess'):
        dt = np.dtype([
                ('x', np.float32), ('y', np.float32), ('z', np.float32),
                ('fb_x', np.float32), ('fb_y', np.float32), ('fb_z', np.float32), 
                ('psd_x', np.float32), ('psd_y', np.float32),
                ('sum_x', np.float32), ('sum_y', np.float32)])
	d = np.loadtxt(filename, dtype=dt)
        d.sort(order=('x','y','z'))
        if size == 'guess':
                d = d.reshape(guess_size(d))
        elif size is not None:
                d = d.reshape(size)
        return d

def plot_rough(data=None, use_fb=True, levels=20, colorbars=False):
        if data is None: data = read_rough('rough')
        (x, y) = ('fb_x', 'fb_y') if use_fb else ('x', 'y')
        fig = pl.figure()
        #pos = np.genfromtxt("rough_pos")
        pos = None
        print pos
        for n,signal in enumerate(['psd_x', 'psd_y', 'sum_x', 'sum_y']):
                pl.subplot(2,2,n+1)
                pl.contourf(data[x][:,:,0], data[y][:,:,0], data[signal][:,:,0], levels)
                pl.title(signal)
                pl.axis('equal')
                pl.axis('tight')
                if colorbars:
                        pl.colorbar()

                if pos is not None:
                        pl.axvline(pos[0], alpha=0.3)
                        pl.axhline(pos[1], alpha=0.3)

        fig.show()

def plot_rough_z(data=None, use_fb=True):
        if data is None: data = read_rough('rough_z')
        z = 'fb_z' if use_fb else 'z'
        fig = pl.figure()
        for n,signal in enumerate(['psd_x', 'psd_y', 'sum_x', 'sum_y']):
                pl.subplot(2,2,n+1)
                pl.scatter(data[z], data[signal])
                pl.title('%s vs. %s' % (signal, z))
                pl.axis('equal')
                pl.axis('tight')

        fig.show()

def autoslice(data, axis, frac=0.1):
        _max, _min = max(data[axis]), min(data[axis])
        print _max, _min
        center = _min + (_max - _min)/2
        tol = frac * (_max - _min)
        return slice(data, axis, center, tol)

def slice(data, axis='z', center=0.5, tol=1e-3):
        cond = (data[axis] > (center-tol)) & (data[axis] < (center+tol))
        return np.extract(cond, data)

def read_fine(filename):
        dt = np.dtype([
                ('fb_x', np.float32), ('fb_y', np.float32), ('fb_z', np.float32), 
                ('psd_x', np.float32), ('psd_y', np.float32),
                ('sum_x', np.float32), ('sum_y', np.float32) ])
	d = np.loadtxt(filename, dtype=dt)
        return d

def plot_fine(data=None, x='fb_x', y='fb_y', z='psd_x'):
        if data is None: data = read_fine('fine')
	fig = pl.figure()
	ax = Axes3D(fig)
        ax.scatter(data[x], data[y], data[z], c='r', marker='o')
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_zlabel(z)
	fig.show()
	return ax

def plot_scan(data=None, x='fb_x', y='fb_y', z='fb_z', c='sum_x'):
        if data is None: data = read_fine('scan')
	fig = pl.figure()
	ax = Axes3D(fig)
        a = ax.scatter(data[x], data[y], data[z], c=data[c], marker='o', alpha=0.2)
        pl.colorbar(a)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_zlabel(z)
	fig.show()
	return ax

def plot_pos(data=None):
        if data is None: data = np.genfromtxt('pos', skip_footer=1)
        pl.figure()
        pl.plot(data[:,7], label='X')
        pl.plot(data[:,8], label='Y')
        pl.plot(data[:,9], label='Z')
        pl.legend(loc='upper left')
        pl.show()

def plot_resids(data, plot_all=True, relative=True):
        pl.figure()
        plots = [ (ax, ax) for ax in 'x y z'.split() ]
        rows = 1
        if plot_all:
                plots = itertools.product('x y z'.split(), 'x y z'.split())
                rows = 3

        for n, (pos_axis, resid_axis) in enumerate(plots):
                pl.subplot(rows,3,n+1)
                ylabel = '%s residual' % resid_axis
                a = 1
                if relative:
                        ylabel = '%s relative residual' % resid_axis
                        a = 1 / data['bead_' + resid_axis]

                pl.scatter(data[pos_axis], a*data['resid_' + resid_axis])
                pl.title('%s vs. %s position' % (ylabel, pos_axis))
                pl.xlabel('%s position' % pos_axis)
                pl.ylabel(ylabel)

def plot_delays(data, offset=0.1):
        colors = 'b g r c m y k w'.split()
        pl.figure()
        off = 0
        for c,(k,v) in zip(colors, data.items()):
                pl.scatter(v['fb_z'], v['sum_y']+off, c=c, label=k)
                off += offset
        pl.legend()

