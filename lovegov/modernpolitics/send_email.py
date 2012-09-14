########################################################################################################################
########################################################################################################################
#
#           Send Email
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.models import *

# django
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template import Context, loader

#-----------------------------------------------------------------------------------------------------------------------
# email backendery
#-----------------------------------------------------------------------------------------------------------------------
def sendHTMLEmail(subject, email_sender, email_recipients, email_html=None, template=None, dictionary=None):
    if not email_html:
        email_html = render_to_string(template,dictionary)
    emailHelper(subject, email_html, email_sender, email_recipients)

def emailHelper(subject, email_html, email_sender, email_recipients):
    headers = {'From':'LoveGov <' + email_sender + '>'}
    msg = EmailMessage(subject, email_html, email_sender, email_recipients, headers=headers)
    #msg = EmailMessage(subject, email_html, email_sender, email_recipients)
    msg.content_subtype = "html"
    try:
        msg.send()
    except:
        errors_logger.error("email error for [" + subject + "] to " + str(email_recipients))

#-----------------------------------------------------------------------------------------------------------------------
# particular emails
#-----------------------------------------------------------------------------------------------------------------------

def sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template, email_sender="info@lovegov.com", to_email=None):

    if not to_email:
        to_email = user_profile.email

    email_recipients = [to_email]

    email_vals['email_header'] = subject
    email_vals['user_profile'] = user_profile
    email_vals['to_email'] = to_email
    email_vals['domain'] = DOMAIN

    context = Context(email_vals)
    template = loader.get_template(email_template)
    email_html = template.render(context)

    sendHTMLEmail(
        subject = subject,
        email_html = email_html,
        email_sender = email_sender,
        email_recipients = email_recipients)


def sendConfirmationEmail(user_profile, verified=False):
    subject = "LoveGov Confirmation Email"
    email_vals = {'verified':verified}
    email_template = 'emails/lovegov/welcome.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)

def sendPasswordRecoveryEmail(user_profile, recovery_url):
    subject = "LoveGov Password Recovery"
    email_vals = {'recovery_url':recovery_url}
    email_template = 'emails/lovegov/password_change.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)

def sendElectionInviteEmail(to_email, election):
    subject = "You were invited to join LoveGov"
    email_vals = {'election':election}
    email_template = 'emails/lovegov/invite_election.html'
    sendLoveGovEmailHelper(None, subject, email_vals, email_template, to_email=to_email)

def sendScorecardInviteEmail(to_email, scorecard):
    subject = "You were invited to join LoveGov"
    email_vals = {'scorecard':scorecard}
    email_template = 'emails/lovegov/invite_scorecard.html'
    sendLoveGovEmailHelper(None, subject, email_vals, email_template, to_email=to_email)

def sendInviteByEmail(inviter, to_email):
    subject = "You were invited to join LoveGov"
    email_vals = {'inviter':inviter}
    email_template = 'emails/lovegov/invite_by_email.html'
    sendLoveGovEmailHelper(None, subject, email_vals, email_template, to_email=to_email)

def sendLaunchEmail(user_profile):
    subject = "The New LoveGov"
    email_vals = {}
    email_template = 'emails/lovegov/launch.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)




def sendTeamEmail(subject, email_html):
    email_recipients = TEAM_EMAILS
    sendHTMLEmail(
        subject = subject,
        email_html = email_html,
        email_sender = "info@lovegov.com",
        email_recipients = email_recipients)


def sendTeamMessagedRepEmail(messaged):

    vals = {}
    vals['user'] = messaged.user
    vals['message'] = messaged.message
    vals['politician'] = messaged.politician
    vals['phone_number'] = messaged.phone_number

    context = Context(vals)
    template = loader.get_template('emails/team/message_rep.html')
    email_html = template.render(context)

    sendTeamEmail('Someone Messaged Their Rep [to_do]', email_html)


def sendTeamFeedbackEmail(feedback, name):

    vals = {'feedback':feedback.feedback, 'name':name, 'page':feedback.page}

    context = Context(vals)
    template = loader.get_template('emails/team/feedback.html')
    email_html = template.render(context)

    sendTeamEmail('Someone Sent Us Feedback [feedback]', email_html)


def sendTeamClaimedProfileEmail(claimed):

    vals = {'viewer':claimed.user, 'politician':claimed.politician, 'claim_email':claimed.email}

    context = Context(vals)
    template = loader.get_template('emails/team/claimed.html')
    email_html = template.render(context)

    sendTeamEmail('Someone Claimed Their Profile [to_do]', email_html)

#-----------------------------------------------------------------------------------------------------------------------
# batch emails
#-----------------------------------------------------------------------------------------------------------------------
def sendLaunchEmailBatch():
    from lovegov.modernpolitics.helpers import enc
    to_send = UserProfile.objects.filter(ghost=False)
    exclude_ids = range(0,4822)
    to_send = to_send.exclude(id__in=exclude_ids)
    count = 0
    for x in to_send:
        try:
            sendLaunchEmail(x)
            count += 1
            print "+II+ " + enc(x.get_name())
        except:
            print '+EE+ ERROR SENDING TO: ' + enc(x.get_name())
    return count





















#-----------------------------------------------------------------------------------------------------------------------
# Sends an email from an HTML template
#-----------------------------------------------------------------------------------------------------------------------
def sendTemplateEmail(subject, template, dictionary, email_sender, email_recipient):
    """
    Sends an email from an HTML template

    @param subject:              the subject of the email
    @type subject:               string
    @param template:             the template file, located in test/templates/emails
    @type template:              string
    @param dictionary:           a dictionary of values to fill the template with
    @type dictionary:            dictionary
    @param email_sender:         the sender address
    @type email_sender:          string
    @param email_recipient:      the receiving address
    @type email_recipient:       string
    """
    template_reference = 'emails/' + template
    email_html = render_to_string(template_reference,dictionary)
    emailHelper(subject, email_html, email_sender, [email_recipient])

#-----------------------------------------------------------------------------------------------------------------------
# Sends email to registered alpha user.
#-----------------------------------------------------------------------------------------------------------------------
def sendAlphaTesterEmail(name, email, password):
    recipient_list = [email]
    message = "<h3>" + "Hello " + name + ", </h3>"
    message += "<p>" + "username: " + email + "</p>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)


#-----------------------------------------------------------------------------------------------------------------------
# Sends an email telling us someone registered.
#-----------------------------------------------------------------------------------------------------------------------
def sendYayRegisterEmail(user):
    from lovegov.frontend.analytics import userActivity
    time.sleep(60*60)
    message = "<h3>" + user.get_name() + " just registered. LOVEGOV </h3> \n"
    message += userActivity(user)
    send_mail(subject='LoveGov Registration', message=message,
        from_email='info@lovegov.com', recipient_list=YAY_EMAILS)

#-----------------------------------------------------------------------------------------------------------------------
# Sends email to invite user to lovegov
#-----------------------------------------------------------------------------------------------------------------------
def sendInviteEmail(email):
    recipient_list = [email]
    message = "<h3>" + "Welcome to LoveGov. </h3>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)

#-----------------------------------------------------------------------------------------------------------------------
# Sends email to registered alpha user.
#-----------------------------------------------------------------------------------------------------------------------
def sendAlphaTesterEmail(name, email, password):
    recipient_list = [email]
    message = "<h3>" + "Hello " + name + ", </h3>"
    message += "<p>" + "username: " + email + "</p>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)

def sendFBRegisterEmail(name, email, password):
    recipient_list = [email]
    message = "<h3>" + "Hello " + name + ", </h3>"
    message += "<p> welcome to LoveGov! You registered via facebook, and you can connect in the future via facebook or using\
    the username and password below. You can also change your password once you are logged on through the account settings page."
    message += "<p>" + "username: " + email + "</p>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)
