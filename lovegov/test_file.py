from lovegov.frontend.analytics import *
from lovegov.frontend.views import *

start_date = datetime.datetime(year=2012, month=7, day=5, hour=6)
end_date = datetime.datetime.now()

delta = datetime.timedelta(days=14)
time_tuples = getTimeTuplesByDelta(start_date, end_date, delta)

output_file = os.path.join(PROJECT_PATH, 'logging/metrics/percentage_analytics_weekly.xls')

percentageAnalytics(time_tuples=time_tuples, resolution=20, output_file=output_file)