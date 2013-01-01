#!/usr/bin/env python

if __name__ == "__main__":

    from lovegov.frontend.analytics import *
    from lovegov.frontend.views import *

    time_tuples = []

    start_date = datetime.datetime(year=2012, month=4, day=10, hour=6)
    end_date = datetime.datetime(year=2012, month=11, day=6, hour=6)
    time_tuples.append((start_date, end_date))

    start_date = datetime.datetime(year=2012, month=4, day=10, hour=6)
    end_date = datetime.datetime(year=2012, month=7, day=10, hour=6)
    time_tuples.append((start_date, end_date))

    start_date = datetime.datetime(year=2012, month=7, day=10, hour=6)
    end_date = datetime.datetime(year=2012, month=9, day=7, hour=6)
    time_tuples.append((start_date, end_date))

    start_date = datetime.datetime(year=2012, month=9, day=7, hour=6)
    end_date = datetime.datetime(year=2012, month=10, day=25, hour=6)
    time_tuples.append((start_date, end_date))

    start_date = datetime.datetime(year=2012, month=10, day=25, hour=6)
    end_date = datetime.datetime(year=2012, month=11, day=6, hour=6)
    time_tuples.append((start_date, end_date))

    output_file = os.path.join(PROJECT_PATH, 'logging/metrics/percentage_analytics_retention.xls')

    percentageAnalytics(time_tuples=time_tuples, resolution=20, output_file=output_file)