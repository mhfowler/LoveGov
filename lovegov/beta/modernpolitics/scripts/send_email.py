########################################################################################################################
#   Sends email to all members of team. [for testing]
#
########################################################################################################################

import sys
import getpass
import datetime
from lovegov.beta.modernpolitics import backend
from lovegov.beta.modernpolitics.models import Script
from lovegov.beta.modernpolitics.models import EmailList
from django.core.mail import send_mail

# save the fact that script was run
command = ''
for x in sys.argv:
    command += x + ' '
to_save = Script(command=command, user=getpass.getuser())
to_save.save()
time = datetime.datetime.now()

print '\n"' + command + '" ' + " at " + str(time)
# send email
send_mail(subject='Test Email', message="Happy Valentine's day from Lovegov.",
    from_email='info@lovegov.com', recipient_list=['max_fowler@brown.edu'])




