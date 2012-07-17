########################################################################################################################
########################################################################################################################
#
#           Helpers
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.send_email import *

# django
from django.shortcuts import render_to_response
from django.template.context import RequestContext, RenderContext
from django.template import loader

# python
import string
import httpagentparser
from googlemaps import GoogleMaps
import sunlight
import pprint

browser_logger = logging.getLogger('browserlogger')


#-----------------------------------------------------------------------------------------------------------------------
# gets query set of main topics
#-----------------------------------------------------------------------------------------------------------------------
def getMainTopics():
    return Topic.objects.filter(topic_text__in=MAIN_TOPICS)

#-----------------------------------------------------------------------------------------------------------------------
# convenience method to get a user with inputted name or email
#-----------------------------------------------------------------------------------------------------------------------
def getUser(name):
    splitted = name.split()
    if len(splitted) > 1:
        first_name = splitted[0]
        last_name = splitted[1]
        users = UserProfile.objects.filter(first_name=first_name, last_name=last_name)
    else:
        users = UserProfile.objects.filter(first_name=name)
    if users.count() == 1:
        return users[0]
    elif users.count() == 0:
        users = UserProfile.objects.filter(email=name)
    return users

#-----------------------------------------------------------------------------------------------------------------------
# takes in a request and returns the path to the source of the request. This is request.path if normal request, and this
# is the referer if it is an ajax request.
#-----------------------------------------------------------------------------------------------------------------------
def checkBrowserCompatible(request):

    to_return = True

    cookie = request.COOKIES.get('atyourownrisk')
    if cookie:
        if cookie == 'yes':
            return True

    user_agent = request.META.get('HTTP_USER_AGENT')
    if user_agent:
        parsed = httpagentparser.detect(user_agent)
        browser = parsed.get('browser')
        if browser:
            browser_logger.debug('useragent: ' + pprint.pformat(parsed))
            browser_name = browser.get('name')
            if browser_name == "Microsoft Internet Explorer":
                version = float(browser.get('version'))
                if version < 9.0:
                    to_return = False
    else:
        to_return = False

    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# Returns location from address string and zipcode.
#-----------------------------------------------------------------------------------------------------------------------
def locationHelper(address, zip):

    location = PhysicalAddress.lg.get_or_none(address_string=address, zip=zip)
    if not location:
        if (not address) and zip:
            address_string = zip
        else:
            address_string = address
        gmaps = GoogleMaps(GOOGLEMAPS_API_KEY)
        coordinates = gmaps.address_to_latlng(address_string)
        try:
            state_district = sunlight.congress.districts_for_lat_lon(coordinates[0],coordinates[1])
            location = PhysicalAddress(address_string=address,zip=zip,latitude=coordinates[0],
                longitude=coordinates[1],state=state_district[0]['state'],district=state_district[0]['number'])
            location.save()
        except BadRequestException as e:
            error = "sunlight error: ", e
            errors_logger.error(error)

    return location

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
    return path

def getHostHelper(request):
    return 'http://' + request.get_host()

def getRedirectURI(request, redirect):
    domain = getHostHelper(request)
    redirect_uri = domain + redirect
    return redirect_uri

def getEmptyDict():
    return {}

#-----------------------------------------------------------------------------------------------------------------------
# Render template with csrf context processor.
#-----------------------------------------------------------------------------------------------------------------------
def renderToResponseCSRF(template, vals, request):
    """Does stuff that we need to happen on every single template render (such as context processing)."""
    # get privacy mode
    try:
        vals['privacy'] = request.COOKIES['privacy']
    except KeyError:
        vals['privacy'] = 'PUB'
    vals['request'] = request
    response = render_to_response(template, vals, context_instance=RequestContext(request))
    response.set_cookie("fb_state", vals['fb_state'])
    return response

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
        return Network.lg.get_or_none(alias=alias)
    elif type == 'group':
        return Group.lg.get_or_none(id=alias)
    elif type == 'blog':
        return BlogEntry.lg.get_or_none(id=int(split[2]))

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method for rendering a template to string.
#-----------------------------------------------------------------------------------------------------------------------
def ajaxRender(template, vals, request):
    context = RequestContext(request, vals)
    template = loader.get_template(template)
    return template.render(context)

#-----------------------------------------------------------------------------------------------------------------------
# Gets a user profile from a request or id.
#-----------------------------------------------------------------------------------------------------------------------
def getUserProfile(request=None, control_id=None):
    #Try and get a ControllingUser
    if control_id:
        control = ControllingUser.lg.get_or_none(id=control_id)
    else:
        control = ControllingUser.lg.get_or_none(id=request.user.id)

    user_prof = None
    if control:     #Try and get a user profile from that Control if it exists
        user_prof = UserProfile.lg.get_or_none(id=control.user_profile_id)
        if not user_prof:
            errors_logger.error("Controlling User: " + str(control.id) + " does not have a userProfile")

    from lovegov.modernpolitics.defaults import getAnonUser
    user_prof = user_prof or getAnonUser()
    return user_prof #and return it


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
