########################################################################################################################

# lovegov
from lovegov.modernpolitics.backend import *
from lovegov.settings import PROJECT_PATH

########################################################################################################################
########################################################################################################################

def createPoliticianProfiles(sheet):
    for column in range(2,sheet.ncols):
        name = sheet.cell(0,column).value.split(" ")
        firstname = name[0]
        lastname = name[1]
        fullname = name[0] + " " + name[1]
        if not UserProfile.objects.filter(first_name=name[0],last_name=name[1],politician=True):
            print "Creating " + fullname
            email = firstname + "@lovegov.com"
            password = 'president'
            politician = createUser(fullname,email,password)
            politician.user_profile.confirmed = True
            politician.user_profile.politician = True
            politician.user_profile.save()
            image_path = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/' + lastname.lower() + ".jpg")
            politician.user_profile.setProfileImage(file(image_path))
            print "Successfully created and confirmed " + fullname


def answerQuestions(sheet):
    errors = ''
    ans_not_found = 0
    question_not_found = 0
    text_not_found = 0
    duplicate_responses = 0
    # For the cells in a question sheet
    for row in range(1,sheet.nrows):
        for column in range(2,sheet.ncols):
            # Get politician name
            politician_name = sheet.cell(0,column).value.split(" ")
            print politician_name

            # Find the politician
            politician = UserProfile.lg.get_or_none(first_name=politician_name[0],last_name=politician_name[1],politician=True)

            # Get the answer text
            answer_text = sheet.cell(row,column).value
            answer_text = answer_text.encode('utf-8','ignore')
            print answer_text
            # Check answer text
            if not answer_text:
                text_not_found += 1
                errors += "++WARNING++ Answer text not found\n"
                continue
            # Find the answer
            answer = Answer.lg.get_or_none(answer_text=answer_text)
            if not answer:
                ans_not_found += 1
                errors += "++WARNING++ Answer not found for text :: " + answer_text +'\n'
                continue

            # Find the question that corresponds to this answer
            questions = answer.question_set.all()
            if questions:
                question = questions[0]

                # See if a response already exists
                responses = politician.view.responses.filter(question=question)
                if not responses:
                    response = Response(question=question,most_chosen_answer=answer,explanation="")
                    response.most_chosen_num = 1
                    response.total_num = 1
                    response.autoSave(creator=politician)
                else:
                    if len(responses) > 1:
                        duplicate_responses += 1
                        print "++DUPLICATE++ Potential duplicate response for user ID #" + str(politician.id) + " and question ID #" + str(question.id)
                    response = responses[0]
                    response.most_chosen_answer = answer
                    response.explanation = ''
                    response.most_chosen_num = 1
                    response.total_num = 1
                    response.save()
            else:
                question_not_found += 1
                errors += "++WARNING++ Question Not Found for politician " + politician.get_name() + '\n'


    print "========= Errors =========="
    print errors
    print "========= Stats =========="
    print "Potential duplicate responses: " + str(duplicate_responses)
    print "Answer Objects not found in database: " + str(ans_not_found)
    print "Question Objects not found in database: " + str(question_not_found)
    print "Answer Text not given: " + str(text_not_found)