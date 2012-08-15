from lovegov.frontend.views import *
from django.template import Context, loader
from django.core.mail import send_mail

print "*** SENDING SPECIAL EMAIL ***"

if len(sys.argv) > 1:
    email = sys.argv[1]
    print "sending to: " + email
    email_recipients = [email]
else:
    email_recipients = DAILY_SUMMARY_EMAILS

users = UserProfile.objects.filter(developer=True)

for u in users:
    vals = {'name':u.first_name}
    context = Context(vals)
    template = loader.get_template('emails/vicepresidential.html')
    email_html = template.render(context)
    email_recipient = [u.email]
    sendHTMLEmail(subject="LoveGov VicePresidential Match", email_html=email_html,
    email_sender="team@lovegov.com", email_recipients=email_recipients)