#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.frontend.analytics import metricsToExcel
    from lovegov.modernpolitics.constants import PROJECT_PATH
    import os
    from pprint import pprint

    print "================= scriptCreateResponses() ==================="
    print '======================================================================='
    file = os.path.join(PROJECT_PATH, 'logging/metrics/10-1-12.xls')
    print file
    errors = metricsToExcel(file)

