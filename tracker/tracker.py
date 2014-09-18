#!/usr/bin/python

import subprocess

class Tracker(object):
        def __init__(self):
                PIPE=subprocess.PIPE
                args = ('ssh', 'tracker', './tracker')
                self.p = subprocess.Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        def read_not_prompt(self):
                while True:
                        l = self.p.stdout.readline()
                        if not l.startswith('>'):
                                return l
