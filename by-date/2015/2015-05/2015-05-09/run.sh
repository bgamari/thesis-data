#!/bin/bash

fcs-corr -p 2015-05-09-run_110.timetag --engine=hphoton --plot-chunks -n 10 -c0,1 -E5e-7 -e1062-1069 -L10
fcs-corr -p 2015-05-09-run_111.timetag --engine=hphoton --plot-chunks -n 10 -c0,1 -E5e-7 -e162-168 -L10

