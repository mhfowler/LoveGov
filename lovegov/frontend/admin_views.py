### LOVEGOV ###
from lovegov.modernpolitics.backend import *

### Python ###
from django.http import *
from modernpolitics import send_email


def adminHome(request,vals={}):
    def getForms(vals):
        vals['createUserForm'] = CreateUserForm()
        vals['searchUserForm'] = SearchUserForm(auto_id='search_%s')

    userProfile = vals['viewer']
    if request.method == 'GET' and str(userProfile.username) in TEAM_EMAILS:
        vals['message'] = "Admins can add users here"
        getForms(vals)
        return renderToResponseCSRF('deployment/pages/admin/home.html', vals, request)
    elif request.method=='POST' and userProfile.username in TEAM_EMAILS:
        if 'createUser' in request.POST:
            createUserForm = CreateUserForm(request.POST)
            getForms(vals)
            if createUserForm.is_valid() and not createUserForm.checkUserExists():
                createUserForm.save()
                vals['message'] = "User added, you may add more users from this page"
            else:
                vals['message'] = "Input into form was not valid or user already exists"
    else:
        vals['forbidden'] = "You aren't allowed here"
    return renderToResponseCSRF('deployment/pages/admin/home.html', vals, request)


def adminAction(request,vals={}):
    if request.method=='POST':
        action = request.POST['action']
        if action == "searchuser":
            return searchUser(request,vals)
        elif action == 'reinviteuser':
            return reinviteUser(request,vals)

def searchUser(request,vals={}):
    searchUserForm = SearchUserForm(request.POST)
    queryset = searchUserForm.searchUserProfiles()
    return HttpResponse(json.dumps(queryset))

def reinviteUser(request,vals={}):
    userProfile = UserProfile.objects.get(id=request.POST['id'])
    new_password = generateRandomPassword(8)
    userProfile.user.set_password(new_password)
    userProfile.user.save()
    EMAIL_SENDER = 'info@lovegov.com'
    EMAIL_TEMPLATE = 'alphaInvite.html'
    vals = {'firstname':userProfile.first_name,'message':userProfile.basicinfo.invite_message,'email':userProfile.username,'password':new_password}
    send_email.sendTemplateEmail(userProfile.basicinfo.invite_subject,EMAIL_TEMPLATE,vals,EMAIL_SENDER,userProfile.username)
    return HttpResponse("+")

def writeAllUsers(request,vals={}):
    allusers = UserProfile.objects.filter(user_type="U")
    for user in allusers:
        vals = {'firstname':userProfile.first_name,'message':userProfile.basicinfo.invite_message,'email':userProfile.username,'password':new_password}


