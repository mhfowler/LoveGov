#!/usr/bin/env python

from lovegov.frontend.analytics import benchmarkPage
import sys


# run benchmark on page for all different concurrencies
page = sys.argv[1]
output_folder = sys.argv[2]
print "output_folder: " + output_folder


benchmarkPage(page, output_folder)