#!/usr/bin/python

from ph import *
import ph
#ph.use_cache = False

irfs = read_run('run_002.pt3')

# OG488
files = {
    6:  2.5,    7:  3.0,
    8:  3.5,    9:  4.0,
    10: 4.5,   11:  5.0,
    12: 5.5,   13:  6.0,
    14: 6.5,   15:  7.0,
    16: 7.5,   17:  8.0,
    18: 8.0,   19:  7.5,
    20: 7.0,   21:  6.5,
    22: 6.0,   23:  5.5,
    24: 5.0,   25:  4.5,
    26: 4.0,   27:  3.5,
    28: 3.0,   29:  2.5,
}
analyze(go(irfs, files, 'og488'), 'og488', -1)

# BCECF
files = {
    31: 2.5,
    32: 3.0,   33: 3.5,
    34: 4.0,   35: 4.5,
    36: 5.0,   37: 5.5,
    38: 6.0,   39: 6.5,
    40: 7.0,   41: 7.5,
    42: 8.0,   43: 8.0,
    44: 8.0,   45: 7.5,
    46: 7.0,   47: 6.5,
    48: 6.0,   49: 5.5,
    50: 5.0,   51: 4.5,
    52: 4.0,   53: 3.5,
    54: 3.0,   55: 2.5,
}
analyze2(go(irfs, files, 'bcecf'), 'bcecf', -1)

# Droplet