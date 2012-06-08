from lovegov.beta.modernpolitics import models as betamodels
from lovegov.beta.modernpolitics.backend import generateRandomPassword
from lovegov.beta.modernpolitics.models import UserProfile
from lovegov.beta.modernpolitics.send_email import sendTemplateEmail


# Fixes password for user
userprofile = UserProfile.objects.get(username="cschmidt@risd.edu")
userprofile.user.set_password("sorrycatherine")
userprofile.user.save()
dictionary = {'firstname':userprofile.first_name,'password':"sorrycatherine"}
sendTemplateEmail("LoveGov Security Update",'alphaSecurityUpdate.html',dictionary,'info@lovegov.com',userprofile.username)



"""
for userprofile in betamodels.UserProfile.objects.all():
    password = generateRandomPassword(10)
    if not betamodels.User.objects.filter(username=userprofile.username).exists():
        control = betamodels.ControllingUser.objects.create_user(username=userprofile.username, email=userprofile.email, password=password)
        control.user_profile = userprofile
        control.save()
        userprofile.user = control
        userprofile.save()
        dictionary = {'firstname':userprofile.first_name,'password':password}
        sendTemplateEmail("LoveGov Security Update",'alphaSecurityUpdate.html',dictionary,'info@lovegov.com',userprofile.username)
"""