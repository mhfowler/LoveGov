""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.views import *
from lovegov.frontend.analytics import *

print "*** SENDING DAILY SUMMARY EMAIL ***"
print "args: [email] [days-ago-start] [how-many-days]"

days_ago=1
days_for=0
if len(sys.argv) > 1:
    email = sys.argv[1]
    print "sending to: " + email
    email_recipients = [email]
else:
    email_recipients = DAILY_SUMMARY_EMAILS
if len(sys.argv) == 3:
    days_ago = int(sys.argv[2])
if len(sys.argv) == 4:
    days_for= int(sys.argv[3])

email_html = email_html=dailySummaryEmail(days_ago, days_for)

TMP_DEBUG = True
if TMP_DEBUG:
    print email_html

sendHTMLEmail(subject="LoveGov Daily Summary [summary]", email_html=email_html,
            email_sender="info@lovegov.com", email_recipients=email_recipients)

