#!/bin/bash

ls *046.timetag | xargs -n1 -P10 fcs-corr -p -A 2015-02-10-run_000.timetag -L10
