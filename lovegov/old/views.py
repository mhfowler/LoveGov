########################################################################################################################
###### VIEWS ###########################################################################################################
#
#       Main Control Room
#           each page is associated with one of these views, which handles retrieval and presentation
#
#
########################################################################################################################
################################################# TAGS #################################################################
#
# FINISHED:     The code is more or less in its final state and should not be edited without conversing
#
# USABLE:       The code handles the task that it is designed to perform. The specifics of where it will redirect
#               the user are not sorted out and details may be added, but it's usable in it's current state.
#
# BROKEN:       The code does not work and should not be used without fixing.
#
# TEST:         The code is for testing purposes and not part of the project proper yet (should go in tests.py)
#
# <NAME>_HELPME: If either you or I are unable to complete a method use this tag to request help. <NAME> should be your
#                name so we know who is requesting help.  This will be useful if we have more coders working with us in
#                the future. So if I were to be asking you for help, I'd write "CLAY_HELPME"
#
# <NAME>_MINE:   If you don't want somebody else to touch your code, use this tag and put your name in <NAME>
#
########################################################################################################################
################################################## IMPORT ##############################################################


### INTERNAL ###
from lovegov.beta.modernpolitics.forms import *
from lovegov.beta.modernpolitics import backend
from lovegov.beta.modernpolitics.models import *

### DJANGO LIBRARIES ###
from django.http import *
from django.forms import *
from django.forms.models import model_to_dict

from django.template import loader
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template

from django import shortcuts
from django.shortcuts import render_to_response

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from django.contrib import messages
from django.contrib import auth

from django.core.exceptions import ObjectDoesNotExist

### EXTERNAL LIBRARIES ###
from PIL import Image
import logging

# logger
logger = logging.getLogger('filelogger')

########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Login page, from which you can also register.
# args: request, to_page (the page they were trying to actionGET before being redirected to login screen)
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def universalLogin(request, to_page='home/'):
    """Login page., from which you can also register."""
    # checks if user requested to POST information
    if request.method == 'POST':
        # if registering
        if request.POST['submit_type'] != 'Login':
            return register(request)
        # check to see if the entered username and password is valid
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_active:
            auth.login(request, user)
            # check if user confirmed
            user_prof = UserProfile.objects.get(id=user.id)
            if user_prof.confirmed:
                redirect_response = shortcuts.redirect('/' + to_page)
                redirect_response.set_cookie('privacy', value='PUB')
                return redirect_response
            else:
                auth.logout(request)
                dict = {'user':user_prof}
                return renderToResponseCSRF('usable/need_confirmation.html',dict,request)
        # else invalid, render login form with errors
        else:
            login_form = LoginForm(request.POST)
    # else get request, render blank login form
    else:
        login_form = LoginForm()
    # reload page
    register_form = RegisterForm()
    dict = {'login_form': login_form, 'register_form': register_form}
    return renderToResponseCSRF('usable/login.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Action of registering a user.
# post:
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def register(request):
    """Action of registering a user."""
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            dict = {}
            # checks if entered username is already in use
            if UserProfile.objects.filter(username=request.POST['email']):
                # TODO: change to actual error message
                return renderToResponseCSRF('test/account_exists.html', dict, request)
            # else save new user
            else:
                register_form.save(request.POST)
                # TODO: change to something else
                return renderToResponseCSRF('usable/register_success.html', dict, request)
        else:
            login_form = LoginForm()
            dict = {'login_form': login_form, 'register_form': register_form}
            return renderToResponseCSRF('usable/login.html',dict,request)
    # else get request, render blank register form
    else:
        return shortcuts.redirect('/home/')

#-----------------------------------------------------------------------------------------------------------------------
# Page from which you can confirm your account.
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def confirm(request, link, dict={}):
    """Page from which you can confirm your account."""
    if request.method == 'POST':
        # check if username and password match
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None and user.is_active:
            auth.login(request, user)
            user_prof = getUserProfile(request)
            # check if correct confirmation number
            if user_prof.confirmation_link == link:
                user_prof.confirmed = True
                user_prof.save()
                redirect_response = shortcuts.redirect('/home')
                redirect_response.set_cookie('privacy', value='PUB')
                return redirect_response
            else:
                dict['error'] = "You are not at your own confirmation page."
        # else invalid, render login form with errors
        else:
            dict['login_form'] = LoginForm(request.POST)
    # else get request, render blank login form
    else:
        dict['login_form'] = LoginForm()
    # return
    return renderToResponseCSRF('usable/confirm.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Logout page.
# post: empty
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def logout(request, dict={}):
    """Logout page."""
    if request.method == 'POST':
        auth.logout(request)
        return renderToResponseCSRF('usable/logout.html',{},request=request)
    else:
        auth.logout(request)
        return renderToResponseCSRF('usable/logout.html',{},request=request)

#-----------------------------------------------------------------------------------------------------------------------
# User profile page.
# post:
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def displayProfile(request,profile_name, profile_uid,dict={}):
    """User profile page."""
    person = UserProfile.objects.get(id=profile_uid)
    # check if name in url matches id in url
    if profile_name == (person.first_name + person.last_name):
        user = dict['user']
        dict['person'] = person
        # get comparison data
        dict['user_responses'] = UserResponse.objects.filter(responder=user)
        dict['person_responses'] = UserResponse.objects.filter(responder=person)
        # get friends
        dict['following'] = UserFollow.objects.filter(user=person, confirmed=True)
        # check if you are them
        if request.user.username==person.username:
            dict['myprofile'] = True
        # check if you are friends with them
        else:
            youarefollowing = UserFollow.objects.filter(user=user,to_user=person)
            if youarefollowing:
                dict['youarefollowing'] = youarefollowing[0]
        # profile page
        dict['page'] = person.getProfilePage()
        # render
        return renderToResponseCSRF('usable/profile.html',dict,request)
    # else invalid profile url
    else:
        message = profile_name + " does not match " + profile_uid
        dict['message'] = message
        return renderToResponseCSRF('usable/message.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Page to displays a detail of a single piece of content.
# explanation:
#  - switch statement based on type of content, downcasts content and chooses correct template.
#  - then updates dictionary with information relevant to all content with helper method getContentFrame()
#  - then renders
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def displayContent(request, c_id, dict={}):
    """Displays a detail of a single piece of content."""
    content = Content.objects.get(id=c_id)
    user = dict['user']
    # add to viewed history
    user.my_history.add(content)
    # switch statement to select template and downcast
    object = content.downcast()
    dict['object'] = object
    dict['content_template'] = content.getTemplate()
    # special case for groups
    if content.type == 'G':
        ingroup = object.members.filter(id=user.id)
        dict['ingroup'] = ingroup
    elif content.type == 'D':
        dict['left_debater'] = Debaters.objects.get(side="L",content__id=c_id).user.id
        dict['right_debater'] = Debaters.objects.get(side="R", content__id=c_id).user.id
        dict['user'] = getUserProfile(request)
        dict['debateID'] = c_id
        return renderToResponseCSRF('debates/debates.html', dict, request)
    # special case for persistent debates
    elif content.type == 'Y':
        dict = displayPersistent(dict=dict, object=object)
    # update dictionary with info relevant to all content
    dict = getFrame(request=request,dict=dict,object=object)
    # special case for groups
    if content.type == 'G':
        return renderToResponseCSRF('usable/display_group.html',dict,request)
    # else render
    else:
        return renderToResponseCSRF('usable/display_content.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Helper method for display content, which deals with stuff universal to all content.
# explanation:
#  - switch statement based on type of content, downcasts content and chooses correct template.
#  - then renders frame (which is not specific to content)
# args: request
# return: updated dictionary
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def getFrame(request, dict, object):
    # get user
    user = dict['user']
    # update values
    dict['content'] = object
    # creator
    try:
        creator = object.getCreator()
        dict['creator'] = object.getCreatorDisplayName(user=user)
        dict['created'] = object.created_when
        dict['has_permission'] = object.getPermission(user)
        if creator.id == user.id:
            dict['iamcreator'] = True
            dict['editform'] = object.getEditForm()
    except ObjectDoesNotExist:
        print "error"
    # comments
    user_votes = Voted.objects.filter(user=user)
    dict['thread'] = makeThread(request=request,object=object,depth=0,user=user,user_votes=user_votes)
    # voting history
    dict['votes'] = object.upvotes - object.downvotes
    my_vote = user_votes.filter(content=object)
    if my_vote:
        dict['i_vote'] = my_vote[0].value
    else: dict['i_vote'] = 0
    dict['status'] = object.status
    # return
    return dict

#-----------------------------------------------------------------------------------------------------------------------
# Creates the html for a comment thread.
# explanation:
#  - recursive, <ul> within <ul>
# args: request, object (which comment thread is for), depth (have many level it has recurred)
# return: html string
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, depth, user, user_votes):
    """Creates the html for a comment thread."""
    comments = Comment.objects.filter(on_content=object).order_by('-status')
    # if not empty
    if comments:
        # my comments, that I created
        my_comments = Created.objects.filter(user=user)
        # open list
        to_return = "<ul>"
        for c in comments:
            to_return += "<br>"
            to_return += "<li>"
            # check if i like
            my_vote = user_votes.filter(content=c)
            if my_vote:
                ivote = my_vote[0].value
            else: ivote = 0
            # check if iown
            iown = my_comments.filter(content=c)
            if iown:
                own = True
            else: own = False
            # render comment html
            dict = model_to_dict(c)
            dict['status'] = c.status
            dict['my_vote'] = ivote
            dict['owner'] = own
            dict['votes'] = c.upvotes - c.downvotes
            dict['creator_name'] = c.getCreatorDisplayName(user=user)
            # get percent similar
            comp = backend.findUserComparison(user, c.getCreator())
            if comp:
                dict['simpercent'] = comp.result
            context = RequestContext(request,dict)
            template = loader.get_template('usable/comment.html')
            comment_string = template.render(context)
            to_return += comment_string
            # look at children
            to_return += makeThread(request,c,depth+1, user, user_votes)
            # close list
        to_return += "</ul>"
        return to_return
    else:
        return ''

#-----------------------------------------------------------------------------------------------------------------------
# Updates dictionary properly for persistent debate.
# args: dict (dict to be updated), object (debate)
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def displayPersistent(dict, object):
    object.update()     # update debate
    user = dict['user']
    # if both users aren't confirmed, check if you are on the invite list
    if not(object.affirmative and object.negative):
        onlist = object.possible_users.filter(id=user.id)
        if onlist:
            dict['youareinvited'] = True
        else:
            dict['youareinvited'] = False
    # else check if the debate is over and there is winner
    else:
        if object.voting_finished:
            if object.affirmative == object.winner:
                dict['affirmativewins'] = True
            elif object.negative == object.winner:
                dict['negativewins'] = True
        # else if debate is ongoing, check if it is your turn
        elif not object.debate_finished:
            if object.affirmative == user and object.turn_current:
                dict['yourturn'] = True
            elif object.negative == user and not object.turn_current:
                dict['yourturn'] = True
        # else check how many seconds remaining till vote is cast.
        else:
            now = datetime.datetime.now()
            delta = object.debate_expiration_time - now
            timeremaining = delta.days * 86400 + delta.seconds
            dict['timeremaining'] = timeremaining
        # check if/who you voted for
        my_vote = DebateVoted.objects.filter(user=user, content=object)
        if my_vote:
            vote = int(my_vote[0].value)
            if vote == 1:
                dict['ivotepos'] = True
            elif vote == -1:
                dict['ivoteneg'] = True
    return dict

#-----------------------------------------------------------------------------------------------------------------------
# Simple interface for creating content (to be deprecated).
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def createSimple(request,  dict={}):
    """Simple interface for creating content (to be deprecated)"""
    from lovegov.beta.modernpolitics.actionsPOST import actionPOST   # workaround for mutual import in model (has to be in method)
    petition = PetitionForm_simple()
    event = EventForm_simple()
    news = NewsForm_simple()
    group = GroupForm()
    album = UserImageForm()
    # IF post
    if request.method == 'POST':
        request.POST['action'] = 'create'
        return actionPOST(request)
    # IF get
    else:
        dict['petition'] = petition
        dict['event'] = event
        dict['news'] = news
        dict['group'] = group
        dict['album'] = album
        return renderToResponseCSRF('usable/create_content_simple.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Lists all questions on the site.
# args: template (to render), dict (of all values needed for rendering), request
# return: HttpResponse
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def listQuestions(request, dict={}):
    """Lists all questions on the site."""
    user = dict['user']
    questions = Question.objects.all()
    responses = UserResponse.objects.filter(responder=user)
    qr = []
    for q in questions:
        r = responses.filter(question=q)
        if r:
            qr.append((q,r[0]))
        else: qr.append((q,0))
    return renderToResponseCSRF('usable/list_questions.html', {'qr':qr},request)



#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for all views which require login.
# args: view (which is being wrapped)
# return: HttpResponse
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def requiresLogin(view):
    """Wrapper for all views which require login."""
    def new_view(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(request.path + 'login')
        else:
            # SET DEFAULT DICTIONARY VALUES
            user = getUserProfile(request)
            dict = {'user':user}
            dict = getForms(dict)
            dict['staticpath'] = constants.STATIC_PATH
            # SAVE PAGE ACCESS
            PageAccess().autoSave(request)
        return view(request, dict=dict, *args, **kwargs)
    return new_view

#-----------------------------------------------------------------------------------------------------------------------
# Page for displaying result of comparison between two users.
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def displayUserComparison(request, a_id, b_id, dict={}):
    userA = UserProfile.objects.get(id=a_id)
    userB = UserProfile.objects.get(id=b_id)
    dict['A'] = userA
    dict['B'] = userB
    dict['comp'] = backend.getUserUserComparison(userA, userB)
    return renderToResponseCSRF('usable/display_comparison.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Page for displaying result of comparison between two users.
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def displayWorldView(request, id, dict={}):
    view = WorldView.objects.get(id=id)
    dict['view'] = view
    return renderToResponseCSRF('usable/display_worldview.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Page for editing user's basic info.
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def editInfo(request, dict={}):
    user = dict['user']
    if request.method == 'POST':
        form = BasicInfoForm(request.POST)
        if form.is_valid():
            basicInfo = form.save(user.basicinfo)
            user.basicinfo = basicInfo
            user.save()
            return shortcuts.redirect(user.get_url())
        else:
            dict['form'] = form
            return renderToResponseCSRF('usable/edit_info.html',dict,request)
    else:
        previous_info = model_to_dict(user.basicinfo)
        form = BasicInfoForm(previous_info)
        dict['form'] = form
        return renderToResponseCSRF('usable/edit_info.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Returns value of privacy cookie, or in the case of no cookie returns 'public'.
# args: request
# return: string
# tags: USABLE
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
# Returns UserProfile associated with logged in user.
# args: request
# return: UserProfile
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def getUserProfile(request):
    control = ControllingUser.objects.filter(id=request.user.id)
    if control:
        return control[0].getUserProfile()
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# Info about the site and our mission.
# args: request
# return: updated dictionary
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def aboutNovavote(request,  dict={}):
    """Info about the site and our mission."""
    dict['message'] = "Novavote will change the world."
    content = Content.objects.exclude(type='I')
    dict['content'] = content
    return renderToResponseCSRF('usable/message.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# My profile.
# args: request
# return: updated dictionary
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def myProfile(request, dict={}):
    """My profile."""
    user = dict['user']
    return shortcuts.redirect('/profile/' + user.first_name + user.last_name + '/' + str(user.id))

#-----------------------------------------------------------------------------------------------------------------------
# Displays links to all content I have a relationship with.
# args: request
# return: updated dictionary
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def myInvolvement(request, dict={}):
    """ Displays links to all content I have a relationship with."""
    user = dict['user']
    list = user.my_involvement.exclude(content__type='I').order_by('-involvement')
    print list
    dict['relationship_list'] = list
    return renderToResponseCSRF('usable/myinvolvement.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Blackbox
# args: request
# return: updated dictionary
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def myGovernment(request, dict={}):
    message = "This is my government."
    dict['message'] = message
    return renderToResponseCSRF('usable/message.html',dict,request)

########################################################################################################################
########################################  BACKEND OPERATIONS ###########################################################

# initialize db
def initialize(request, dict={}):
    backend.initializeDB()
    return HttpResponse("initialized")

# run all update methods
def update(request, dict={}):
    backend.update()
    return HttpResponse("updated")

########################################################################################################################
############################################### DEBUGGING CODE #########################################################

# page for testing search
def deploySearch(request, dict={}):
    return renderToResponseCSRF('deploy/search_test.html', dict, request)

# page for testing register
def deployRegister(request, dict={}):
    if request.method == 'POST':
        register_form = SimpleRegisterForm(request.POST)
        # if valid, save
        if register_form.is_valid():
            control = register_form.save()
            # if user is confirmed, login and send to home page
            if control:
                auth.login(request, control)
                return shortcuts.redirect('/home')
            # else send to page saying confirmation email has been sent!
            else:
                return HttpResponse("awaiting confirmation email")
    else:
        register_form = SimpleRegisterForm()
    dict = {'register_form':register_form}
    dict['recaptcha'] = constants.RECAPTCHA_PUBLIC
    return renderToResponseCSRF('deploy/register_login.html', dict, request)

# page for testing register with facebook
def facebookRegister(request, dict={}):
    return renderToResponseCSRF('test/test_facebook.html', dict, request)

# page that prints out all cookies
def viewCookies(request, dict={}):
    return render_to_response('test/cookies.html', {'request':request})

# prints all content content relationship
def debugLinked(request, dict={}):
    relationships = Linked.objects.all()
    return render_to_response("test/debug.html", {'r':relationships})

def debugFeedback(request, dict={}):
    dict = {'feedback':Feedback.objects.all()}
    return render_to_response("test/feedback.html", dict)

# prints all content content relationship
def debugRelationships(request, dict={}):
    relationships = Relationship.objects.all()
    return render_to_response("test/debug.html", {'u':relationships})

# prints all user user relationship
def debugFriends(request, dict={}):
    relationships = UserFollow.objects.all()
    return render_to_response("test/debug.html", {'f':relationships})

# page that shows all users in database
def debugUsers(request, dict={}):
    dict['users'] = UserProfile.objects.all()
    return renderToResponseCSRF("test/debug_users.html", dict, request)

# page that shows all page accesses in db
def viewAccess(request, dict={}):
    user = getUserProfile(request)
    access = PageAccess.objects.filter(user=user)
    print access
    return renderToResponseCSRF('usable/actionGET.html', locals(),request)

# should display user information in content section of page
def testHome(request, dict={}):
    user = dict['user']
    uploadform = UploadFileForm()
    dict['uploadform'] = uploadform
    if request.method == 'POST' and 'submitpic' in request.POST:
        try:
            file_content = ContentFile(request.FILES['image'].read())
            Image.open(file_content)
            user.setProfileImage(file_content)
            dict = {'user': user, 'uploadform': uploadform}
            return renderToResponseCSRF('test/test_home.html', dict, request)
        except IOError:
            return HttpResponse("image is invalid")
    else:
        return renderToResponseCSRF('test/test_home.html', dict, request)

def testImage(request, dict={}):
    user = getUserProfile(request)
    form = UploadImageForm()
    if request.method == 'POST':
        uploaded = request.FILES['image']
        file_content = ContentFile(uploaded.read())
        user.basicinfo.profile_image.save(request.FILES['image'].name, file_content)
        dict = {'user':user, 'form':form}
        return renderToResponseCSRF('test/test_image.html', dict, request)
    else:
        dict = {'user':user, 'form':form}
        return renderToResponseCSRF('test/test_image.html', dict, request)


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
################################################## TEST CODE ###########################################################
########################################################################################################################
########################################################################################################################
def debugNotifications(request, dict={}):
    x = 2
    notifications = Notification.objects.all().order_by('-when')[:x]
    actions = Action.objects.all().order_by('-when')[:x]
    relations = Relationship.objects.all().order_by('-when')[:x]
    dict['notifications'] = notifications
    dict['actions'] = actions
    dict['relations'] = relations
    return renderToResponseCSRF('test/debug_notifications.html', dict, request)


def testJ(request, dict={}):
    return render_to_response('test/jquery_test.html')


def qaweb(request, dict={}):
    t_economy = get_template('qaweb/topicQuestions/economy.html')
    html_economy = t_economy.render(Context())
    dict['economy'] = html_economy

    t_education = get_template('qaweb/topicQuestions/education.html')
    html_education = t_education.render(Context())
    dict['education'] = html_education

    t_environment = get_template('qaweb/topicQuestions/environment.html')
    html_environment = t_environment.render(Context())
    dict['environment'] = html_environment

    t_energy = get_template('qaweb/topicQuestions/energy.html')
    html_energy = t_energy.render(Context())
    dict['energy'] = html_energy

    t_foreign_policy = get_template('qaweb/topicQuestions/foreign_policy.html')
    html_foreign_policy = t_foreign_policy.render(Context())
    dict['foreign_policy'] = html_foreign_policy

    t_reform = get_template('qaweb/topicQuestions/reform.html')
    html_reform = t_reform.render(Context())
    dict['reform'] = html_reform

    t_health_care = get_template('qaweb/topicQuestions/health_care.html')
    html_health_care = t_health_care.render(Context())
    dict['health_care'] = html_health_care

    t_social_issues = get_template('qaweb/topicQuestions/social_issues.html')
    html_social_issues = t_social_issues.render(Context())
    dict['social_issues'] = html_social_issues

    t_myviews = get_template('qaweb/topicQuestions/myviews.html')
    html_myviews = t_myviews.render(Context())
    dict['myviews'] = html_myviews

    return renderToResponseCSRF('qaweb/qaweb.html', dict, request)

def debates(request, c_id, dict={}):
    dict['left_debater'] = Debaters.objects.get(side="L",content__id=c_id).user.id
    dict['right_debater'] = Debaters.objects.get(side="R", content__id=c_id).user.id
    dict['user'] = getUserProfile(request)
    return renderToResponseCSRF('debates/debates.html', dict, request)


def feed(request, dict={}):
    return render_to_response('feed/feed.html')

def testfeed(request, dict={}):
    user = getUserProfile(request)
    feed = backend.OldFeed(user)
    feed.calculateScores()
    topic = str(feed.getTopicTypeMatches())
    return HttpResponse(topic)

def getForms(dict):
    petition = CreatePetitionForm()
    event = CreateEventForm()
    news = CreateNewsForm()
    group = CreateGroupForm()
    debate = DebateForm()
    dict['petition'] = petition
    dict['event'] = event
    dict['news'] = news
    dict['group'] = group
    dict['debate'] = debate
    return dict

def testmainpage(request, dict={}):
    return render_to_response('test/mainpage.html')

def scrollbar(request, dict={}):
    return render_to_response('test/scrollbar.html')

### USABLE ###
# views for creating each piece of content
def createContent(request,  dict={}):
    from lovegov.beta.modernpolitics.actionsPOST import actionPOST   # workaround for mutual import in model (has to be in method)
    # IF post
    if request.method == 'POST':
        return actionPOST(request)
    # IF get
    else:
        petition = CreatePetitionForm()
        event = CreateEventForm()
        news = CreateNewsForm()
        group = CreateGroupForm()
        debate = CreateDebateForm()
        album = UserImageForm()
        dict['petition'] = petition
        dict['event'] = event
        dict['news'] = news
        dict['group'] = group
        dict['debate'] = debate
        dict['album'] = album
        return renderToResponseCSRF('usable/create_content.html',dict,request)

### USABLE ###
# This view is the login and registration homepage.
def frontPage(request, dict={}):
    # checks if user requested to POST information
    if request.method == 'POST':
        if 'loginbutton' in request.POST:
            return universalLogin(request, 'test_home')
        elif 'submitregistration' in request.POST:
            return register(request)
    # else the user is coming to our page for the first time
    else:
        # generate blank Forms to display on the page
        login_form = LoginForm()
        register_form = RegisterForm()
        # sets dictionary values
        dict = {'login_form': login_form, 'register_form': register_form}
        return renderToResponseCSRF('usable/login.html', dict, request)

### USABLE ###
# takes in a piece of content, and returns a list of all comments and comments of comments
# recursive... i is depth of comment (0 is base, 1 is comment on comment.. etc)
# four tuple: comment, depth, totalvotes, myvote
def get_thread(user, object, i):
    comments = Comment.objects.filter(on_content=object)
    to_return = []
    if (comments):
        my_likes = Relationship.objects.filter(user=user,relationship='L')
        my_dislikes = Relationship.objects.filter(user=user,relationship='D')
        for c in comments:
            # check if i like
            my_vote=0
            ilike = my_likes.filter(content=c)
            if (ilike):
                my_vote=1
            else: #check if i dislike
                idislike = my_dislikes.filter(content=c)
                if (idislike): my_vote=-1
                # calculate vote total (THIS SHOULD BE DEPRECATED)
            status = c.status
            # create tuple
            to_return.append((c,i,status,my_vote))
            # look at children
            children = get_thread(user, c, i+1)
            to_return.extend(children)
    return to_return

### USABLE ###
# working on making more beautiful comment thread
def displayThread(request, content_id, dict={}):
    content = Content.objects.get(id=content_id)
    dict['thread']=makeThread(request,content,0,dict['user'])
    return renderToResponseCSRF('usable/thread.html',dict,request)

# for testing ajax
def test_ajax(request, dict={}):
    # this if statement is how we differentiate between ajax request and normal request
    if request.is_ajax():
        print "ajax!"
        return HttpResponse("ajax banana")
    else:
        return render_to_response('test/test_ajax.html')

from django import shortcuts
# logout user
def test_logout(request):
    auth.logout(request)
    return shortcuts.redirect('/login_old/')


from lovegov.beta.modernpolitics.models import Topic

# test database
def testSaveData(request, dict={}):
    topic = Topic(topic_text='gayrights')
    topic.save()
    user = UserProfile(first_name='testDude', id=99)
    user.save()
    topics = Topic.objects.all()
    stringRep = "list: "
    for x in topics:
        stringRep += x.topic_text + ' '
    return HttpResponse(stringRep)

# This view logs a user into the site.  After a user is logged in, use request.user to actionGET information about the user.
def loginUser_old(request, dict={}):
    # checks if user requested to POST information
    if request.method == 'POST':
        # references to what the user entered in the login form
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # check to see if the entered username and password is valid, assigns output to 'user'
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            auth.login(request, user)
            # login success
            return testHome(request)
        else:
        # return render_to_response('check.html', {'username': username , 'password': password})
            # Show an error page.  TODO: do something cooler
            return render_to_response('test/fail_login.html')
    else:
        # generate a blank LoginForm
        login_form = LoginForm()
        # sends to user a page
        print "check"
        return render_to_response('test/login_old.html', {'login_form': login_form})

def test(request, dict={}):
    messages.success( request, 'Test successful' )
    return HttpResponseRedirect( reverse('main_page'))

def main_page(request, template_name , dict={}):
    # create dictionary of items to be passed to the template
    c = { messages: messages.get_messages( request ) }

    # render page
    return render_to_response( template_name, c)

    # TEST
# Returns the current date and time
def current_datetime(request, dict={}):
        current_date = datetime.datetime.now()
        user = TestModel(name='clay')
        user.save()
        # loads the html template (without variables inserted)
        t = loader.get_template('test/current_datetime.html')
        # renders the final html to send to client with variables defined in Context
        html = t.render(Context(locals()))
        return HttpResponse(html)

# TEST
def loginuser(request, dict={}):
    user = User(username='rioisk3',first_name='clay',last_name='dunwell',email='rioisk@gmail.com',password='texers',is_staff=0,is_active=1,is_superuser=1)
    user.save()
    t = loader.get_template('test/newuser.html')
    html = t.render(Context(locals()))
    return HttpResponse(html)

# TEST
# Iterates over numbers 0 through 10 and returns them.  <br> is an HTML tag to go to the next line
def iterate_num(request, dict={}):
    j = "0<br>"
    for i in range(1,10):
        j = j + str(i) + "<br>"
    return render_to_response('test/zero_ten.html', {'zero_ten': j})

# TEST
def homepage(request, dict={}):
    return render_to_response('test/homepage.html')

# TEST
def form(request, dict={}):
    t = loader.get_template('create_content/create_content.html')
    html = t.render(Context())
    return HttpResponse(html)

# TEST
def searchret(request, dict={}):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        search_result = 'You searched for: %r' % request.GET['q']
        tests = TestModel.objects.filter(name__icontains=q)
    else:
        search_result = 'You submitted an empty form.'
    t = loader.get_template('test/search_results.html')
    html = t.render(Context(locals()))
    return HttpResponse(html)

# test inherit
def test_inherit(request, dict={}):
    word = "banana"
    return render_to_response('home_inherit.html', locals())

from BeautifulSoup import BeautifulSoup
import os

def billparser(request):
    Legislation.objects.all().delete()
    path = os.path.join(os.path.dirname(__file__), 'C:\\GovTrackData\\112\\bills\\').replace('\\','/')
    listing = os.listdir(path)
    for infile in listing:
        print 'Inserting data from ' + str(infile) + ' into database'
        # open XML file
        fileXML = open(path + infile)
        # parse XML file into internal data structure
        parsedXML = BeautifulSoup(fileXML)
        # create new Legislation, set and save Attributes from parsed XML
        newLegislation = Legislation()
        newLegislation.setSaveAttributes(parsedXML=parsedXML)
    return HttpResponse("All legislation is now in the database!")

def billrelations(request):
    path = os.path.join(os.path.dirname(__file__), 'C:\\GovTrackData\\112\\bills\\').replace('\\','/')
    listing = os.listdir(path)
    for infile in listing:
        print 'Inserting data from ' + str(infile) + ' into database'
        # open XML file
        fileXML = open(path + infile)
        # parse XML file into internal data structure
        parsedXML = BeautifulSoup(fileXML)
        editLeg = Legislation.objects.get(bill_type=parsedXML.bill['type'], bill_number=int(parsedXML.bill['number']))
        for rbill in parsedXML.relatedbills:
            addLeg = Legislation.objects.get(bill_type=rbill['type'], bill_number=int(rbill['number']))
            editLeg.bill_relation.add(addLeg)

def billroll(request):
    path = os.path.join(os.path.dirname(__file__), 'C:\\GovTrackData\\112\\rolls\\').replace('\\','/')
    listing = os.listdir(path)
    CongressRoll.objects.all().delete()
    RollOption.objects.all().delete()
    for infile in listing:
        print 'Inserting data from ' + str(infile) + ' into database'
        # open XML file
        fileXML = open(path + infile)
        # parse XML file into internal data structure
        parsedXML = BeautifulSoup(fileXML)
        newRoll = CongressRoll()
        newRoll.setSaveAttributes(parsedXML)

########################################################################################################################
########################################################################################################################
########################################################################################################################
