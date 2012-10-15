""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.analytics import *

#time_start = datetime.datetime(year=2012, month=10, day=11, hour=6)
#time_end = datetime.datetime.now()
#
#analyzeCookieData(time_start, time_end)

from lovegov.frontend.views import *
from lovegov.scripts.alpha import scriptCreateCongressAnswers

scriptCreateCongressAnswers()
