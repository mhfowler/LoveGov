""" sends emails to all developers describing usage of the site that day."""

from lovegov.frontend.views import *
from django.template import Context, loader
from django.core.mail import send_mail

class Session:
    """ for storing an individual users page accesses for a single session """
    def __init__(self):
        self.pa = []
    def getSessionStart(self):
        return self.pa[0].when
    def processPA(self):
        self.pa.sort(key=lambda item: item.when)
        previous = None
        for x in self.pa:
            if previous:
                duration = (x.when - previous.when).total_seconds()
                if duration < (60*60):
                    previous.duration = int(duration)
                else:
                    previous.duration = None
            previous = x

    def getNumPA(self):
        return len(self.pa)
    def getPA(self):
        return self.pa

def dailySummaryEmail(days=0):
    vals = {}

    now = datetime.datetime.now() - datetime.timedelta(days=days)
    delta = datetime.timedelta(hours=24)
    today = now - delta

    pa = PageAccess.objects.filter(when__gt=today)

    accessed = {}
    for x in pa:
        user = x.user
        alias = user.alias
        if not alias in accessed:
            accessed[alias] = {'user':user, 'session':Session()}
        accessed[alias]['session'].pa.append(x)

    accessed_list = []
    for k,v in accessed.items():
        accessed_list.append(v)

    accessed_list.sort(key=lambda item: item['session'].getNumPA())
    for x in accessed_list:
        x['session'].processPA()

    vals['accessed'] = accessed_list

    registered = UserProfile.objects.filter(created_when__gt=today).order_by("created_when")
    vals['registered'] = registered

    context = Context(vals)
    template = loader.get_template('emails/daily_summary/daily_summary.html')
    email = template.render(context)

    return email

################################################# ACTUAL SCRIPT ########################################################

print "*** SENDING DAILY SUMMARY EMAIL ***"
print "args: [email] [days-prior]"

days=0
if len(sys.argv) > 1:
    email = sys.argv[1]
    print "sending to: " + email
    email_recipients = [email]
else:
    email_recipients = DAILY_SUMMARY_EMAILS
if len(sys.argv) == 3:
    days = int(sys.argv[2])

sendHTMLEmail(subject="LoveGov Daily Summary [summary]", email_html=dailySummaryEmail(days=days),
            email_sender="info@lovegov.com", email_recipients=email_recipients)

