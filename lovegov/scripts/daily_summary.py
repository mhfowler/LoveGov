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

def dailySummaryEmail(days_ago=1, days_for=0):
    vals = {}

    now = datetime.datetime.now()
    time_start = now - datetime.timedelta(days=days_ago)
    if not days_for:
        time_end = now
    else:
        time_end = now + datetime.timedelta(days=days_for)
    vals['time_start'] = time_start
    vals['time_end'] = time_end

    pa = PageAccess.objects.filter(when__gt=time_start, when__lt=time_end)

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

    registered = UserProfile.objects.filter(created_when__gt=time_start).order_by("created_when")
    vals['registered'] = registered

    context = Context(vals)
    template = loader.get_template('emails/daily_summary/daily_summary.html')
    email = template.render(context)

    return email

################################################# ACTUAL SCRIPT ########################################################

print "*** SENDING DAILY SUMMARY EMAIL ***"
print "args: [email] [days-ago-start] [how-many-days]"

days_ago=0
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

sendHTMLEmail(subject="LoveGov Daily Summary [summary]", email_html=dailySummaryEmail(days_ago, days_for),
            email_sender="info@lovegov.com", email_recipients=email_recipients)

