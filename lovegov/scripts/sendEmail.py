from lovegov.frontend.views import *
from django.template import Context, loader
from django.core.mail import send_mail

print "*** SENDING SPECIAL EMAIL ***"

#users = UserProfile.objects.filter(user_type="U")
users = UserProfile.objects.filter(developer=True, first_name="Max")

count = 0
for u in users:
    vals = {'name':u.first_name}
    context = Context(vals)
    template = loader.get_template('emails/vicepresidential.html')
    email_html = template.render(context)
    email_recipients = [u.email]
    sendHTMLEmail(subject="LoveGov VicePresidential Match", email_html=email_html,
    email_sender="team@lovegov.com", email_recipients=email_recipients)
    normal_logger.debug("sent: " + u.get_name())
    count += 1
normal_logger.debug("total sent: " + str(count))
