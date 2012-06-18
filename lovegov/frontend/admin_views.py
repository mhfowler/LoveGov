### LOVEGOV ###
from lovegov.modernpolitics.backend import *

### Python ###
from django.http import *
from modernpolitics import send_email


def adminHome(request,dict={}):
    def getForms(dict):
        dict['createUserForm'] = CreateUserForm()
        dict['searchUserForm'] = SearchUserForm(auto_id='search_%s')

    userProfile = dict['user']
    if request.method == 'GET' and str(userProfile.username) in TEAM_EMAILS:
        dict['message'] = "Admins can add users here"
        getForms(dict)
        return renderToResponseCSRF('deployment/pages/admin/home.html', dict, request)
    elif request.method=='POST' and userProfile.username in TEAM_EMAILS:
        if 'createUser' in request.POST:
            createUserForm = CreateUserForm(request.POST)
            getForms(dict)
            if createUserForm.is_valid() and not createUserForm.checkUserExists():
                createUserForm.save()
                dict['message'] = "User added, you may add more users from this page"
            else:
                dict['message'] = "Input into form was not valid or user already exists"
    else:
        dict['forbidden'] = "You aren't allowed here"
    return renderToResponseCSRF('deployment/pages/admin/home.html', dict, request)


def adminAction(request,dict={}):
    if request.method=='POST':
        action = request.POST['action']
        if action == "searchuser":
            return searchUser(request,dict)
        elif action == 'reinviteuser':
            return reinviteUser(request,dict)

def searchUser(request,dict={}):
    searchUserForm = SearchUserForm(request.POST)
    queryset = searchUserForm.searchUserProfiles()
    return HttpResponse(json.dumps(queryset))

def reinviteUser(request,dict={}):
    userProfile = UserProfile.objects.get(id=request.POST['id'])
    new_password = generateRandomPassword(8)
    userProfile.user.set_password(new_password)
    userProfile.user.save()
    EMAIL_SENDER = 'info@lovegov.com'
    EMAIL_TEMPLATE = 'alphaInvite.html'
    dict = {'firstname':userProfile.first_name,'message':userProfile.basicinfo.invite_message,'email':userProfile.username,'password':new_password}
    send_email.sendTemplateEmail(userProfile.basicinfo.invite_subject,EMAIL_TEMPLATE,dict,EMAIL_SENDER,userProfile.username)
    return HttpResponse("+")

def writeAllUsers(request,dict={}):
    allusers = UserProfile.objects.filter(user_type="U")
    for user in allusers:
        dict = {'firstname':userProfile.first_name,'message':userProfile.basicinfo.invite_message,'email':userProfile.username,'password':new_password}


