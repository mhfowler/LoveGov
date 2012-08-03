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
from lovegov.settings import PROJECT_PATH


# python
import getpass
from xlrd import open_workbook
from pprint import pprint

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
    path = os.path.join(PROJECT_PATH, 'frontend/excel/Presidential_Candidates.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    createPoliticianProfiles(sheet)
    answerQuestions(sheet)

def scriptCreateCongressAnswers(args=None):
    # Open the spreadsheet and shit
    path = os.path.join(PROJECT_PATH, 'frontend/excel/congress.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(3)
    metrics = {}

    # If no congress tag has been made, congress likely doesn't exist.
    if not congress_tag:
        print "No congress OfficeTag found.  Congress probably hasn't been initialized yet.  Aborting answer creation."
        return None

    # For cells in the spreadsheet
    for row in range(1,sheet.nrows):
        for column in xrange(1,sheet.ncols,4):
            #Set amendment and bill to none
            amendment = None
            bill = None

            # If the sheet cell isn't empty
            if sheet.cell(row,column).value == "":
                continue

            # Get the congress number
            congress_num = int(sheet.cell(row,column).value.replace("th",""))
            session = CongressSession.lg.get_or_none(session=congress_num)

            # Get legislation value
            legislation = sheet.cell(row,column+2).value
            # If it's an amendment
            if "Amdt" in legislation:
                # Split the chamber and the number (at .) Format = <chamber>.Amdt.<number>
                legislation = legislation.split('.')
                chamber = legislation[0].lower()
                number = int(legislation[2].strip())

                metricName = "Amdt_" + str(congress_num) + "_" + chamber + "_" + str(number)

                print "Searcing for " + metricName

                # Find the amendment!
                amendment = LegislationAmendment.lg.get_or_none(amendment_type=chamber,congress_session=session,amendment_number=number)
                if not amendment:
                    print "Couldn't find amendment " + metricName
            # Otherwise it's a bill
            else:
                # Make the number non-existent
                legislation = legislation.split('.')
                chamber = ''
                number = -1
                # If the split is length two, format is <chamber>.<number> (e.g. "h.220")
                if len(legislation) == 2:
                    chamber = legislation[0].lower()
                    number = int(legislation[1].strip())
                # If the split is length three, format is <chamber>.<chamber>.<number> (e.g. "h.r.220")
                elif len(legislation) == 3:
                    chamber = (legislation[0] + legislation[1]).lower()
                    number = int(legislation[2].strip())

                metricName = str(congress_num) + "_" + chamber + "_" + str(number)

                print "Searching for " + metricName

                # Find the bill!
                bill = Legislation.objects.filter(congress_session=session,bill_number=number,bill_type=chamber)
                if not bill:
                    print "Couldn't find bill " + metricName

            # Get answer text and value from spreadsheet
            answer_text = sheet.cell(row,0).value
            answer_text = answer_text.encode('utf-8','ignore')
            answer_value = sheet.cell(row,column+3).value
            answer_value = answer_value.encode('utf-8','ignore')
            # Convert answer value
            if answer_value == "Yes":
                answer_value = "+"
            else:
                answer_value = "-"
            # Reset metrics value
            metrics[metricName] = 0

            congress_rolls = None
            # Get votes from the bill or amendment
            if bill:
                congress_rolls = CongressRoll.objects.filter(legislation=bill)
            elif amendment:
                congress_rolls = CongressRoll.objects.filter(amendment=amendment)

            votes = []

            # Collect Votes from Congress Rolls
            for roll in congress_rolls:
                for vote in roll.votes:
                    if vote.votekey == answer_value:
                        votes.append(vote)

            # For all votes
            for vote in votes:
                # Get Voter
                voter = voter.voter

                # Check that answer text was found
                if not answer_text:
                    print "Couldn't find answer text"
                    continue

                # Look for that answer in the database
                answer = Answer.lg.get_or_none(answer_text=answer_text)
                if not answer:
                    print "Couldn't find answer for :: " + answer_text
                    continue

                answer_val = answer.value

                # Look for that question in the database
                question = Question.lg.get_or_none(answers__answer_text=answer_text)
                if not question:
                    print "Couldn't find question"
                    continue

                # Look for that response in the database
                response = UserResponse.lg.get_or_none(responder=voter,question=question)
                if not response: # If it doesn't exist, create it
                    response = UserResponse(responder=voter,question=question,answer_val=answer_val,explanation="")
                    response.autoSave(creator=voter)
                # Otherwise, change the answer
                else:
                    response.answer_val = answer_val
                    response.save()

                metrics[metricName] += 1

                print metricName + " " + str(metrics[metricName])

    pprint(metrics)


def scriptCreateResponses(args=None):
    path = os.path.join(PROJECT_PATH, 'frontend/excel/' + args[0])
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)

    # For all cells in the spreadsheet
    for row in range(1,sheet.nrows):
        for column in range(2,sheet.ncols):
            # Get politician Name
            politician_name = sheet.cell(0,column).value.split(" ")
            print politician_name

            # Look for politician
            politician = UserProfile.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1], politician=True)
            # If they don't exist
            if not politician:
                # Create and print their name and email
                name = politician_name[0] + " " + politician_name[1]
                print "Creating " + name
                email = politician_name[0] + '_' + politician_name[1] + "@lovegov.com"
                password = 'politician'

                # Create user
                politician = createUser(name,email,password)

                # Set some user facts
                politician.user_profile.confirmed = True
                politician.user_profile.politician = True
                politician.user_profile.save()

                #image_path = os.path.join(PROJECT_PATH, 'alpha/static/images/presidentialCandidates/' + politician_name[1].lower() + ".jpg")
                #politician.user_profile.setProfileImage(file(image_path))

                print "Successfully created and confirmed " + name
                politician = politician.user_profile

            # Get and print answer text
            answer_text = sheet.cell(row,column).value
            answer_text = answer_text.encode('utf-8','ignore')
            print answer_text

            # Check for answer text
            if not answer_text:
                print "No answer text"
                continue

            # Find answer
            answer = Answer.lg.get_or_none(answer_text=answer_text)
            if not answer:
                print "Answer not found for text :: " + answer_text
                continue

            answer_val = answer.value
            question = Question.lg.get_or_none(answers__answer_text=answer_text)
            if question:

                response = UserResponse.lg.get_or_none(responder=politician,question=question)
                if not response:
                    response = UserResponse(responder=politician,question=question,answer_val=answer_val,explanation="")
                    response.autoSave(creator=politician)
                else:
                    response.answer_val = answer_val
                    response.explanation = ''
                    response.save()

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