#!/usr/bin/env python

""" sends emails to all developers describing usage of the site that week."""

from lovegov.frontend.views import *
from lovegov.frontend.analytics import *

print "*** SENDING WEEKLY SUMMARY EMAIL ***"
print "args: [email]"

if len(sys.argv) > 1:
    email = sys.argv[1]
    print "sending to: " + email
    email_recipients = [email]
else:
    email_recipients = DAILY_SUMMARY_EMAILS

if len(sys.argv) > 2:
    days = int(sys.argv[2])
else:
    days = 7

today = datetime.datetime.today()
today_now = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=4)
delta = datetime.timedelta(days=1)
time_start = today_now - delta
time_end = today_now
for x in range(1,days+1):
    print "sending usage summary for " + str(x) + " days ago"
    sendHTMLEmail(subject="LoveGov Daily Summary [summary]", email_html=summaryEmail(time_start, time_end),
        email_sender="info@lovegov.com", email_recipients=email_recipients)
    time_start -= delta
    time_end -= delta

