#!/usr/bin/python

import matplotlib.pyplot as pl
import numpy as np

tau1 = 2250
tau2 = 4623

phs = {
    'cit2.5': 2.57,
    'cit3.0': 3.15,
    'cit3.5': 3.57,
    'cit4.0': 4.09,
    'cit4.5': 4.56,
    'cit5.0': 5.09,
    'cit5.5': 5.75,
    
    'phos6.0': 5.95,
    'phos6.5': 6.37,
    'phos7.0': 6.87,
    'phos7.5': 7.39,
    'phos8.0': 7.33,
}

results = np.genfromtxt('results.txt', dtype=None, names=True)
ph = np.array([phs.get(res['buffer'], 0) for res in results])

for buff in ['cit', 'phos']:
    b = np.char.find(results['buffer'], buff) != -1
    f = results['fraction'][b]
    pl.plot(ph[b], f * tau1 / (f * tau1 + (100-f) * tau2), 'o')

#pl.plot(ph, results['fraction'], 'o')
#pl.ylim(0,100)
pl.show()

