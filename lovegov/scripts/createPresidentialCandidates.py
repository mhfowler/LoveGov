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
                errors += "Answer text not found\n"
                continue
            # Find the answer
            answer = Answer.lg.get_or_none(answer_text=answer_text)
            if not answer:
                ans_not_found += 1
                errors += "+++Answer not found for text :: " + answer_text +'\n'
                continue

            # Get the value and find the question
            answer_val = answer.value
            question = Question.lg.get_or_none(answers__answer_text=answer_text)
            if question:
                # See if a response already exists
                response = UserResponse.lg.get_or_none(responder=politician,question=question)
                if not response:
                    print "Response Created"
                    response = UserResponse(responder=politician,question=question,answer_val=answer_val,explanation="")
                    response.autoSave(creator=politician)
                else:
                    print "Response Updated"
                    response.answer_val = answer_val
                    response.explanation = ''
                    response.save()
            else:
                question_not_found += 1
                errors += "---Question Not Found for politician" + politician.get_name() + '\n'


    print "========= Errors =========="
    print errors
    print "========= Stats =========="
    print "Answer Objects not found: " + str(ans_not_found)
    print "Question Objects not found: " + str(question_not_found)
    print "Answer Text not found: " + str(text_not_found)