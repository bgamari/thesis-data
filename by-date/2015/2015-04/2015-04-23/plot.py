#!/usr/bin/python

from matplotlib import pyplot as pl
import numpy as np

d = np.genfromtxt('obs.txt', dtype=None, names='record,pore,radius')
pl.scatter(d['pore'], d['radius'])
pl.xlabel('Pore diameter (nm)')
pl.ylabel('Droplet radius (nm)')
pl.show()
