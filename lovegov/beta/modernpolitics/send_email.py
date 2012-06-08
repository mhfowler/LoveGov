__author__ = 'CLAY'
########################################################################################################################

# Django Imports
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail

########################################################################################################################

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
    msg = EmailMessage(subject, email_html, email_sender, [email_recipient])
    msg.content_subtype = "html"
    try:
        msg.send()
    except:
        print "Invalid e-mail for user " + email_recipient

#-----------------------------------------------------------------------------------------------------------------------
# Sends confirmation email to user.
#-----------------------------------------------------------------------------------------------------------------------
def sendConfirmationEmail(userProfile):
    recipient_list = [userProfile.email]
    # send email
    send_mail(subject='Welcome to LoveGov.', message="TODO: how to actually send nice emails.",
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

#-----------------------------------------------------------------------------------------------------------------------
# Sends email of password change
#-----------------------------------------------------------------------------------------------------------------------
def sendPasswordChangeEmail(django_user, password):
    recipient_list = [django_user.email]
    message = "<h3>" + "Hello " + django_user.first_name + ", </h3>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='LoveGov password change.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)