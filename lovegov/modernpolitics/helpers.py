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
import traceback
import httpagentparser
from googlemaps import GoogleMaps
import sunlight
from sunlight.errors import BadRequestException
from curses.ascii import isalnum
from urlparse import urlsplit
import Image

browser_logger = logging.getLogger('browserlogger')

#-----------------------------------------------------------------------------------------------------------------------
# helper for logging and throwing errors
#-----------------------------------------------------------------------------------------------------------------------
class LGException(Exception):

    def __init__(self, error_message, client_message=None, request=None, vals=None):

        if client_message:
            self.client_message = client_message
        else:
            self.client_message = error_message

        self.error_message = error_message
        critical_logger.critical(self.error_message)

    def __str__(self):
        return repr(self.error_message)

    def getClientMessage(self):
        return self.client_message

#-----------------------------------------------------------------------------------------------------------------------
# returns an object from an alias
#-----------------------------------------------------------------------------------------------------------------------
def aliasToObject(alias):
    if alias in HOME_URLS:
        return None
    else:
        to_return = Group.lg.get_or_none(alias=alias)
        if to_return:
            to_return = to_return.downcast()
    if not to_return:
        to_return = UserProfile.lg.get_or_none(alias=alias)
    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# def filter by time
#-----------------------------------------------------------------------------------------------------------------------
def filterByCreatedWhen(stuff, time_start, time_end):
    if time_start:
        stuff = stuff.filter(created_when__gt=time_start)
    if time_end:
        stuff = stuff.filter(created_when__lt=time_end)
    return stuff

def filterByEditedWhen(stuff, time_start, time_end):
    if time_start:
        stuff = stuff.filter(edited_when__gt=time_start)
    if time_end:
        stuff = stuff.filter(edited_when__lt=time_end)
    return stuff

def filterByWhen(stuff, time_start, time_end):
    if time_start:
        stuff = stuff.filter(when__gt=time_start)
    if time_end:
        stuff = stuff.filter(when__lt=time_end)
    return stuff

#-----------------------------------------------------------------------------------------------------------------------
# gets query set of main topics, pseudo-caching
#-----------------------------------------------------------------------------------------------------------------------
def getMainTopics(vals=None):
    if vals:
        main_topics = vals.get('main_topics')
    else:
        main_topics = None
    if not main_topics:
        main_topics = Topic.objects.filter(topic_text__in=MAIN_TOPICS)
        if vals:
            vals['main_topics'] = main_topics
    return main_topics

#-----------------------------------------------------------------------------------------------------------------------
# fills vals with useres group data
#-----------------------------------------------------------------------------------------------------------------------
def getMyGroups(request, vals={}):
    viewer = vals['viewer']
    groups = vals.get('all_my_groups')
    if not groups:
        groups = viewer.getGroups()
        vals['all_my_groups'] = groups
    my_groups = vals.get('my_groups')
    if not my_groups:
        my_groups = groups.filter(group_type="U")
        vals['my_groups'] = my_groups
    my_networks = vals.get('my_groups')
    if not my_networks:
        my_networks = groups.filter(group_type="N")
        vals['my_networks'] = my_networks

#-----------------------------------------------------------------------------------------------------------------------
# gets official questions, pseudo-caching
#-----------------------------------------------------------------------------------------------------------------------
def getOfficialQuestions(vals=None):
    if vals:
        official_questions = vals.get('official_questions')
    else:
        official_questions = None
    if not official_questions:
        official_questions = Question.objects.filter(official=True).order_by("-rank")
        if vals:
            vals['official_questions'] = official_questions
    return official_questions

#-----------------------------------------------------------------------------------------------------------------------
# takes in a query set of questions, and returns a dictionary of the questions organized by topic.
#-----------------------------------------------------------------------------------------------------------------------
def getQuestionsDictionary(questions=None, vals=None):

    if not questions:
        questions = getOfficialQuestions(vals)

    topics = getMainTopics(vals)

    to_return = {'all':questions, 'topics':[]}
    for t in topics:
        to_return['topics'].append((t, questions.filter(main_topic_id=t.id)))

    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# checks if current session is with authenticated and confirmed user. If so, redirect to home page.
#-----------------------------------------------------------------------------------------------------------------------
def ifConfirmedRedirect(request):
    already = getUserProfile(request)
    if (not already.isAnon()) and already.confirmed:
        return shortcuts.redirect("/home/")
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# answers all questions randomly for a user
#-----------------------------------------------------------------------------------------------------------------------
def randomAnswers(user):
    from lovegov.modernpolitics.actions import answerAction
    questions = Question.objects.filter(official=True)
    for q in questions:
        answers = list(q.answers.all())
        my_answer = random.choice(answers)
        # print "answered: ", my_answer.answer_text
        answerAction(user, question=q, privacy='PUB', answer_id=my_answer.id, weight=5, explanation="")
    user.last_answered = datetime.datetime.now()
    user.save()

def randomWhales():
    print "RANDOM WHALES"
    from lovegov.modernpolitics.compare import updateGroupViews
    g = Group.lg.get_or_none(title="Save The Whales")
    if g:
        print "save the whales!"
        for x in UserProfile.objects.all()[:4]:
            print x.get_name()
            g.joinMember(x)
            randomAnswers(x)
        print "group view!"
        updateGroupViews()

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

def getAllUsers(not_team=False):
    users = UserProfile.objects.filter(ghost=False).exclude(alias="anonymous")
    if not_team:
        users = users.filter(developer=False)
    return users

def getBill(bill_type, bill_number, session_num):
    session = CongressSession.objects.get(session=session_num)
    bill = Legislation.lg.get_or_none(bill_type=bill_type, bill_number=bill_number, congress_session=session)
    return bill

def getAmendment(amendment_type, amendment_number, session_num):
    session = CongressSession.objects.get(session=session_num)
    amendment = LegislationAmendment.lg.get_or_none(amendment_type=amendment_type, amendment_number=amendment_number, congress_session=session)
    return amendment

def getImportantCongressRollsFromBill(bill):
    rolls = CongressRoll.objects.filter(important=True, legislation=bill)
    return rolls

def getImportantCongressRollsFromAmendment(amendment):
    rolls = CongressRoll.objects.filter(important=True, amendment=amendment)
    return rolls

def getVotesFromRolls(congress_rolls, answer_value=None):

    votes =[]

    possible_vote_keys = ["+", "-", "0"]
    found_votes = 0
    invalid_votes = 0
    total_votes = 0
    for roll in congress_rolls:
        for vote in roll.votes.all():
            total_votes += 1
            vote_key = vote.votekey
            if vote_key == answer_value or not answer_value:
                votes.append(vote)
                found_votes += 1
            elif vote_key not in possible_vote_keys:
                invalid_votes += 1
    print enc("+II+ invalid/found/total " + str(invalid_votes) + "/" + str(found_votes) + "/" + str(total_votes))

    return votes

#-----------------------------------------------------------------------------------------------------------------------
# convenience methods to get some common things
#-----------------------------------------------------------------------------------------------------------------------
def getDemocraticParty():
    getParty(alias="democrats")

def getRepublicanParty():
    getParty(alias="republicans")

def getParty(alias):
    return Party.lg.get_or_none(alias=alias)

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
            browser_name = browser.get('name')
            if browser_name == "Microsoft Internet Explorer":
                try:
                    version = float(browser.get('version'))
                    if version < 9.0:
                        to_return = False
                except ValueError as e:
                    to_return = False

    if not to_return:
        browser_logger.debug('useragent: ' + str(user_agent))

    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# Returns a location with coordinates, either by using passed in location, or creating a new one
#-----------------------------------------------------------------------------------------------------------------------
def locationHelper(address, city, state, zip, location=None):

    if not location:
        location = PhysicalAddress()
        location.save()

    full_address = ''
    if address:
        full_address += address
    if city:
        if not full_address == '':
            full_address += ', '
        full_address += city
    if state:
        if not full_address == '':
            full_address += ', '
        full_address += state
    if zip:
        if not full_address == '':
            full_address += ', '
        full_address += zip

    location.address_string = address
    location.city = city
    location.state = state
    location.zip = zip

    gmaps = GoogleMaps(GOOGLEMAPS_API_KEY)
    coordinates = gmaps.address_to_latlng(full_address)
    latitude = coordinates[0]
    longitude = coordinates[1]
    location.latitude = latitude
    location.longitude = longitude
    location.save()

    setDistrict(location)

    location.setIdentifier()

    return location

def setDistrict(location):
    latitude = location.latitude
    longitude = location.longitude
    if latitude and longitude:
        try:
            state_district = sunlight.congress.districts_for_lat_lon(latitude,longitude)[0]
            state = state_district['state']
            district = state_district['number']
            location.state = state
            location.district = district
            location.save()
        except BadRequestException as e:
            error = "sunlight error: ", e
            errors_logger.error(error)
    else:
        LGException("set district was called on location with no latitude or longitude")

#-----------------------------------------------------------------------------------------------------------------------
# takes in a request and returns the path to the source of the request. This is request.path if normal request, and this
# is the referer if it is an ajax request.
#-----------------------------------------------------------------------------------------------------------------------
def getSourcePath(request):
    if request.is_ajax():
        if request.method == 'GET':
            url = request.POST.get('url')
        else:
            url = request.GET.get('url')
        if not url:
            url = request.META.get('HTTP_REFERER')
            if not url:
                url = request.path
        tuple = urlsplit(url)
        to_return = tuple[2]
    else:
        to_return = request.path
    return to_return


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
    if vals['requires_login']:
        response.delete_cookie("cookie_data_id")
    return response

#-----------------------------------------------------------------------------------------------------------------------
# returns and object from the url which uniquely identifies it
#-----------------------------------------------------------------------------------------------------------------------
def urlToObject(url):
    alias = url.replace("/","")
    to_return = aliasToObject(alias)
    if not to_return:
        to_return = urlToObjectOld(url)
    return to_return

def urlToObjectOld(url):
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
    elif type == 'scorecard':
        return Scorecard.lg.get_or_none(id=alias)

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method for rendering a template to string.
#-----------------------------------------------------------------------------------------------------------------------
def ajaxRender(template, vals, request):
    context = RequestContext(request, vals)
    template = loader.get_template(template)
    return template.render(context)

def renderHelper(template, vals):
    context = Context(vals)
    template = loader.get_template(template)
    html = template.render(context)
    return html

#-----------------------------------------------------------------------------------------------------------------------
# Gets a user profile from a request or id.
#-----------------------------------------------------------------------------------------------------------------------
def getUserProfile(request=None, control_id=None, control=None):

    control = control or getControllingUser(request, control_id)

    user_prof = None
    if control:     #Try and get a user profile from that Control if it exists
        user_prof = UserProfile.lg.get_or_none(id=control.user_profile_id)
        if not user_prof:
            errors_logger.error("Controlling User: " + str(control.id) + " does not have a userProfile")

    from lovegov.modernpolitics.initialize import getAnonUser
    user_prof = user_prof or getAnonUser()
    return user_prof


def getControllingUser(request=None, control_id=None):
    if control_id:
        control = ControllingUser.lg.get_or_none(id=control_id)
    else:
        control = ControllingUser.lg.get_or_none(id=request.user.id)
    return control


def getCookieData(request):

    cookie_data_id = request.COOKIES.get('cookie_data_id')
    new_cookie = False
    cookie_data = None
    if cookie_data_id:
        cookie_data = CookieData.lg.get_or_none(id=cookie_data_id)
    if not cookie_data:
        cookie_data = CookieData()
        cookie_data.save()
        new_cookie = True
    return cookie_data, new_cookie

def cookieDataResponse(response, cookie_data, new_cookie):
    if new_cookie:
        response.set_cookie("cookie_data_id", cookie_data.id)
    return response

#-----------------------------------------------------------------------------------------------------------------------
# Gets privacy from cookies.
#-----------------------------------------------------------------------------------------------------------------------
def getPrivacy(request):
    """"Returns value of privacy cookie, or in the case of no cookie returns 'public'."""
    return request.COOKIES.get('privacy') or 'PUB'

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
    already = ControllingUser.objects.filter(email=email)
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

def isUniqueAlias(alias):
    if alias in URL_SPECIAL_NAMES:
        return False
    if UserProfile.objects.filter(alias=alias).count() > 0:
        return False
    if Group.objects.filter(alias=alias).count() > 0:
        return False
    return True

def genAliasSlug(alias, unique=True, old_alias=None):
    import re
    alias = alias.replace(' ', '_')
    alias = re.sub(r'\W+', '', alias)
    alias = str(alias).lower()
    nonce = 1
    orig_alias = alias
    if unique:
        while not isUniqueAlias(alias) and alias != old_alias:
            temp_logger.debug("unoriginal:" + alias)
            alias = orig_alias + str(nonce)
            nonce += 1
    return alias



#-----------------------------------------------------------------------------------------------------------------------
# analyzes a queryset of content and prints out type nums
#-----------------------------------------------------------------------------------------------------------------------
def analyzeContentTypes(content):
    types = {}
    for x in content:
        type = x.type
        if type in types:
            types[type] += 1
        else:
            types[type] = 0
    for type in types:
        print type + ": " + str(types[type])

def analyzeGroupTypes(groups):
    types = {}
    for x in groups:
        type = x.group_type
        if type in types:
            types[type] += 1
        else:
            types[type] = 0
    for type in types:
        print type + ": " + str(types[type])



def logIterate(sequence, function):
    count = 0
    for x in sequence:
        function(x)
        count += 1
        if not count%20:
            print count

def calculate_age(born):
    import datetime
    today = datetime.datetime.today()
    try: # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year)
    except ValueError:
        birthday = born.replace(year=today.year, day=born.day-1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


def generateMatchImage(obamaMatch,romneyMatch):
    filename = 'card'+str(obamaMatch)+'x'+str(romneyMatch)+'.png'
    fpath = 'images/matchcards/'+filename
    filepath = settings.STATIC_ROOT+fpath
    urlpath = settings.STATIC_URL+fpath
    import os
    if os.path.isfile(filepath):
        return urlpath
    i=Image.new('RGB',(400,400),'white')
    if(romneyMatch > obamaMatch):
        template = 'romney_template'
    elif obamaMatch > romneyMatch:
        template = 'obama_template'
    else:
        template = 'both_template'
    template_path = settings.STATIC_ROOT+'images/matchcards/'+template+'.png'
    t = Image.open(template_path)
    i.paste(t,(0,0))
    import ImageFont, ImageDraw
    draw = ImageDraw.Draw(i)
    sonusPath = settings.STATIC_ROOT+'fonts/SonusLight.ttf'
    sonus72 = ImageFont.truetype(sonusPath, 72)
    if obamaMatch >= 10:
        obamaX = 70
    else:
        obamaX = 90
    if romneyMatch >= 10:
        romneyX = 245
    else:
        romneyX = 265
    draw.text((obamaX,290), str(obamaMatch), fill="#EF503B", font=sonus72)
    draw.text((romneyX,290), str(romneyMatch), fill="#EF503B", font=sonus72)
    i.save(filepath,'PNG')
    return urlpath