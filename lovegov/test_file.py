""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.views import *
from lovegov.frontend.analytics import *

print "*** SENDING DAILY SUMMARY EMAIL ***"
print "args: [email] [days-ago-start] [how-many-days]"

days_ago=1
days_for=0
email_recipients = ['max_fowler@brown.edu']

email_html = str(dailySummaryEmail(days_ago, days_for)).replace("^M", "")

#context = Context({})
#template = loader.get_template('emails/daily_summary/test.html')
#email_html = template.render(context)

attachment_file = open('/tmp/daily_summary_html.html', 'w')
attachment_file.write(email_html)
attachment_file.close()

attachment_file = open('/tmp/daily_summary_html.html', 'r')
attachment_dict = {'file':attachment_file, 'name':'daily_summary.html'}

email_html = "<p> Hey guys it's daily summary time! </p>"

sendHTMLEmail(subject="LoveGov Daily Summary [summary]", email_html=email_html,
    email_sender="info@lovegov.com", email_recipients=email_recipients, email_attachments=[attachment_dict])

