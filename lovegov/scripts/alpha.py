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

def scriptCreateCongressAnswers(args=None):
    # Open the spreadsheet and shit
    path = os.path.join(PROJECT_PATH, 'frontend/excel/congress.xls')
    wb = open_workbook(path)
    sheet = wb.sheet_by_index(3)
    metrics = {}

    print "Tags:"
    print "======================"
    print "+EE+ = Error"
    print "+WW+ = Warning"
    print "+II+ = Information"
    print "======================"

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

                # Find the amendment!
                amendment = LegislationAmendment.lg.get_or_none(amendment_type=chamber,congress_session=session,amendment_number=number)
                if not amendment:
                    print "+WW+ Couldn't find amendment " + metricName

                bill_or_amendment = amendment
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

                # Find the bill!
                bill = Legislation.objects.filter(congress_session=session,bill_number=number,bill_type=chamber)
                if not bill:
                    print "+WW+ Couldn't find bill " + metricName

                bill_or_amendment = bill

#            # Get answer text and value from spreadsheet
#            answer_text = sheet.cell(row,0).value
#            answer_text = answer_text.encode('utf-8','ignore')


            # Get answer ID and value from spreadsheet
            try:
                answer_id = int(sheet.cell(row,0).value)
            except:
                print "+WW+ Invalid Answer ID on row " + str(row)
                continue

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
                congress_rolls = CongressRoll.objects.filter(legislation=bill).order_by('datetime')
            elif amendment:
                congress_rolls = CongressRoll.objects.filter(amendment=amendment).order_by('datetime')

            votes = []

            if not congress_rolls:
                print "+EE+ Could not find bill or amendment for == " + str(legislation) + " " + str(congress_num)
                continue

            # the possible vote keys
            possible_vote_keys = ["+", "-"]

            # Collect Votes from Congress Rolls
            for roll in congress_rolls:
                for vote in roll.votes.all():
                    vote_key = vote.voteKey
                    if vote_key == answer_value:
                        votes.append(vote)
                    elif not vote_key in possible_vote_keys:
                        print enc("+EE+ Vote roll had vote key that wasn't + or - | voter: " + vote.voter.get_name() + "| legislation: " + bill_or_amendment.get_name() )

            # For all votes
            for vote in votes:
                # Get Voter
                voter = vote.voter

                # Check that answer text was found
                if not answer_id:
                    print "+WW+ Couldn't find answer ID"
                    continue

                # Look for that answer in the database
                answer = Answer.lg.get_or_none(id=answer_id)
                if not answer:
                    print "+WW+ Couldn't find answer for :: " + str(answer.id)
                    continue

                # Look for that question in the database
                questions = answer.question_set.all()
                if not questions:
                    print "+WW+ Couldn't find question for answer ID #" + str(answer.id)
                    continue
                if questions.count() > 1:
                    print "+WW+ Multiple questions found for this answer"

                # If it's found, take the first item of the query set
                question = questions[0]

                # Answer that shit!
                answerAction(voter,question,"PUB",answer_id)
                print "+II+ Successful Answer for " + voter.get_name()

    return metrics


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


def scriptCreateResponses(args=None):
    path = os.path.join(PROJECT_PATH, 'frontend/excel/' + args[0])
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

