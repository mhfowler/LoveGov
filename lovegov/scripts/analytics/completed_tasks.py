#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.frontend.analytics import *
    from lovegov.frontend.views import *

    initializeAnalyticsTasks()

    updateUserAnalyticsData()

    start_date = datetime.datetime(year=2012, month=4, day=10, hour=6)
    end_date = datetime.datetime.now()

    delta = datetime.timedelta(days=7)
    time_tuples = getTimeTuplesByDelta(start_date, end_date, delta)

    output_file = os.path.join(PROJECT_PATH, 'logging/metrics/completed_tasks_weekly.xls')

    completedTasksAnalytics(time_tuples, output_file)