""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.analytics import *

#time_start = datetime.datetime(year=2012, month=10, day=11, hour=6)
#time_end = datetime.datetime.now()
#
#analyzeCookieData(time_start, time_end)

from lovegov.frontend.views import *
from lovegov.scripts.alpha import scriptCreateCongressAnswers

a = LegislationAmendment.objects.all()

def printAmendmentInfo(a):
    types = {}
    total = 0
    for x in a:
        rolls = CongressRoll.objects.filter(amendment=x)
        count = 0
        for r in rolls:
            type = r.type
            if not type in types:
                types[type] = 0
            types[type] += 1
            count += 1
        if not count in types:
            types[count] = 0
        types[count] += 1
        total += 1
        if not total % 20:
            print total

    for k,v in types.items():
        print enc(str(k) + ": " + str(v))

printAmendmentInfo(a)