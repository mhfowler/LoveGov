__author__ = 'maxfowler'

from lovegov.frontend.views import *
from lovegov.scripts.daily_summary import *


#g = Group.objects.get(title__contains="Whales")

#updateGroupView(g)

sendLaunchEmail(getUser("Max Fowler"))

