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
from lovegov.modernpolitics.recalculate import *
from lovegov.base_settings import PROJECT_PATH
from django.template.loader import render_to_string


# python
from xlrd import open_workbook

########################################################################################################################
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



def scriptReparseCongressAnswers():

    print "+SS+ DELETING ALL GHOST RESPONSES"
    deleteAllGhostResponses()

    print "+SS+ REANSWERING QUESTIONS BASED ON LEGISLATION"
    scriptCreateCongressAnswers()

    print "+SS+ REANSWERING SPECIFIC STATES MY MANUAL RESEARCH"
    scriptAnswerFromManualResearch()

    print "finished script!"


def scriptAnswerFromManualResearch():
    specific_answer_files_relative= [
        'HouseCandidateAnswers_CT.xls',
        'HouseCandidateAnswers_MA.xls',
        'HouseCandidateAnswers_ME.xls',
        'HouseCandidateAnswers_NH.xls',
        'HouseCandidateAnswers_RI.xls',
        ]
    for x in specific_answer_files_relative:
        print enc("+SS+ creating responses based on file: " + x)
        scriptCreateResponses([x])



def scriptCreateCongressAnswers(args=None):
    # Open the spreadsheet and shit
    path = os.path.join(PROJECT_PATH, 'frontend/excel/LegislationToAnswers.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)
    metrics = {}
    metrics['overall_metrics'] = overall_metrics = {}

    print "Tags:"
    print "======================"
    print "+EE+ = Error"
    print "+WW+ = Warning"
    print "+II+ = Information"
    print "======================"

    overall_metrics['actions_attempted'] = 0
    overall_metrics['actions_failed'] = 0
    overall_metrics['bills_not_found'] = 0
    overall_metrics['multiple_bills_found'] = 0
    overall_metrics['invalid_votes'] = 0
    overall_metrics['answer_ids_not_found'] = 0
    overall_metrics['questions_not_found'] = 0
    overall_metrics['multiple_questions_found'] = 0
    overall_metrics['answer_actions'] = 0
    overall_metrics['responses_deleted'] = 0
    overall_metrics['questions_deleted'] = 0
    overall_metrics['multiple_congress_rolls_found'] = 0
    overall_metrics['congress_roll_not_found'] = 0

    # For cells in the spreadsheet
    for row in range(1,sheet.nrows):

        action = sheet.cell(row,0).value
        vote = sheet.cell(row,1).value
        legislation =  sheet.cell(row,2).value
        congress_session_text = sheet.cell(row,3).value
        answer_id = sheet.cell(row,6).value
        if answer_id:
            answer_id = int(answer_id)

        overall_metrics['actions_attempted'] += 1

        if action == 'a':

            # Get the congress number
            congress_num = int(congress_session_text.replace("th",""))
            session = CongressSession.lg.get_or_none(session=congress_num)

            if not session:
                print enc("+WW+ Session not found for: " + legislation)
                continue

            bill, amendment, legislation_name = getBillOrAmendment(legislation, session, overall_metrics)
            if not (bill or amendment):
                overall_metrics['bills_not_found'] += 1
                overall_metrics['actions_failed'] += 1
                print enc("+WW+ Couldn't find bill " + legislation)
                continue
            elif bill:
                print enc("+II+ FOUND BILL: " + bill.full_title)
            elif amendment:
                print enc("+II+ FOUND AMENDMENT: " + amendment.description)

            createCongressAnswer(bill, amendment, legislation_name, vote, answer_id, metrics)

        elif action == 'xr':

            creators = UserProfile.objects.filter(ghost=True)
            responses_to_delete = Response.objects.filter(most_chosen_answer_id=answer_id, creator__in=creators)
            for x in responses_to_delete:
                x.delete()
                print enc("deleted response by: " +  x.creator.get_name() + " | to | " + x.question.get_name())
                overall_metrics['responses_deleted'] += 1

        elif action == 'xq':

            answer = Answer.lg.get_or_none(id=answer_id)
            if not answer:
                overall_metrics['answer_ids_not_found'] += 1
                print enc("+WW+ answer id not found: " + str(answer_id))
            else:
                print enc("+II deleting question..")

            questions = answer.question_set.all()
            if not questions:
                overall_metrics['questions_not_found'] += 1
                overall_metrics['actions_failed'] += 1
                print enc("+WW+ TRYING TO DELETE QUESTION: Couldn't find question for answer ID #" + str(answer.id))
                continue
            if questions.count() > 1:
                overall_metrics['multiple_questions_found'] += 1
                print enc("+WW+ Multiple questions found for this answer")

            question = questions[0]

            question.delete()
            print enc("Deleted question: " + question.get_name())
            overall_metrics['questions_deleted'] += 1

    # print overall metrics
    for k,v in overall_metrics.items():
        print enc(str(k) + ": " + str(v))

    return metrics


def getBillOrAmendment(legislation, session, overall_metrics):

    # Get legislation value
    # If it's an amendment
    bill = amendment = None
    if "amdt" in legislation:
        # Split the chamber and the number (at .) Format = <chamber>.amdt.<number>
        legislation = legislation.split('.')
        chamber = legislation[0].lower()
        number = int(legislation[2].strip())

        legislation_name = "amdt_" + str(session.session) + "_" + chamber + "_" + str(number)

        # Find the amendment!
        amendment = LegislationAmendment.objects.filter(amendment_type=chamber,congress_session=session,amendment_number=number)

        if amendment.count() > 1:
            overall_metrics['multiple_bills_found'] += 1
            print enc("+WW+ multiple bills found for " + legislation_name + " : ")
            for x in amendment:
                print enc("- " + x.get_name())

        if amendment:
            amendment = amendment[0]

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

        legislation_name = str(session.session) + "_" + chamber + "_" + str(number)

        # Find the bill!
        bill = Legislation.objects.filter(congress_session=session,bill_number=number,bill_type=chamber)

        if bill.count() > 1:
            overall_metrics['multiple_bills_found'] += 1
            print enc("+WW+ multiple bills found for " + legislation_name + " : ")
            for x in bill:
                print enc("- " + x.get_name())

        if bill:
            bill = bill[0]

    return bill, amendment, legislation_name



def createCongressAnswer(bill, amendment, legislation_name, vote, answer_id, metrics):

        metrics[legislation_name] = num_answers_created = 0
        overall_metrics = metrics['overall_metrics']

        # Convert vote to + or -
        answer_value = "na"
        if vote == "yes":
            answer_value = "+"
        elif vote == "no":
            answer_value = "-"
        elif vote != "":
            overall_metrics['invalid_votes'] += 1
            overall_metrics['actions_failed'] += 1
            print enc("+EE+ Invalid vote for " + legislation_name)
            return False

        congress_rolls = None
        # Get congress rolls from the bill or amendment
        if bill:
            congress_rolls = CongressRoll.objects.filter(legislation=bill, important=True).order_by('datetime')
        elif amendment:
            congress_rolls = CongressRoll.objects.filter(amendment=amendment, important=True).order_by('datetime')

        if not congress_rolls:
            overall_metrics['actions_failed'] += 1
            overall_metrics['congress_roll_not_found'] += 1
            print enc("+EE+ Could not congress roll for == " + legislation_name)
            return False
        elif congress_rolls.count() > 2:
            overall_metrics['multiple_congress_rolls_found'] += 1
            print enc("+EE+ more than one congress roll found for == " + legislation_name)

        # get votes from congress rolls
        votes = getVotesFromRolls(congress_rolls, answer_value=answer_value)

        # For all votes
        for vote in votes:
            # Get Voter
            voter = vote.voter

            # Check that answer text was found
            if not answer_id:
                overall_metrics['answer_ids_not_found'] += 1
                overall_metrics['actions_failed'] += 1
                print "+WW+ Couldn't find answer ID"
                return False

            # Look for that answer in the database
            answer = Answer.lg.get_or_none(id=answer_id)
            if not answer:
                overall_metrics['answer_ids_not_found'] += 1
                overall_metrics['actions_failed'] += 1
                print "+WW+ Couldn't find answer for :: " + str(answer.id)
                return False

            # Look for that question in the database
            questions = answer.question_set.all()
            if not questions:
                overall_metrics['questions_not_found'] += 1
                overall_metrics['actions_failed'] += 1
                print "+WW+ Couldn't find question for answer ID #" + str(answer.id)
                return False
            if questions.count() > 1:
                overall_metrics['multiple_questions_found'] += 1
                print "+WW+ Multiple questions found for this answer"

            # If it's found, take the first item of the query set
            question = questions[0]

            # Answer that shit!
            answerAction(voter,question,"PUB",answer_id)
            print enc("+II+ Successful Answer for " + voter.get_name())
            overall_metrics['answer_actions'] += 1
            num_answers_created += 1
        return True


def scriptCheckPoliticians(args=None):
    path = os.path.join(PROJECT_PATH, 'frontend/excel/' + args[0])
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)

    for column in range(2,sheet.ncols):
        # Get politician Name
        politician_name = sheet.cell(0,column).value.split(" ")

        # Look for politician
        politician = UserProfile.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1], politician=True)
        name = politician_name[0] + " " + politician_name[1]
        # If they don't exist
        if not politician:
            print "Could not find " + name

        else:
            print "Found " + name


def scriptCreateResponses(file):
    path = os.path.join(PROJECT_PATH, 'frontend/excel/' + file)
    print "path: " + path
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(0)

    print "Tags:"
    print "======================"
    print "+EE+ = Error"
    print "+WW+ = Warning"
    print "+II+ = Information"
    print "======================"

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
                print "+WW+ Creating " + name
                email = politician_name[0] + '_' + politician_name[1] + "@lovegov.com"
                password = 'politician'

                # Create user
                politician = createUser(name,email,password)

                # Set some user facts
                politician.user_profile.confirmed = True
                politician.user_profile.politician = True
                politician.user_profile.ghost = True
                politician.user_profile.save()

                #image_path = os.path.join(PROJECT_PATH, 'alpha/static/images/presidentialCandidates/' + politician_name[1].lower() + ".jpg")
                #politician.user_profile.setProfileImage(file(image_path))

                print "+WW+ Successfully created and confirmed " + name
                politician = politician.user_profile

            # Get and print answer text
#            answer_text = sheet.cell(row,column).value
#            answer_text = answer_text.encode('utf-8','ignore')
#            print answer_text
            answer_id = sheet.cell(row,column).value

            # Check for answer text
            if not answer_id:
                print "+WW+ No answer id"
                continue

            # Find answer
            answer = Answer.lg.get_or_none(id=answer_id)
            if not answer:
                print "+WW+ Answer not found for ID #" + str(answer_id)
                continue

            questions = answer.question_set.all()
            if questions:
                question = questions[0]

                # Answer that mamma jamma
                answerAction(politician,question,"PUB",answer_id)

                print "+II+ Successfully answered question for " + politician_name[0]

