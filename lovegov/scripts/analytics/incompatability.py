__author__ = 'maxfowler'

from lovegov.frontend.views import *

c = CompatabilityLog.objects.all()

incompatible = {}

for x in c:
    for i in x.incompatible:
        if i not in incompatible:
            incompatible[i] = (1, {x})
        else:
            incompatible[i][0] += 1
            incompatible[i][1].add(x)

incompatible_list = incompatible.items()
incompatible_list.sort(key=lambda x:x[1][0])

print "INCOMPATABILITY LOG"
for x in incompatible_list:
    print str(x[0]) + ": " + str(x[1][0])