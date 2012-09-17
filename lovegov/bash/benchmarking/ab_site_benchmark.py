#!/usr/bin/env python

import os
import sys

pages = ['/login/', '/home/', '/profile/max_fowler/']

print '*** RUNNING APACHE BENCHMARK ON WHOLE SITE ***'

output_folder = sys.argv[1]
print "output_folder: " + output_folder

for page in pages:
    command = "./ab_page_benchmark.py" + page + " " + output_folder
    os.system(command)