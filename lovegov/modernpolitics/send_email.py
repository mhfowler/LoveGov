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

from xlrd import open_workbook
from boto.exception import BotoServerError

# django
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template import Context, loader

#-----------------------------------------------------------------------------------------------------------------------
# email backendery
#-----------------------------------------------------------------------------------------------------------------------
def sendHTMLEmail(subject, email_sender, email_recipients, email_html=None, template=None, dictionary=None, email_attachments=None):
    if not email_html:
        email_html = render_to_string(template,dictionary)
    emailHelper(subject, email_html, email_sender, email_recipients, email_attachments=email_attachments)

def emailHelper(subject, email_html, email_sender, email_recipients, email_attachments=None):
    email_html = email_html.encode('ascii', 'ignore')
    headers = {'From':'LoveGov <' + email_sender + '>'}
    msg = EmailMessage(subject, email_html, email_sender, email_recipients, headers=headers)
    msg.content_subtype = "html"

    if email_attachments:
        for attachment_dict in email_attachments:
            file = attachment_dict['file']
            file_name= attachment_dict['name']
            msg.attach(file.name, file.read(), "text/html")

    try:
        msg.send()
    except Exception, e:
        import traceback, os.path
        top = traceback.extract_stack()[-1]
        print ", ".join([type(e).__name__, os.path.basename(top[0]), str(top[1])])
        errors_logger.error("email error for [" + subject + "] to " + str(email_recipients))

#-----------------------------------------------------------------------------------------------------------------------

# particular emails
#-----------------------------------------------------------------------------------------------------------------------

def sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template, email_sender=u'info@lovegov.com', to_email=None):

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

def sendInviteByEmail(inviter, to_email, msg):
    subject = "You were invited to join LoveGov"
    email_vals = {'inviter':inviter, 'msg': msg}
    email_template = 'emails/lovegov/invite_by_email.html'
    sendLoveGovEmailHelper(None, subject, email_vals, email_template, to_email=to_email)

def sendLaunchEmail(user_profile):
    subject = u'The New LoveGov'
    email_vals = {}
    email_template = 'emails/lovegov/launch.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)


def sendNewLoveGovEmail(user_profile):
    subject = u'Same LoveGov, New Look'
    email_vals = {}
    email_template = 'emails/lovegov/new_lovegov.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)

def sendNewLoveGovEmails():
    users = UserProfile.objects.filter(ghost=False)
    for x in users:
        if not x.checkEmailSubscription("A"):
            print "+XX+ not subscribed: " + enc(x.get_name())
        else:
            sendNewLoveGovEmail(x)
            print enc("+II+ sent email to: " + x.get_name())



def sendWeeklyDigestEmail(user_profile):

    from lovegov.frontend.views_helpers import getWeeklyDigestQuestions, getWeeklyDigestNews

    if not user_profile.checkEmailSubscription("W"):
        print "+XX+ not subscribed: " + enc(user_profile.get_name())
        return False
    else:
        print "sending weekly digest to: " + enc(user_profile.get_name())

    subject = "LoveGov Weekly Digest"

    now = datetime.datetime.now()
    delta = datetime.timedelta(days=7)
    time_start = now - delta
    time_end = now

    popular_questions = getWeeklyDigestQuestions(time_start, time_end, user_profile)[:5]
    for x in popular_questions:
        x.the_link = DOMAIN + x.get_url()
        user_profile.addDigestedContent(x)

    popular_news = getWeeklyDigestNews(time_start, time_end, user_profile)[:5]
    for x in popular_news:
        x.the_link = x.link
        user_profile.addDigestedContent(x)

    email_vals = {'popular_questions':popular_questions, 'popular_news':popular_news}
    email_template = 'emails/lovegov/weekly_digest/weekly_digest.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)


def sendSpecialEmail(user_profile):

    from lovegov.frontend.views_helpers import getWeeklyDigestQuestions, getWeeklyDigestNews

    if not user_profile.checkEmailSubscription("W"):
        print "+XX+ not subscribed: " + enc(user_profile.get_name())
        return False
    else:
        print "sending weekly digest to: " + enc(user_profile.get_name())

    subject = "Two questions about the election"

    email_vals = {}
    email_template = 'emails/lovegov/special_email.html'
    sendLoveGovEmailHelper(user_profile, subject, email_vals, email_template)

def sendSpecialEmails():
    u = UserProfile.objects.filter(ghost=False)
    for x in u:
        sendSpecialEmail(x)

def sendWeeklyDigestEmails():
    u = UserProfile.objects.filter(ghost=False)
    for x in u:
        sendWeeklyDigestEmail(x)

def isUnsubscribedToEmail(email):
    user = UserProfile.lg.get_or_none(email=email)
    if user:
        return not user.checkEmailSubscription("A")
    else:
        return UnsubscribedToEmail.lg.get_or_none(email=email)


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
    exclude_ids = range(0,4815)
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




def sendStudentGroupInviteEmail(xlsfile, sheet):
    from_where = "national_email_oct01"
    path = os.path.join(PROJECT_PATH, xlsfile)
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(sheet)
    num = 0
    for row in range(1,sheet.nrows):
    #for row in range(100,103):
        student_name = sheet.cell(row,4).value
        student_affiliation = sheet.cell(row,3).value
        student_email = sheet.cell(row,0).value
        #student_email = 'jsgreenf@gmail.com'

        to_lovegov = toLoveGov(who=student_email, from_where=from_where)
        to_lovegov.save()
        email_code = to_lovegov.id

        vals = {'student_name': student_name, 'student_affiliation': student_affiliation, 'email_code':email_code}
        email_message = render_to_string('emails/lovegov/student_group_invite.html',vals)
        email_message = enc(email_message)
        try:
            msg = EmailMessage('LoveGov', email_message, 'joschka@lovegov.com', [student_email])
            msg.content_subtype = "html"
            msg.send()
        except BotoServerError:
            print '+WW+ Something went wrong with sending the email to : ' + enc(student_email)
        try:
            print 'Name: %s, Affiliation: %s, Email: %s' % (student_name, student_affiliation, student_email)
        except:
            print 'Something went wrong printing but the email should have sent...'
        num += 1
    return num





def sendGroupGeneralInviteEmail(xlsfile, sheet):
    from_where = "massachu_email_oct1"
    path = os.path.join(PROJECT_PATH, xlsfile)
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(sheet)
    num = 0
    for row in range(1,sheet.nrows):
    #for row in range(30,33):
        group_affiliation = sheet.cell(row,1).value
        group_email = sheet.cell(row,0).value
        #group_email = 'jsgreenf@gmail.com'

        to_lovegov = toLoveGov(who=group_email, from_where=from_where)
        to_lovegov.save()
        email_code = to_lovegov.id

        vals = {'group_affiliation': group_affiliation, 'email_code':email_code}

        email_message = render_to_string('emails/lovegov/group_general_invite.html',vals)
        email_message = enc(email_message)
        try:
            msg = EmailMessage('LoveGov', email_message, 'joschka@lovegov.com', [group_email])
            msg.content_subtype = "html"
            msg.send()
        except BotoServerError:
            print '+WW+ Something went wrong with sending the email to : ' + enc(group_email)
        try:
            print 'Affiliation: %s, Email: %s' % (group_affiliation, group_email)
        except:
            print 'Something went wrong printing but the email should have sent...'
        num += 1
    return num





def sendProfessorInviteEmail(xlsfile, sheet):
    from_where = "massachu_email_oct1"
    path = os.path.join(PROJECT_PATH, xlsfile)
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(sheet)
    num = 0
    for row in range(1,sheet.nrows):
    #for row in range(1,3):
        professor_name = sheet.cell(row,0).value
        professor_last_name = professor_name.split(' ')[-1]
        professor_affiliation = sheet.cell(row,1).value
        professor_email = sheet.cell(row,2).value
        #professor_email = 'jsgreenf@gmail.com'

        to_lovegov = toLoveGov(who=professor_email, from_where=from_where)
        to_lovegov.save()
        email_code = to_lovegov.id

        vals = {'professor_name': professor_name, 'professor_affiliation': professor_affiliation, 'email_code':email_code}

        email_message = render_to_string('emails/lovegov/professor_invite.html',vals)
        email_message = enc(email_message)
        try:
            msg = EmailMessage('LoveGov', email_message, 'joschka@lovegov.com', [professor_email])
            msg.content_subtype = "html"
            msg.send()
        except BotoServerError:
            print '+WW+ Something went wrong with sending the email to : ' + enc(professor_email)
        try:
            print 'Name: %s, Affiliation: %s, Email: %s' % (professor_name, professor_affiliation, professor_email)
        except:
            print 'Something went wrong printing but the email should have sent...'
        num += 1
    return num




def sendBrownProfessorInviteEmail():
    path = os.path.join(PROJECT_PATH, 'frontend/excel/AcademiaBundle_RI.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(2)
    num = 0
    for row in range(1,sheet.nrows):
        professor_name = sheet.cell(row,0).value
        professor_last_name = professor_name.split(' ')[-1]
        professor_affiliation = sheet.cell(row,1).value
        professor_department = professor_affiliation.split('Brown University ')[-1]
        professor_email = sheet.cell(row,2).value
        email_message = render_to_string('emails/lovegov/brown_professor_invite.html',{'professor_name': professor_last_name, 'professor_affiliation': professor_department})
        send_mail('LoveGov', email_message, 'joschka@lovegov.com', [professor_email])
        print 'Name: %s, Affiliation: %s, Email: %s' % (professor_name, professor_affiliation, professor_email)
        num += 1
    return num













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
