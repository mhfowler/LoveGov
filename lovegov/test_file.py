""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.views import *
from lovegov.frontend.analytics import *

m = getUser("Max Fowler")

sendWeeklyDigestEmail(m)

