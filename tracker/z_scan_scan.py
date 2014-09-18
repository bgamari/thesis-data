#!/usr/bin/python

from numpy import arange


p.stdout.readline()
cmds = """
set scale_psd_inputs 0
set rough_cal.xy_range 0.4
set rough_cal.xy_points 40
set rough_cal.z_range 0.5
set rough_cal.z_points 500
set feedback.delay 3000
set feedback.show_rate 1
set feedback.max_delta 0.05
set fine_cal.xy_range 0.008
set fine_cal.z_range 0.016
set pids.x_prop  0.6
set pids.y_prop  0.6
set pids.z_prop  0.6
set pids.x_int  0.10
set pids.y_int  0.10
set pids.z_int  0.15
set pids.x_tau  10
set pids.y_tau  10
set pids.z_tau  40
set pids.x_diff  0
set pids.y_diff  0
set pids.z_diff  0

rough-cal
"""
p.stdin.write(cmds)
read_not_prompt()

for z in arange(0.1, 0.9, 0.05):
        p.stdin.write('set rough.pos_z %f\n' % z)
        p.stdin.write('fine-cal\n')
        l = read_not_prompt()

        print l
        print z, l.split()[4]
        z += 0.05


