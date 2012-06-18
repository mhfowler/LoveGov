########################################################################################################################
########################################################################################################################
#
#           Helpers
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.models import *

# django
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template import loader

# python
import string

#-----------------------------------------------------------------------------------------------------------------------
# takes in a request and returns the path to the source of the request. This is request.path if normal request, and this
# is the referer if it is an ajax request.
#-----------------------------------------------------------------------------------------------------------------------
def getSourcePath(request):
    if request.is_ajax():
        if request.method == 'GET':
            path = request.POST.get('url')
        else:
            path = request.GET.get('url')
        if not path:
            referer = request.META.get('HTTP_REFERER')
            if not referer:
                return request.path
            else:
                if LOCAL:
                    splitted = referer.split(".com:8000")
                else:
                    splitted = referer.split(".com")
                path = splitted[1]
        else:
            if LOCAL:
                splitted = path.split(".com:8000")
            else:
                splitted = path.split(".com")
            path = splitted[1]
    else:
        path = request.path
    print "path: " + path
    return path

#-----------------------------------------------------------------------------------------------------------------------
# Render template with csrf context processor.
#-----------------------------------------------------------------------------------------------------------------------
def renderToResponseCSRF(template, dict, request):
    """Does stuff that we need to happen on every single template render (such as context processing)."""
    # get privacy mode
    try:
        dict['privacy'] = request.COOKIES['privacy']
    except KeyError:
        dict['privacy'] = 'PUB'
    try:
        dict['linkfrom'] = request.COOKIES['linkfrom']
    except KeyError:
        dict['linkfrom'] = 0
    dict['request'] = request
    return render_to_response(template, dict, context_instance=RequestContext(request))

#-----------------------------------------------------------------------------------------------------------------------
# returns and object from the url which uniquely identifies it
#-----------------------------------------------------------------------------------------------------------------------
def urlToObject(url):
    split = filter(None,url.split('/'))
    type = split[0]
    alias = split[1]
    if type == 'profile':
        return UserProfile.lg.get_or_none(alias=alias)
    elif type == 'network':
        return Network.lg.get_or_none(name=alias)
    elif type == 'group':
        return Group.lg.get_or_none(id=alias)

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method for rendering a template to string.
#-----------------------------------------------------------------------------------------------------------------------
def ajaxRender(template, dict, request):
    context = RequestContext(request, dict)
    template = loader.get_template(template)
    return template.render(context)

#-----------------------------------------------------------------------------------------------------------------------
# Gets a user profile from a request or id.
#-----------------------------------------------------------------------------------------------------------------------
def getUserProfile(request=None, control_id=None):
    if control_id:
        control = ControllingUser.lg.get_or_none(id=control_id)
    else:
        control = ControllingUser.lg.get_or_none(id=request.user.id)
    if control:
        return control.user_profile
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# Gets privacy from cookies.
#-----------------------------------------------------------------------------------------------------------------------
def getPrivacy(request):
    """"Returns value of privacy cookie, or in the case of no cookie returns 'public'."""
    try:
        to_return = request.COOKIES['privacy']
    except KeyError:
        logger.error("no privacy cookie")
        to_return = 'PUB'
    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# Checks if an email is valid
#-----------------------------------------------------------------------------------------------------------------------
def checkEmail(email):
    splitted = email.split("@")
    if len(splitted)==2:
        extension = splitted[1]
        valid = ValidEmailExtension.objects.filter(extension=extension)
        if valid: return True
        valid = ValidEmail.objects.filter(email=email)
        if valid: return True
        else: return False
    else:
        return False

def checkUnique(email):
    already = ControllingUser.objects.filter(username=email)
    if already: return False
    else: return True

def checkRegisterCode(register_code):
    if RegisterCode.objects.filter(code_text=register_code).exists():
        return True
    else:
        return False

def enc(s):
    return s.encode('ascii', 'ignore')

def restoreUser(user):
    password = generateRandomPassword(10)
    control = ControllingUser.objects.create_user(username=user.username, email=user.username, password=password)
    control.user_profile = user
    control.save()
    user.user = control
    user.save()
    print (user.username + ": " + password)

#-----------------------------------------------------------------------------------------------------------------------
# Generates a random password with digits and characters of given length
#-----------------------------------------------------------------------------------------------------------------------
def generateRandomPassword(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))

#-----------------------------------------------------------------------------------------------------------------------
# Generates random key for keeping photo location secret.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def photoKey(type=".jpg"):
    key = str(random.randint(1,999999))           # TODO: make cryptographically safe
    return key + type

#-------------------------------------------------------------------------------------------------------------------
# Alpha
#-------------------------------------------------------------------------------------------------------------------
def removeUser(email):
    """
    Removes an Alpha user.

    @param email: email address of user to remove
    @type email: string
    """
    control = ControllingUser.objects.get(username=email)
    control.delete()
    return True

#-----------------------------------------------------------------------------------------------------------------------
# Adds email to valid email list.
#-----------------------------------------------------------------------------------------------------------------------
def addValidEmail(email):
    new_email = ValidEmail(email=email)
    new_email.save()
    print("added: " + str(new_email.email))