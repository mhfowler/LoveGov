########################################################################################################################
########################################################################################################################
#
#           Alpha
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.scripts.createPresidentialCandidates import answerQuestions
from lovegov.scripts.createPresidentialCandidates import createPoliticianProfiles
from lovegov.modernpolitics.backend import *

# python
import getpass
from xlrd import open_workbook

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
        initializeCongress()
        scriptCreatePresidentialCandidates()
        initializeCommittees()
        initializeLegislation()
        initializeLegislationAmendments()
        initializeVotingRecord()
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
        splash_emails = EmailList.objects.all()
        print "**** PRINTING SPLASH EMAILS ****"
        for x in splash_emails:
            print x.email + " at " + str(x.when)
        beta_emails = EmailList.objects.all()
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
        initializeLoveGov()
    elif tag=='user':
        if len(args) >= 4:
            name = args[1] + " " + args[2]
            email = args[3]
            password = args[4]
            control = createUser(name=name, email=email, password=password)
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
            createAlphaUser(name=name, email=email)
            print "**** CREATED ALPHA USER ****"
            print "name: " + name
            print "email: " + email
        else:
            print "invalid command: user tag requires 3 additional arguments <first_name> <last_name> <email>"
    elif tag=='testdata':
        initializeTopics()
        initializeQ()
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
            mailingList = EmailList.objects.all()
            for user in mailingList:
                message_html = render_to_string('emails/' + emailFile)
                msg = EmailMessage(subject, message_html ,from_email='info@lovegov.com',to=[user.email])
                msg.content_subtype = "html"
                msg.send()
        elif tag=='test':
            vals = {'firstname':'clay','email':'clayton_dunwell@brown.edu','password':'qlkqwel23'}
            sendTemplateEmail('Welcome to LoveGov Alpha', emailFile, vals, 'info@lovegov.com','clay@lovegov.com')
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
        password=generateRandomPassword(8)
        print ("email: " + email)
        print("first: "+first_name)
        print("last: "+last_name)
        print("pass: "+password)
        createUser(name, email, password)
        vals = {'firstname':first_name,'email':email,'password':password}
        sendTemplateEmail("Welcome to LoveGov Alpha",'alphaInvite.html',vals,'team@lovegov.com',email)


#-----------------------------------------------------------------------------------------------------------------------
#   generates Politician objects for each candidates in spreadsheet
#   answers questions for them
#-----------------------------------------------------------------------------------------------------------------------
def scriptCreatePresidentialCandidates(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'frontend/excel/Presidential_Candidates.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    createPoliticianProfiles(sheet)
    answerQuestions(sheet)

def scriptCreateCongressAnswers(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'frontend/excel/congress.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(3)
    metrics = {}

    for row in range(1,sheet.nrows):
        for column in xrange(1,sheet.ncols,4):
            amendment = None
            bill = None

            if sheet.cell(row,column).value != "":
                congress_num = int(sheet.cell(row,column).value.replace("th",""))
                session = CongressSession.lg.get_or_none(session=congress_num)

                legislation = sheet.cell(row,column+2).value
                if "Amdt" in legislation:
                    legislation = legislation.split('.')
                    chamber = legislation[0].lower()
                    number = int(legislation[2].strip())

                    metricName = str(congress_num) + "_" + chamber + "_" + str(number)

                    print str(congress_num) + "_" + chamber + "_" + str(number) + "_Amendment"

                    amendment = LegislationAmendment.lg.get_or_none(amendment_type=chamber,congress_session=session,amendment_number=number)
                    if not amendment:
                        print "Couldn't find amendment " + metricName

                else:
                    legislation = legislation.split('.')
                    chamber = ''
                    number = -1

                    if len(legislation) == 2:
                        chamber = legislation[0].lower()
                        number = int(legislation[1].strip())

                    elif len(legislation) == 3:
                        chamber = (legislation[0] + legislation[1]).lower()
                        number = int(legislation[2].strip())

                    metricName = str(congress_num) + "_" + chamber + "_" + str(number)

                    print "Searching for " + metricName

                    bill = Legislation.objects.filter(congress_session=session,bill_number=number,bill_type=chamber)
                    if not bill:
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

                for congressman in UserProfile.objects.filter(elected_official=True):
                    congress_vote = None

                    if bill:
                        congress_vote = CongressVote.lg.get_or_none(voter=congressman,votekey=answer_value,roll__legislation=bill)

                    elif amendment:
                        congress_vote = CongressVote.lg.get_or_none(voter=congressman,votekey=answer_value,roll__amendment=amendment)

                    if congress_vote:
                        if answer_text:

                            answer = Answer.lg.get_or_none(answer_text=answer_text)
                            if answer:
                                answer_val = answer.value

                                question = Question.lg.get_or_none(answers__answer_text=answer_text)
                                if question:
                                    response = UserResponse.lg.get_or_none(responder=congressman,question=question)

                                    if not response:
                                        response = UserResponse(responder=congressman,question=question,answer_val=answer_val,explanation="")
                                        response.autoSave(creator=congressman)

                                    else:
                                        response.answer_val = answer_val
                                        response.save()

                                    #print "WORKED FOR " + electedofficial.get_name().encode('utf-8','ignore')
                                    metrics[metricName]+= 1
                                else:
                                    print "Question doesn't exist"
                            else:
                                print "Couldn't find answer"
                        else:
                            print "Couldn't find answer text"

                print metricName + " " + str(metrics[metricName])
    print metrics


def scriptCreateResponses(args=None):
    path = os.path.join(settings.PROJECT_PATH, 'frontend/excel/' + args[0])
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    for row in range(1,sheet.nrows):
        for column in range(2,sheet.ncols):
            politician_name = sheet.cell(0,column).value.split(" ")
            print politician_name
            politician = UserProfile.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1], politician=True)
            if not politician:

                name = politician_name[0] + " " + politician_name[1]
                print "Creating " + name
                email = politician_name[0] + '_' + politician_name[1] + "@lovegov.com"
                password = 'politician'

                politician = createUser(name,email,password)

                politician.user_profile.confirmed = True
                politician.user_profile.politician = True
                politician.user_profile.save()

                #image_path = os.path.join(settings.PROJECT_PATH, 'alpha/static/images/presidentialCandidates/' + politician_name[1].lower() + ".jpg")
                #politician.user_profile.setProfileImage(file(image_path))

                print "Successfully created and confirmed " + name
                politician = politician.user_profile

            answer_text = sheet.cell(row,column).value
            answer_text = answer_text.encode('utf-8','ignore')
            print answer_text

            if answer_text and Answer.objects.filter(answer_text=answer_text).exists():
                answer = Answer.objects.get(answer_text=answer_text)
                answer_val = answer.value

                if Question.objects.filter(answers__answer_text=answer_text).exists():
                    question = Question.objects.get(answers__answer_text=answer_text)
                    response = UserResponse(responder=politician,question=question,answer_val=answer_val,explanation="")
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
        removeUser(email)

def scriptSendAllFeedback(args):
    for feedback in Feedback.objects.all():
        vals = {'text':feedback.feedback}
        for team_member in TEAM_EMAILS:
            sendTemplateEmail("LoveGov Feedback",'feedback.html',vals,"team@lovegov.com",team_member)

########################################################################################################################
#
# Start of actual script.
#
########################################################################################################################
# save the fact that script was run
command = ''
for x in sys.argv:
    command += x + ' '
to_save = Script(command=command, user=getpass.getuser())
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