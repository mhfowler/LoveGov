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
                    print "++WARNING++ Couldn't find amendment " + metricName
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
                    print "++WARNING++ Couldn't find bill " + metricName

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

            if not congress_rolls:
                print "++ERROR++ Could not find bill or amendment for == " + str(legislation)
                continue

            # Collect Votes from Congress Rolls
            for roll in congress_rolls:
                for vote in roll.votes.all():
                    if vote.votekey == answer_value:
                        votes.append(vote)

            # For all votes
            for vote in votes:
                # Get Voter
                voter = vote.voter

                # Check that answer text was found
                if not answer_text:
                    print "++WARNING++ Couldn't find answer text"
                    continue

                # Look for that answer in the database
                answer = Answer.lg.get_or_none(answer_text=answer_text)
                if not answer:
                    print "++WARNING++ Couldn't find answer for :: " + answer_text
                    continue

                # Look for that question in the database
                questions = answer.question_set.all()
                if not questions:
                    print "++WARNING++ Couldn't find question for answer ID #" + str(answer.id)
                    continue
                if questions.count() > 1:
                    print "++WARNING++ Multiple questions found for this answer"

                # If it's found, take the first item of the query set
                question = questions[0]

                # Look for that response in the database
                responses = voter.view.responses.filter(question=question)
                if not responses: # If it doesn't exist, create it
                    response = Response(question=question,most_chosen_answer=answer,explanation="")
                    response.total_num = 1
                    response.most_chosen_num = 1
                    response.autoSave(creator=voter)
                # Otherwise, change the answer
                else:
                    if len(responses) > 1:
                        print "++DUPLICATE++ Potential duplicate response for user ID #" + str(voter.id) + " and question ID #" + str(question.id)
                    response = responses[0]
                    response.most_chosen_answer = answer
                    response.total_num = 1
                    response.most_chosen_num = 1
                    response.save()

                metrics[metricName] += 1

                print metricName + " " + str(metrics[metricName])

    return metrics


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
                print "++WARNING++ No answer text"
                continue

            # Find answer
            answer = Answer.lg.get_or_none(answer_text=answer_text)
            if not answer:
                print "++WARNING++ Answer not found for text :: " + answer_text
                continue

            questions = answer.question_set.all()
            if questions:
                question = questions[0]

                responses = politician.view.responses.filter(question=question)
                if not responses:
                    response = Response(question=question,most_chosen_answer=answer,explanation="")
                    response.most_chosen_num = 1
                    response.total_num = 1
                    response.autoSave(creator=politician)
                else:
                    if len(responses) > 1:
                        print "++DUPLICATE++ Potential duplicate response for question ID #" + str(question.id) + "and user id #" + str(politician.id)
                    response = responses[0]
                    response.most_chosen_answer = answer
                    response.explanation = ''
                    response.total_num = 1
                    response.most_chosen_num = 1
                    response.save()

                print "Successfully answered question for " + politician_name[0]
