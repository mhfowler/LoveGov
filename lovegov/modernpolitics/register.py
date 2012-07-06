########################################################################################################################
########################################################################################################################
#
#           Registration
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.defaults import *

#-----------------------------------------------------------------------------------------------------------------------
# Resets a users password and sends an email.
#-----------------------------------------------------------------------------------------------------------------------
def resetPassword(user):
    password = generateRandomPassword(10)
    print ("password: " + password)
    user.set_password(password)
    user.save()
    sendPasswordChangeEmail(user, password)

#-----------------------------------------------------------------------------------------------------------------------
# Creates a user for the alpha based on name and email (with autogenerated password)
# args: name, email
#-----------------------------------------------------------------------------------------------------------------------
def createAlphaUser(name, email):
    password = passwordAutogen()
    createUser(name, email, password)
    sendAlphaTesterEmail(name, email, password)

def createFBUser(name, email):
    password = generateRandomPassword(10)
    control = createUser(name, email, password)
    vals = {'name':name,'email':email,'password':password}
    sendTemplateEmail(subject="Welcome to LoveGov", template="facebookRegister.html", dictionary=vals, email_sender='info@lovegov.com', email_recipient=email)
    return control

#-------------------------------------------------------------------------------------------------------------------
# creates a new userprofile from name, email and password, along with controlling user to manage this profile.
# - name, email, password
#-------------------------------------------------------------------------------------------------------------------
def createUser(name, email, password, type='userProfile',active=True):
    if not ControllingUser.objects.filter(username=email):
        control = ControllingUser.objects.create_user(username=email, email=email, password=password)
        control.is_active = active
        control.save()
        logger.debug("created control: " + control.email)
        user_profile = createUserHelper(control=control, name=name, type=type, active=active)
        logger.debug("created userpof: " + user_profile.get_name())
        control.user_profile = user_profile
        control.save()
        return control
    else:
        splitted = email.split("@")
        if len(splitted)==1:
            print ("deletes! " + email)
            c = ControllingUser.objects.get(username=email)
            c.delete()
            return createUser(name, email, password, type, active)
        else:
            print ("email duplicate!" + email)
            if splitted[1] == "lovegov.com":
                print ("deletes! " + email)
                c = ControllingUser.objects.get(username=email)
                c.delete()
                return createUser(name, email, password, type, active)

#-------------------------------------------------------------------------------------------------------------------
# creates a new userprofile from name, email and password, along with controlling user to manage this profile.
# - name, email, password
#-------------------------------------------------------------------------------------------------------------------
def createUserHelper(control,name,type='userProfile',active=True):
    # new user profile
    if type=="politician":
        userProfile = Politician(user_type='P')
    elif type=="senator":
        userProfile = Senator(user_type='S')
    elif type=="representative":
        userProfile = Representative(user_type='R')
    else:
        userProfile = UserProfile(user_type='U')
        toregister = getToRegisterNumber()
        toregister.number -= 1
        toregister.save()
        # split name into first and last
    names = name.split(" ")
    if len(names) == 2:
        userProfile.first_name = names[0]
        userProfile.last_name = names[1]
    elif len(names) == 3:
        userProfile.first_name = names[0] + " " + names[1]
        userProfile.last_name = names[2]
        # save email and username from control
    userProfile.email = control.email
    userProfile.username = control.username
    # active
    userProfile.is_active = active
    userProfile.confirmation_link = str(random.randint(1,9999999999999999999))   #TODO: crypto-safe
    # worldview
    world_view = WorldView()
    world_view.save()
    userProfile.view_id = world_view.id
    userProfile.save()
    userid = userProfile.id
    # profilePage
    userProfilePage = ProfilePage(person=userProfile)
    userProfilePage.save()
    # alias
    userProfile.makeAlias()
    # filter settings
    filter_setting = getDefaultFilter()
    userProfile.filter_setting = filter_setting
    # notification settings
    userProfile.initNotificationSettings()
    # connections group and lovegov group and join or create network group
    userProfile.createIFollowGroup()
    userProfile.createFollowMeGroup()
    userProfile.joinLoveGovGroup()
    userProfile.createDefaultFilter()
    # associate with control
    userProfile.user = control
    userProfile.save()
    if type=="userProfile":
        pass
        #sendYayRegisterEmail(userProfile)
    # return user prof
    return userProfile

