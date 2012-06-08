########################################################################################################################

# Internal
from lovegov.beta.modernpolitics import models as betamodels
from lovegov.beta.modernpolitics import backend as betabackend
from lovegov.beta.modernpolitics import send_email
from lovegov.beta.modernpolitics import constants as betaconstants
from lovegov.alpha.splash.createPresidentialCandidates import answerQuestions
from lovegov.alpha.splash.createPresidentialCandidates import createPoliticianProfiles
from lovegov.alpha.splash.createAlphaUsers import createAlphaUsers

# Python
import sys
import getpass
import datetime
from xlrd import open_workbook
import traceback
import os


# Django
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


########################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------
# Switch method which calls correct script.
#-----------------------------------------------------------------------------------------------------------------------
def runScript(operation, args):
    operations = ['print', 'init','createCandidates']
    if operation == 'print':
        scriptPrint(args)
    elif operation == 'init':
        scriptInitialize(args)
    elif operation == "email":
        scriptEmail(args)
    elif operation == "addAlphaUser":
        scriptAddAlphaUser(args)
    elif operation =="removeAlphaUser":
        scriptRemoveAlphaUser(args)
    elif operation == "createCandidates":
        scriptCreatePresidentialCandidates(args)
    elif operation == "sendAllFeedback":
        scriptSendAllFeedback(args)
    elif operation == "initializeCongress":  # THIS SCRIPT TAKES A VERY LONG TIME TO RUN - DO NOT CALL FREQUENTLY
        betabackend.initializeCongress()
        scriptCreatePresidentialCandidates()
        scriptCreateRhodeIsland()
        betabackend.initializeCommittees()
        betabackend.initializeLegislation()
        betabackend.initializeLegislationAmendments()
        betabackend.initializeVotingRecord()
        scriptCreateCongressAnswers()
    elif operation == "createCongressResponses":
        scriptCreateCongressAnswers(args)
    elif operation == "createResponses":
        scriptCreateResponses(args)
    # prints valid scripts
    elif operation == 'help':
        to_print = 'acceptable operations: help, '
        for t in operations:
            to_print += t + ', '
        print to_print
    # else invalid operations
    else:
        print "invalid command: '" + operation + "' is not an operation tag. try help."


#-----------------------------------------------------------------------------------------------------------------------
#   print script
#-----------------------------------------------------------------------------------------------------------------------
def scriptPrint(args):
    tags = ['emails']
    tag = args[0]
    if tag=='emails':
        splash_emails = betamodels.EmailList.objects.all()
        print "**** PRINTING SPLASH EMAILS ****"
        for x in splash_emails:
            print x.email + " at " + str(x.when)
        beta_emails = betamodels.EmailList.objects.all()
        print "**** PRINTING BETA EMAILS ****"
        for x in beta_emails:
            print x.email + " at " + str(x.when)
    elif tag == 'help':
        to_print = 'acceptable tags: help, '
        for t in tags:
            to_print += t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag. try help."

#-----------------------------------------------------------------------------------------------------------------------
#   init script
#-----------------------------------------------------------------------------------------------------------------------
def scriptInitialize(args):
    tags = ['lovegov', 'user', 'alphauser', 'testdata']
    tag = args[0]
    if tag=='lovegov':
        betabackend.initializeLoveGov()
    elif tag=='user':
        if len(args) >= 4:
            name = args[1] + " " + args[2]
            email = args[3]
            password = args[4]
            control = betabackend.createUser(name=name, email=email, password=password)
            user_prof = control.user_profile
            user_prof.confirmed = True
            user_prof.save()
            print "**** CREATED USER ****"
            print "name: " + name
            print "email: " + email
            print "pswd: " + password
        else:
            print "invalid command: user tag requires 4 additional arguments <first_name> <last_name> <email> <password>"
    elif tag=='alphauser':
        if len(args) >= 3:
            name = args[1] + " " + args[2]
            email = args[3]
            betabackend.createAlphaUser(name=name, email=email)
            print "**** CREATED ALPHA USER ****"
            print "name: " + name
            print "email: " + email
        else:
            print "invalid command: user tag requires 3 additional arguments <first_name> <last_name> <email>"
    elif tag=='testdata':
        betabackend.initializeTopics()
        betabackend.initializeQ()
    elif tag == 'help':
        to_print = 'acceptable tags: help, '
        for t in tags:
            to_print += t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag. try help."


#-----------------------------------------------------------------------------------------------------------------------
#   email script
#       args[0]: recipient group
#       args[1]: subject of email
#       args[2]: html file located in test/templates/emails
#-----------------------------------------------------------------------------------------------------------------------
def scriptEmail(args):
    tags = ['alpha','beta', 'splash','user','team','test']
    if len(args) >= 1 and args[0]=='help':
        print "This script required three position arguments of the form: email <group> <subject> <filename>"
        print "<group>: alpha, beta, splash, user, team, test"
        print "<subject>: the subject line of the email you are sending. example: 'URGENT GUYS'"
        print "<filename>: reference to HTML file located in test/templates/emails.  example: alphaInvite.html"
    elif len(args)<2 or len(args)>3:
        print "Not enough or too many arguments for email.  Try 'email help' for correct usage of this script."
    else:
        tag = args[0]
        subject = args[1]
        emailFile = args[2]
        if tag=='splash':
            mailingList = betamodels.EmailList.objects.all()
            for user in mailingList:
                message_html = render_to_string('emails/' + emailFile)
                msg = EmailMessage(subject, message_html ,from_email='info@lovegov.com',to=[user.email])
                msg.content_subtype = "html"
                msg.send()
        elif tag=='test':
            dict = {'firstname':'clay','email':'clayton_dunwell@brown.edu','password':'qlkqwel23'}
            send_email.sendTemplateEmail('Welcome to LoveGov Alpha', emailFile, dict, 'info@lovegov.com','clay@lovegov.com')
        else:
            print "invalid command: '" + tag + "' is not an accepted tag. try help."


#-----------------------------------------------------------------------------------------------------------------------
#   add alpha user script
#       args[0]: recipient group
#       args[1]: subject of email
#       args[2]: html file located in test/templates/emails
#-----------------------------------------------------------------------------------------------------------------------
def scriptAddAlphaUser(args):
    if len(args) >= 1 and args[0]=='help':
        print "This script requires four position arguments of the form: addAlphaUser <first_name> <last_name> <email>"
    elif len(args)<2 or len(args)>4:
        print "Not enough or too many arguments for email.  Try 'email help' for correct usage of this script."
    else:
        first_name= args[0]
        last_name = args[1]
        name = first_name + " " + last_name
        email = args[2]
        password=betabackend.generateRandomPassword(8)
        print ("email: " + email)
        print("first: "+first_name)
        print("last: "+last_name)
        print("pass: "+password)
        betabackend.createUser(name, email, password)
        dict = {'firstname':first_name,'email':email,'password':password}
        send_email.sendTemplateEmail("Welcome to LoveGov Alpha",'alphaInvite.html',dict,'team@lovegov.com',email)



#-----------------------------------------------------------------------------------------------------------------------
#   generates Politician objects for each candidates in spreadsheet
#   answers questions for them
#-----------------------------------------------------------------------------------------------------------------------
def scriptCreatePresidentialCandidates(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'alpha/excel/Presidential_Candidates.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    createPoliticianProfiles(sheet)
    answerQuestions(sheet)

def scriptCreateCongressAnswers(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'alpha/excel/congress.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(3)
    metrics = {}
    for row in range(1,sheet.nrows):
        for column in xrange(1,sheet.ncols,4):
            amendment = None
            bill = None
            if sheet.cell(row,column).value != "":
                congress = int(sheet.cell(row,column).value.replace("th",""))
                legislation = sheet.cell(row,column+2).value
                if "Amdt" in legislation:
                    legislation = legislation.split('.')
                    chamber = legislation[0].lower()
                    number = int(legislation[2].strip())
                    metricName = str(congress) + "_" + chamber + "_" + str(number)
                    print str(congress) + "_" + chamber + "_" + str(number) + "_Amendment"
                    if betamodels.LegislationAmendment.objects.filter(chamber=chamber,session=congress,number=number).exists():
                        amendment = betamodels.LegislationAmendment.objects.get(chamber=chamber,session=congress,number=number)
                    else:
                        print "Couldn't find amendment " + metricName
                else:
                    legislation = legislation.split('.')
                    if len(legislation) == 2:
                        chamber = legislation[0].lower()
                        number = int(legislation[1].strip())
                    elif len(legislation) == 3:
                        chamber = (legislation[0] + legislation[1]).lower()
                        number = int(legislation[2].strip())
                    metricName = str(congress) + "_" + chamber + "_" + str(number)
                    print "Searching for " + metricName
                    if betamodels.Legislation.objects.filter(bill_session=congress,bill_number=number,bill_type=chamber).exists():
                        bill = betamodels.Legislation.objects.get(bill_session=congress,bill_number=number,bill_type=chamber)
                    else:
                        print "Couldn't find bill " + metricName
                answer_text = sheet.cell(row,0).value
                answer_text = answer_text.encode('utf-8','ignore')
                answer_value = sheet.cell(row,column+3).value
                answer_value = answer_value.encode('utf-8','ignore')
                if answer_value == "Yes":
                    answer_value = "+"
                else:
                    answer_value = "-"
                metrics[metricName] = 0
                for electedofficial in betamodels.ElectedOfficial.objects.all():
                    votingrecord = None
                    if bill is not None and betamodels.VotingRecord.objects.filter(electedofficial=electedofficial,bill=bill,amendment=None).exists():
                        votingrecord = betamodels.VotingRecord.objects.filter(electedofficial=electedofficial,bill=bill,amendment=None)[0]
                    elif amendment is not None and betamodels.VotingRecord.objects.filter(electedofficial=electedofficial,amendment=amendment).exists():
                        votingrecord = betamodels.VotingRecord.objects.filter(electedofficial=electedofficial,amendment=amendment)[0]
                    if votingrecord is not None:
                        if answer_text and betamodels.Answer.objects.filter(answer_text=answer_text).exists():
                            if votingrecord.votekey == answer_value:
                                answer = betamodels.Answer.objects.get(answer_text=answer_text)
                                answer_val = answer.value
                                if betamodels.Question.objects.filter(answers__answer_text=answer_text).exists():
                                    question = betamodels.Question.objects.get(answers__answer_text=answer_text)
                                    response = betamodels.UserResponse(responder=electedofficial,question=question,answer_val=answer_val,explanation="")
                                    response.autoSave(creator=electedofficial)
                                    #print "WORKED FOR " + electedofficial.get_name().encode('utf-8','ignore')
                                    metrics[metricName]+= 1
                                else:
                                    print "Question doesn't exist"
                        else:
                            print "Couldn't find answer"

                print metricName + " " + str(metrics[metricName])
    print metrics


def scriptCreateResponses(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'alpha/excel/' + args[0])
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    for row in range(1,sheet.nrows):
        for column in range(2,sheet.ncols):
            politician_name = sheet.cell(0,column).value.split(" ")
            print politician_name
            politician = betamodels.ElectedOfficial.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1])
            if not politician:
                politician = betamodels.Politician.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1])
                if not politician:
                    name = politician_name[0] + " " + politician_name[1]
                    print "Creating " + name
                    email = politician_name[0] + '_' + politician_name[1] + "@lovegov.com"
                    password = 'politician'
                    politician = betabackend.createUser(name,email,password,type="politician")
                    politician.user_profile.confirmed = True
                    politician.user_profile.save()
                    #image_path = os.path.join(settings.PROJECT_PATH, 'alpha/static/images/presidentialCandidates/' + politician_name[1].lower() + ".jpg")
                    #politician.user_profile.setProfileImage(file(image_path))
                    print "Successfully created and confirmed " + name
                    politician = betamodels.Politician.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1])
            answer_text = sheet.cell(row,column).value
            answer_text = answer_text.encode('utf-8','ignore')
            print answer_text
            if answer_text and betamodels.Answer.objects.filter(answer_text=answer_text).exists():
                answer = betamodels.Answer.objects.get(answer_text=answer_text)
                answer_val = answer.value
                if betamodels.Question.objects.filter(answers__answer_text=answer_text).exists():
                    question = betamodels.Question.objects.get(answers__answer_text=answer_text)
                    response = betamodels.UserResponse(responder=politician,question=question,answer_val=answer_val,explanation="")
                    response.autoSave(creator=politician)
                    print "Successfully answered question for " + politician_name[0]

#-----------------------------------------------------------------------------------------------------------------------
#   add alpha user script
#       args[0]: recipient group
#       args[1]: subject of email
#       args[2]: html file located in test/templates/emails
#-----------------------------------------------------------------------------------------------------------------------
def scriptRemoveAlphaUser(args):
    if len(args) >= 1 and args[0]=='help':
        print "This script requires four position arguments of the form: addAlphaUser <first_name> <last_name> <password> <email>"
    else:
        email = args[0]
        betabackend.removeUser(email)

def scriptSendAllFeedback(args):
    for feedback in betamodels.Feedback.objects.all():
        dict = {'text':feedback.feedback}
        for team_member in betaconstants.TEAM_EMAILS:
            send_email.sendTemplateEmail("LoveGov Feedback",'feedback.html',dict,"team@lovegov.com",team_member)

########################################################################################################################
#
# Start of actual script.
#
########################################################################################################################
# save the fact that script was run
command = ''
for x in sys.argv:
    command += x + ' '
to_save = betamodels.Script(command=command, user=getpass.getuser())
to_save.save()
time = datetime.datetime.now()

print len(sys.argv)
# check at least one tag
if len(sys.argv) < 3:
    print "invalid command: need at least one script and one tag."
else:
    print '\n"' + command + '" ' + " at " + str(time)
    operation = sys.argv[1]
    # call script with passed args
    args = sys.argv[2:]
    runScript(operation, args)