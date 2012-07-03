########################################################################################################################

# lovegov
from lovegov.modernpolitics.backend import *

########################################################################################################################
########################################################################################################################

def createPoliticianProfiles(sheet):
    for column in range(2,sheet.ncols):
        name = sheet.cell(0,column).value.split(" ")
        firstname = name[0]
        lastname = name[1]
        fullname = name[0] + " " + name[1]
        if not Politician.objects.filter(first_name=name[0],last_name=name[1]).exists() and not ElectedOfficial.objects.filter(first_name=name[0],last_name=name[1]).exists():
            print "Creating " + fullname
            email = firstname + "@lovegov.com"
            password = 'president'
            politician = createUser(fullname,email,password,type="politician")
            politician.user_profile.confirmed = True
            politician.user_profile.save()
            image_path = os.path.join(settings.PROJECT_PATH, 'frontend/static/images/presidentialCandidates/' + lastname.lower() + ".jpg")
            politician.user_profile.setProfileImage(file(image_path))
            print "Successfully created and confirmed " + fullname


def answerQuestions(sheet):
    for row in range(1,sheet.nrows):
        for column in range(2,sheet.ncols):
            politician_name = sheet.cell(0,column).value.split(" ")
            print politician_name
            if politician_name[1] == "Obama" or politician_name[1] == "Paul":
                politician = ElectedOfficial.objects.get(first_name=politician_name[0],last_name=politician_name[1])
            else:
                politician = Politician.objects.get(first_name=politician_name[0],last_name=politician_name[1])
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