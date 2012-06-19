
# lovegov
from lovegov.modernpolitics.models import UserProfile
from lovegov.modernpolitics import send_email

########################################################################################################################

# XLRD Import
# Project Imports
# Python Imports

########################################################################################################################

# STATIC VARIABLES
EMAIL_SUBJECT = "Welcome to LoveGov Alpha"
EMAIL_SENDER = 'info@lovegov.com'
EMAIL_TEMPLATE = 'alphaInvite.html'
PASSWORD_LENGTH = 8

def createAlphaUsers(sheet):
    for row in range(2,sheet.nrows):
        firstname = sheet.cell(row,0).value
        lastname = sheet.cell(row,1).value
        name = firstname + " " + lastname
        email_recipient = sheet.cell(row,2).value
        password = betabackend.generateRandomPassword(PASSWORD_LENGTH)
        if not UserProfile.objects.filter(username=email_recipient).exists():
            betabackend.createUser(name, email_recipient, password)
            print name + " successfully added to Alpha users, e-mailing them..."
            vals = {'firstname':firstname,'email':email_recipient,'password':password}
            send_email.sendTemplateEmail(EMAIL_SUBJECT,EMAIL_TEMPLATE,vals,EMAIL_SENDER,email_recipient)
    print "All alpha users were successfully initialized and sent e-mails."

########################################################################################################################
########################################################################################################################


