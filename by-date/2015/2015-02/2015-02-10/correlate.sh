#!/bin/bash

ls *.timetag | xargs -n1 -P4 fcs-corr -p -A 2015-02-10-run_000.timetag -L2 -E1e-6 --engine=hphoton
