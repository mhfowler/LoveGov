#!/usr/bin/env python

from lovegov.frontend.analytics import apacheBenchmark
import sys

print "*** RUNNING APACHE BENCHMARK FOR PAGE ***"

domain = "http://dev.lovegov.com"

# run benchmark on page for all different concurrencies
page = sys.argv[1]
url = domain + page
print "url: " + url

output_folder = sys.argv[2]
print "output_folder: " + output_folder

num_requests = 1000
concurrencies = [1, 10, 20, 50]
#[1, 10, 20, 50, 100, 200, 500, 1000]

for num_concurrent in concurrencies:
    apacheBenchmark(domain, page, output_folder, num_requests, num_concurrent)

