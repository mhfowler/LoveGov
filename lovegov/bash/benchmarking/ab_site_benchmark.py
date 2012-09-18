#!/usr/bin/env python

import os
import sys

from lovegov.frontend.analytics import benchmarkPage

print '*** RUNNING APACHE BENCHMARK ON WHOLE SITE ***'

output_folder = sys.argv[1]
print "output_folder: " + output_folder

pages = ['/login/', '/profile/max_fowler/', '/home/']

for page in pages:
    benchmarkPage(page, output_folder)