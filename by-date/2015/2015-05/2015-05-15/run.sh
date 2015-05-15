#!/bin/bash

fcs-corr -p 2015-05-15-run_019.timetag -c0,1 -L10 --engine=hphoton -n0 -e72-77 -e398-402 -e581-591 -e661-665 -e950-955 -e969-674
fcs-corr -p 2015-05-15-run_018.timetag -c0,1 -L10 --engine=hphoton -n0  -e 482-484
fcs-corr -p 2015-05-15-run_011.timetag -c0,1 -L10 --engine=hphoton -n0 -e 223-229
