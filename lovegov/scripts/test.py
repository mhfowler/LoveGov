__author__ = 'maxfowler'

from lovegov.frontend.views import *


#g = Group.objects.get(title__contains="Whales")

#updateGroupView(g)

m = getUser("Maximus Fowler")

m.updateHotFeed()

