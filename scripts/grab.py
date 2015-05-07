#!/usr/bin/python

import subprocess
import threading

dates = '2015-05-05 2015-05-02 2015-04-22 2015-04-20 2015-04-19 2015-04-15 2015-03-19 2015-03-12 2015-02-19 2015-02-17 2015-02-12'.split()

def date_path(date):
    year, month, day = date.split('-')
    return 'data/by-date/%s/%s-%s/%s-%s-%s' % (year, year, month, year, month, day)


files = subprocess.check_output(['ls'] + [date_path(d)+'/*.timetag' for d in dates))

pool = threading.ThreadPool()
def do_file(f):
    subprocess.check_call(['summarize-fcs', f])

pool.map(do_file, files)
