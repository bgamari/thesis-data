#!/usr/bin/python

import os.path
import subprocess
import multiprocessing
from glob import glob

dates = '2015-05-05 2015-05-02 2015-04-22 2015-04-20 2015-04-19 2015-04-15 2015-03-19 2015-03-12 2015-02-19 2015-02-17 2015-02-12'.split()

def date_path(date):
    year, month, day = date.split('-')
    return os.path.expanduser('~/data/by-date/%s/%s-%s/%s-%s-%s' % (year, year, month, year, month, day))

files = []
for d in dates:
    files.extend(glob(date_path(d)+'/*.timetag'))

pool = multiprocessing.Pool(16)
def do_file(f):
    subprocess.check_call(['summarize-fcs', f])

pool.map(do_file, files)
