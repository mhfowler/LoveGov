__author__ = 'maxfowler'

from lovegov.frontend.views import *
from django.template import Context, loader

subject = "Registration Email"

email_recipients = ['max_fowler@brown.edu']
email_sender="info@lovegov.com"

context = Context({'email_header':'Welcome to Lovegov'})
template = loader.get_template('emails/lovegov/registration.html')
email_html = template.render(context)

sendHTMLEmail(
    subject = subject,
    email_html = email_html,
    email_sender = email_sender,
    email_recipients = email_recipients )



