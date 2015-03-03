#!/usr/bin/python

import matplotlib.pyplot as pl
import numpy as np

tau1 = 2307
tau2 = 4718

a = np.genfromtxt('results.txt', dtype=None, names=True)
#pl.plot(a['actual_pH'], a['fraction'], 'o')
f = a['fraction']
pl.plot(a['actual_pH'], f * tau1 / (f * tau1 + (100-f) * tau2), 'o')
#pl.ylim(0,100)
pl.show()

