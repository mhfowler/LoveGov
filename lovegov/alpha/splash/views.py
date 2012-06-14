### LOVEGOV ALPHA ###
from lovegov.beta.modernpolitics.forms import EmailListForm
from lovegov.beta.modernpolitics.forms import RegisterForm

#### LOVEGOV BETA ###
from lovegov.beta.modernpolitics import models as betamodels
from lovegov.beta.modernpolitics import forms as betaforms
from lovegov.beta.modernpolitics import backend as betabackend
from lovegov.beta.modernpolitics import actionsPOST as betaactions
from lovegov.beta.modernpolitics import constants as betaconstants
from lovegov.beta.modernpolitics import facebook
from lovegov.beta.modernpolitics.models import UserProfile
from lovegov.local_manage import LOCAL
from lovegov.settings import UPDATE

### DJANGO LIBRARIES ###
from django.http import *
from django import shortcuts
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.template import loader
from django.core.files.base import ContentFile
from django.db.models import Q

### EXTERNAL ###
from PIL import Image

### PYTHON ###
import json
import random
import pprint
import urllib

### LOGGING ###
import logging

logger = logging.getLogger('filelogger')


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
# Splash page and learn more.
#-----------------------------------------------------------------------------------------------------------------------
def redirect(request, blah="blah"):
    return shortcuts.redirect('/web/')

def splash(request):
    return splashForm(request, 'deployment/pages/splash/splash.html')

def learnmore(request):
    return splashForm(request, 'deployment/pages/splash/learnmore.html')

def underConstruction(request):
    return render_to_response('deployment/pages/microcopy/construction.html')

def splashForm(request,templateURL):
    dict = {}
    if request.method=='POST':
        emailform = EmailListForm(request.POST)
        if emailform.is_valid():
            emailform.save()
            return render_to_response(templateURL, dict, RequestContext(request))
        else:
            return render_to_response(templateURL, dict, RequestContext(request))
    else:
        emailform = EmailListForm()
        dict['emailform'] = emailform
        return render_to_response(templateURL, dict, RequestContext(request))

def postEmail(request):
    if request.method=='POST' and request.POST['email']:
        email = request.POST['email']
        emails = betamodels.EmailList.objects.filter(email=email)
        if not emails:
            newEmail = betamodels.EmailList(email=email)
            newEmail.save()
        if request.is_ajax():
            return HttpResponse('+')
        else:
            dict = {'emailMessage':"Thanks! We'll keep you updated!"}
            return renderToResponseCSRF(template='deployment/pages/login-main.html', dict=dict, request=request)
    else:
        return shortcuts.redirect('/comingsoon/')

#-----------------------------------------------------------------------------------------------------------------------
# Privacy policy page.
#-----------------------------------------------------------------------------------------------------------------------
def privacyPolicy(request,dict={}):
    if request.method == 'POST' and 'button' in request.POST:
        return loginPOST(request,dict={})
    else:
        return renderToResponseCSRF(template='deployment/pages/login-privacy-policy.html', dict=dict, request=request)


#-----------------------------------------------------------------------------------------------------------------------
# Alpha login page.
#-----------------------------------------------------------------------------------------------------------------------
def login(request, to_page='web/', message="", dict={}):
    """
    Handles logging a user into LoveGov

    @param request:
    @type request: HttpRequest
    @param to_page:
    @param dict:
    @type dict: dictionary
    @return:
    """
    # if has fb authenticated, try to facebook login
    if facebook.fbLogin(request,dict):
        print "topage: " + to_page
        #facebook.fbMakeFriends(request,dict) #when fb is authenticated, check to make friends with their current friends
        return shortcuts.redirect('/' + to_page)
    fb_state = facebook.fbGetRedirect(request, dict)
    if request.method == 'POST' and 'button' in request.POST:
        response = loginPOST(request,to_page,message,dict)
    else:
        dict.update({"registerform":RegisterForm(), "username":'', "error":'', "state":'fb'})
        response = renderToResponseCSRF(template='deployment/pages/login/login-main.html', dict=dict, request=request)
    response.set_cookie("fb_state", fb_state)
    return response

def loginPOST(request, to_page='web',message="",dict={}):
    dict['registerform'] = RegisterForm()
    if request.POST['button'] == 'login':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            user_prof = betabackend.getUserProfile(control_id=user.id)
            if user_prof.confirmed:
                auth.login(request, user)
                redirect_response = shortcuts.redirect('/' + to_page)
                redirect_response.set_cookie('privacy', value='PUB')
                return redirect_response
            else:
                error = 'Your account has not been validated yet. Check your email for a confirmation link.  It might be in your spam folder.'
        else:
            error = 'Invalid Login/Password.'
        dict.update({"username":request.POST['username'], "message":message, "error":error, "state":'login'})
        return renderToResponseCSRF(template='deployment/pages/login/login-main.html', dict=dict, request=request)
    elif request.POST['button'] == 'register':
        registerform = RegisterForm(request.POST)
        if registerform.is_valid():
            registerform.save()
            dict.update({"fullname":registerform.cleaned_data.get('fullname'), "email":registerform.cleaned_data.get('email')})
            return renderToResponseCSRF(template='deployment/pages/login/login-main-register-success.html', dict=dict, request=request)
        else:
            dict.update({"registerform":registerform, "state":'register'})
            return renderToResponseCSRF(template='deployment/pages/login/login-main.html', dict=dict, request=request)
    elif request.POST['button'] == 'recover':
        user = betamodels.ControllingUser.lg.get_or_none(username=request.POST['username'])
        if user: betabackend.resetPassword(user)
        message = u"This is a temporary recovery system! Your password has been reset. Check your email for your new password, you can change it from the account settings page after you have logged in."
        return HttpResponse(json.dumps(message))

def passwordRecovery(request, to_page='home', message="", confirm_link=None, dict={}):
    if request.POST:
        if "first_step" in request.POST:
            user =  betamodels.UserProfile.lg.get_or_none(email=request.POST['email'])
            if user:
                if request.is_ajax(): return HttpResponse(json.dumps({'html': ajaxRender('deployment/pages/login/login-forgot-password-step_two.html',dict=dict,request=request)}))
                else: return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password.html",dict=dict.update({"step_two":True}),request=request)
            else:
                msg = u"No user with this email exists."
                if request.is_ajax(): return HttpResponse(json.dumps({'error1': msg}))
                else: return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password.html",dict=dict.update({'error1':msg}),request=request)
        elif "second_step" in request.POST:
            pass
        else:
            return HttpResponse("check")
    else:
        return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password.html",dict=dict,request=request)

def logout(request, dict={}):
    auth.logout(request)
    response = shortcuts.redirect('/web/')
    response.delete_cookie('fb_token')
    return response

def confirm(request, to_page='home', message="", confirm_link=None,  dict={}):
    print "confirm: " + confirm_link
    user = betamodels.UserProfile.lg.get_or_none(confirmation_link=confirm_link)
    if user:
        user.confirmed = True
        user.save()
        dict['user'] = user
        print "user:" + user.get_name()
    if request.method == 'GET':
        # TODO: login user and redirect him/her to Q&A Web after a couple of seconds
        return renderToResponseCSRF('deployment/pages/login/login-main-register-confirmation.html', dict=dict, request=request)
    else:
        return loginPOST(request,to_page,message,dict)

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for all alpha views which require login.
#-----------------------------------------------------------------------------------------------------------------------
def requiresLogin(view):
    """Wrapper for all views which require login."""
    def new_view(request, *args, **kwargs):
        try:
            user = betabackend.getUserProfile(request)
            # IF NOT DEVELOPER AND IN UPDATE MODE, REDIRECT TO CONSTRUCTION PAGE
            if UPDATE and not user.developer and not LOCAL:
                return shortcuts.redirect("/underconstruction/")
            # ELIF NOT AUTHENTICATED REDIRECT TO LOGIN
            elif not request.user.is_authenticated():
                print request.path
                return HttpResponseRedirect('/login' + request.path)
            # ELSE AUTHENTICATED
            else:
                dict = {'user':user, 'google':betaconstants.GOOGLE_LOVEGOV}
                rightSideBar(None, dict)
            # SAVE PAGE ACCESS
            if request.method == 'GET':
                ignore = request.GET.get('log-ignore')
            else:
                ignore = request.POST.get('log-ignore')
            if not ignore:
                page = betamodels.PageAccess()
                page.autoSave(request)
        # exception if user has old cookie
        except ImproperlyConfigured:
            response = shortcuts.redirect('/login' + request.path)
            response.delete_cookie('sessionid')
            logger.debug('deleted cookie')
            return response
        return view(request, dict=dict, *args, **kwargs)
    return new_view

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method for rendering a template to string.
#-----------------------------------------------------------------------------------------------------------------------
def ajaxRender(template, dict, request):
    context = RequestContext(request, dict)
    template = loader.get_template(template)
    return template.render(context)

#-----------------------------------------------------------------------------------------------------------------------
# ajax get method switcher
#-----------------------------------------------------------------------------------------------------------------------
def ajaxSwitch(request, dict):
    type = request.POST['type']
    if type=='thread':
        return ajaxThread(request, dict)
    elif type=='feed':
        return ajaxFeed(request, dict)

#-----------------------------------------------------------------------------------------------------------------------
# get ajax thread
#-----------------------------------------------------------------------------------------------------------------------
def ajaxThread(request, dict={}):
    content = betamodels.Content.objects.get(id=request.POST['c_id'])
    user = dict['user']
    thread = makeThread(request, content, user)
    to_return = {'html':thread}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# gets frame values and puts in dictionary.
#-----------------------------------------------------------------------------------------------------------------------
def frame(request, dict):
    userProfile = dict['user']
    dict['all_users'] = UserProfile.objects.filter(confirmed=True).order_by("last_name")
    dict['firstLogin'] = userProfile.checkFirstLogin()

#-----------------------------------------------------------------------------------------------------------------------
# gets values for right side bar and puts in dictionary
#-----------------------------------------------------------------------------------------------------------------------
def rightSideBar(request, dict):
    userProfile = dict['user']
    dict['random_questions'] = userProfile.getQuestions()
    dict['all_questions'] = betamodels.Question.objects.all().order_by("-rank")
    dict['main_topics'] = betamodels.Topic.objects.filter(topic_text__in=betaconstants.MAIN_TOPICS)
    dict['root_topic'] = betabackend.getGeneralTopic()

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses to questions
#-----------------------------------------------------------------------------------------------------------------------
def getUserResponses(request,dict={}):
    userProfile = dict['user']
    dict['qr'] = userProfile.getUserResponses()

def setPageTitle(title,dict={}):
    dict['pageTitle'] = title

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses proper format for web
#-----------------------------------------------------------------------------------------------------------------------
def getUserWebResponsesJSON(request,dict={}):
    questionsArray = {}
    for (question,response) in dict['user'].getUserResponses():
        for topic in question.topics.all():
            topic_text = topic.topic_text
            if topic_text not in questionsArray:
                questionsArray[topic_text] = []
        answerArray = []
        for answer in question.answers.all():
            if len(response) > 0:
                checked = (answer.value == response[0].userresponse.answer_val)
                weight = response[0].userresponse.weight
            else:
                checked = False
                weight = 5
            answer = {'answer_text':answer.answer_text,'answer_value':answer.value,'user_answer':checked,'weight':weight}
            answerArray.append(answer)
        toAddquestion = {'id':question.id,'text':question.question_text,'answers':answerArray,'user_explanation':"Idk",'childrenData':[]}
        questionsArray[topic_text].append(toAddquestion)
    dict['questionsArray'] = json.dumps(questionsArray)


#-----------------------------------------------------------------------------------------------------------------------
# This is the view that generates hte QAWeb
#-----------------------------------------------------------------------------------------------------------------------
def web(request, dict={}):
    """
    This is the view that generates the QAWeb

    @param request: the request from the user to the server containing metadata about the request
    @type request: HttpRequest
    @param dict: the dictionary of values to pass into the template
    @type dict: dictionary
    @return:
    """
    if request.method == 'GET':
        getUserWebResponsesJSON(request,dict)
        setPageTitle("lovegov: web",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/qaweb.html', dict, request)
            url = '/web/'
            rebind = 'qaweb'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            frame(request, dict)
            return renderToResponseCSRF(template='deployment/pages/web.html', dict=dict, request=request)
    if request.method == 'POST':
        if request.POST['action']:
            return betaactions.answer(request, dict)
        else:
            return shortcuts.redirect('/alpha/')


def compareWeb(request,alias=None,dict={}):
    """
    This is the view that generates the QAWeb

    @param request: the request from the user to the server containing metadata about the request
    @type request: HttpRequest
    @param dict: the dictionary of values to pass into the template
    @type dict: dictionary
    @return: HttpResponse
    """
    if request.method == 'GET':
        if alias:
            user = dict['user']
            dict['user'] = UserProfile.objects.get(alias=alias)
            comparison = betabackend.getUserUserComparison(user, dict['user'])
            getUserWebResponsesJSON(request,dict)
            dict['user'] = user
            dict['json'] = comparison.toJSON()
            setPageTitle("lovegov: web2",dict)
            if request.is_ajax():
                html = ajaxRender('deployment/center/qaweb-temp.html', dict, request)
                url = '/profile/web/' + alias + '/'
                rebind = 'qaweb'
                to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
                return HttpResponse(json.dumps(to_return))
            else:
                frame(request, dict)
                return renderToResponseCSRF(template='deployment/pages/web.html', dict=dict, request=request)
    if request.method == 'POST':
        if request.POST['action']:
            return betaactions.answer(request, dict)
        else:
            return shortcuts.redirect('/alpha/')


#-----------------------------------------------------------------------------------------------------------------------
# home page with feeds
#-----------------------------------------------------------------------------------------------------------------------
def home(request, dict={}):
    rightSideBar(request, dict)             # even though its homesidebar
    # get feed stuff
    user=dict['user']
    # new
    new = latest(user)
    dict['defaultImage'] = betabackend.getDefaultImage().image
    dict['new_length'] = len(new)
    dict['newfeed'] = new
    # hot
    hot = feedHelper(user=user, feed_type='H')
    dict['hot_length'] = len(hot)
    dict['hotfeed'] = hot
    # best
    best = greatest(user)
    dict['best_length'] = len(best)
    dict['bestfeed'] = best
    setPageTitle("lovegov: beta",dict)
    if request.is_ajax():
        html = ajaxRender('deployment/center/home.html', dict, request)
        url = '/home/'
        rebind = 'home'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/home.html', dict=dict, request=request)

def latest(user, start=0, stop=5, content=None):
    if not content:
        content = betamodels.Content.objects.filter(Q(type='P') | Q(type='N'))
    content = content.order_by('-created_when')
    stop = min(stop, len(content))
    content = content[start:stop]
    return listHelper(user, content)

def greatest(user, start=0, stop=5, content=None,):
    if not content:
        content = betamodels.Content.objects.filter(Q(type='P') | Q(type='N'))
    content = content.order_by("-status")
    stop = min(stop, len(content))
    content = content[start:stop]
    return listHelper(user, content)

def listHelper(user, content):
    user_votes = betamodels.Voted.objects.filter(user=user)
    list=[]
    for c in content:
        vote = user_votes.filter(content=c)
        if vote:
            my_vote=vote[0].value
        else:
            my_vote=0
        list.append((c,my_vote))
    return list

def feedHelper(user, feed_type='H', start=0, stop=5, topics=None):
    items = betabackend.getFeedItems(start=start, stop=stop, feed_type=feed_type, topics=topics)
    list = []
    user_votes = betamodels.Voted.objects.filter(user=user)
    for i in items:
        c = i.content
        vote = user_votes.filter(content=c)
        if vote:
            my_vote=vote[0].value
        else:
            my_vote=0
        list.append((c,my_vote))    # content, my_vote
    return list

def ajaxFeed(request, dict={}):
    if request.method == 'POST':
        user = dict['user']
        feed_type = request.POST['feed_type']
        start = int(request.POST['start'])
        how_many = int(request.POST['how_many'])
        json_data = request.POST['topics']
        topic_aliases = json.loads(json_data)
        stop = start + how_many
        if topic_aliases:
            topics = betamodels.Topic.objects.filter(alias__in=topic_aliases)
            content = betamodels.Content.objects.filter(Q(type='P') | Q(type='N'))
            content = content.filter(main_topic__in=topics)
        else:
            content = betamodels.Content.objects.filter(Q(type='P') | Q(type='N'))
        if feed_type == 'N':
            feed = latest(user, start, stop, content)
        elif feed_type == 'B':
            feed = greatest(user, start, stop, content)
        else:
            if not topic_aliases:
                feed = feedHelper(user, feed_type, start, stop)
            else:
                print ("check it: " + str(topics))
                feed = feedHelper(user, feed_type, start, stop, topics)
        dict['feed'] = feed
        position = start + len(feed)
        dict['defaultImage'] = betabackend.getDefaultImage().image
        context = RequestContext(request,dict)
        template = loader.get_template('deployment/snippets/feed_helper.html')
        feed_string = template.render(context)  # render comment html
        to_return = {'feed':feed_string, 'position':position}
        return HttpResponse(json.dumps(to_return))
    else:
        return HttpResponse("not a real page")

#-----------------------------------------------------------------------------------------------------------------------
# Profile Link
#-----------------------------------------------------------------------------------------------------------------------
def profile(request, alias=None, dict={}):
    user = dict['user']
    if request.method == 'GET':
        if alias:
            frame(request, dict)
            getUserResponses(request,dict)
            # get comparison of person you are looking at
            user_prof = UserProfile.objects.get(alias=alias)
            comparison = betabackend.getUserUserComparison(user, user_prof)
            dict['user_prof'] = user_prof
            dict['comparison'] = comparison
            jsonData = comparison.toJSON()
            dict['json'] = jsonData
            logger.debug("json- " + jsonData)       # debug
            setPageTitle("lovegov: " + user_prof.get_name(),dict)

            # Get user's top 5 similar followers
            prof_follow_me = list(user_prof.getFollowMe())
            for follow_me in prof_follow_me:
                comparison = betabackend.getUserUserComparison(user_prof, follow_me)
                follow_me.compare = comparison.toJSON()
                follow_me.result = comparison.result
            prof_follow_me.sort(key=lambda x:x.result,reverse=True)
            dict['prof_follow_me'] = prof_follow_me[0:5]

            # Get user's top 5 similar follows
            prof_i_follow = list(user_prof.getIFollow())
            for i_follow in prof_i_follow:
                comparison = betabackend.getUserUserComparison(user_prof, i_follow)
                i_follow.compare = comparison.toJSON()
                i_follow.result = comparison.result
            prof_i_follow.sort(key=lambda x:x.result,reverse=True)
            dict['prof_i_follow'] = prof_i_follow[0:5]

            # Get user's random 5 followers
            #dict['prof_follow_me'] = user_prof.getFollowMe(5)

            # Get user's random 5 follows
            #dict['prof_i_follow'] = user_prof.getIFollow(5)

            # Get user's top 5 similar groups
            prof_groups = list(user_prof.getGroups())
            for group in prof_groups:
                comparison = betabackend.getUserGroupComparison(user_prof, group)
                group.compare = comparison.toJSON()
                group.result = comparison.result
            prof_groups.sort(key=lambda x:x.result,reverse=True)
            dict['prof_groups'] = prof_groups[0:5]

            # Get user's random 5 groups
            #dict['prof_groups'] = user_prof.getGroups(5)

            # Get Follow Requests
            dict['prof_requests'] = list(user_prof.getFollowRequests())

            # Is the current user already (requesting to) following this profile?
            dict['is_user_requested'] = False
            dict['is_user_confirmed'] = False
            user_follow = betamodels.UserFollow.lg.get_or_none(user=user,to_user=user_prof)
            if user_follow:
                if user_follow.requested:
                    dict['is_user_requested'] = True
                if user_follow.confirmed:
                    dict['is_user_confirmed'] = True

            # Get Activity
            dict['actions'] = user.getActivity(5)
            print dict['actions'][0].getTo().get_name()
            # get responses
            dict['responses'] = user_prof.getView().responses.count()
            if request.is_ajax():
                html = ajaxRender('deployment/center/profile.html', dict, request)
                url = '/profile/' + alias
                rebind = 'profile'
                to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
                return HttpResponse(json.dumps(to_return))
            else:
                return renderToResponseCSRF(template='deployment/pages/profile.html', dict=dict, request=request)
        else:
            return shortcuts.redirect('/profile/' + user.alias)
    else:
        if request.POST['action']:
            return betaactions.answer(request, dict)
        else:
            to_alias = request.POST['alias']
            return shortcuts.redirect('/alpha/' + to_alias)

#-----------------------------------------------------------------------------------------------------------------------
# Network page
#-----------------------------------------------------------------------------------------------------------------------
def network(request, name=None, dict={}):
    if not name:
        user = dict['user']
        return shortcuts.redirect(user.getNetwork().get_url())
    network = betamodels.Network.objects.get(name=name)
    return group(request,g_id=network.id,dict=dict)

#-----------------------------------------------------------------------------------------------------------------------
# Group page
#-----------------------------------------------------------------------------------------------------------------------
def group(request, g_id=None, dict={}):
    user = dict['user']
    if not g_id:
        return HttpResponse('Group id not provided to view function')
    group = betamodels.Group.lg.get_or_none(id=g_id)
    if not group:
        return HttpResponse('Group id not found in database')
    dict['group'] = group
    comparison = betabackend.getUserGroupComparison(user, group, force=True)
    dict['comparison'] = comparison
    jsonData = comparison.toJSON()
    dict['json'] = jsonData
    dict['defaultImage'] = betabackend.getDefaultImage().image

    # Histogram Things
    dict['histogram'] = group.getComparisonHistogram(user)
    dict['histogram_resolution'] = betaconstants.HISTOGRAM_RESOLUTION
    dict['group_members'] = group.members.order_by('id')[0:25]

    # Get Follow Requests
    dict['prof_requests'] = list(group.getFollowRequests())

    # Is the current user already (requesting to) following this group?
    dict['is_user_follow'] = False
    dict['is_user_confirmed'] = False
    user_follow = betamodels.GroupJoined.lg.get_or_none(user=user,group=group)
    if user_follow:
        if user_follow.requested:
            dict['is_user_follow'] = True
        if user_follow.confirmed:
            dict['is_user_confirmed'] = True

    dict['is_user_admin'] = False
    admins = list( group.admins.all() )
    for admin in admins:
        if admin.id == user.id:
            dict['is_user_admin'] = True

    setPageTitle("lovegov: " + group.title,dict)
    if request.is_ajax():
        html = ajaxRender('deployment/center/group.html', dict, request)
        url = group.get_url()
        rebind = 'group'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        return renderToResponseCSRF(template='deployment/pages/group.html', dict=dict, request=request)


#-----------------------------------------------------------------------------------------------------------------------
# About Link
#-----------------------------------------------------------------------------------------------------------------------
def about(request, dict={}):
    if request.method == 'GET':
        setPageTitle("lovegov: about",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/about.html', dict, request)
            url = '/about/'
            rebind = 'about'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            frame(request, dict)
            return renderToResponseCSRF(template='deployment/pages/about.html', dict=dict, request=request)

#-----------------------------------------------------------------------------------------------------------------------
# Legislation-related pages
#-----------------------------------------------------------------------------------------------------------------------

def legislation(request, session=None, type=None, number=None, dict={}):
    dict['session'], dict['type'], dict['number'] = session, type, number
    if session==None:
        dict['sessions'] = [x['bill_session'] for x in betamodels.Legislation.objects.values('bill_session').distinct()]
        return renderToResponseCSRF(template='deployment/pages/legislation.html', dict=dict, request=request)
    legs = betamodels.Legislation.objects.filter(bill_session=session)
    if type==None:
        type_list = [x['bill_type'] for x in betamodels.Legislation.objects.filter(bill_session=session).values('bill_type').distinct()]
        dict['types'] = [(x, betaconstants.BILL_TYPES[x]) for x in type_list]
        return renderToResponseCSRF(template='deployment/pages/legislation-session.html', dict=dict, request=request)
    if number==None:
        dict['numbers'] = [x['bill_number'] for x in betamodels.Legislation.objects.filter(bill_session=session, bill_type=type).values('bill_number').distinct()]
        return renderToResponseCSRF(template='deployment/pages/legislation-type.html', dict=dict, request=request)
    legs = betamodels.Legislation.objects.filter(bill_session=session, bill_type=type, bill_number=number)
    if len(legs)==0:
        dict['error'] = "No legislation found with the given parameters."
    else:
	leg = legs[0]
        dict['leg_titles'] = leg.legislationtitle_set.all()
        dict['leg'] = leg
    return renderToResponseCSRF(template='deployment/pages/legislation-view.html', dict=dict, request=request)

#-----------------------------------------------------------------------------------------------------------------------
# All Users Link
#-----------------------------------------------------------------------------------------------------------------------
def match(request,dict={}):
    if request.method == 'GET':
        user = dict['user']

        # Get presidential candidates, do comparison, rank them
        obama = betamodels.ElectedOfficial.objects.get(first_name="Barack",last_name="Obama")
        paul = betamodels.ElectedOfficial.objects.get(first_name="Ronald",last_name="Paul")
        romney = betamodels.Politician.objects.get(first_name="Mitt",last_name="Romney")
        list = [obama,paul,romney]
        for presidential_user in list:
            comparison = betabackend.getUserUserComparison(user, presidential_user)
            presidential_user.compare = comparison.toJSON()
            presidential_user.result = comparison.result
        list.sort(key=lambda x:x.result,reverse=True)
        dict['presidential_users'] = list

        # Get network and do comparison
        network = user.getNetwork()
        network.compare = betabackend.getUserGroupComparison(user, network).toJSON()
        dict['network'] = network
        congress = betabackend.getCongressNetwork()
        congress.compare = betabackend.getUserGroupComparison(user, congress).toJSON()
        dict['congress'] = congress
        lovegov = betabackend.getLoveGovUser()
        lovegov.compare = betabackend.getUserUserComparison(user, lovegov).toJSON()
        dict['lovegov'] = lovegov

        # Get latest address, find congressmen, do comparison
        if user.userAddress:
            address = user.userAddress
            congressmen = []
            representative = betamodels.Representative.objects.get(congresssessions=112,state=address.state,district=address.district)
            representative.json = betabackend.getUserUserComparison(user,representative).toJSON()
            congressmen.append(representative)
            senators = betamodels.Senator.objects.filter(congresssessions=112,state=address.state)
            for senator in senators:
                senator.json = betabackend.getUserUserComparison(user,senator).toJSON()
                congressmen.append(senator)
            dict['congressmen'] = congressmen
            dict['state'] = address.state
            dict['district'] = address.district
            dict['latitude'] = address.latitude
            dict['longitude'] = address.longitude

        # Get all facebook friends data
        fb_friends = user.getFBFriends()
        for friend in fb_friends:
            comparison = betabackend.getUserUserComparison(user,friend)
            friend.compare = comparison.toJSON()
            friend.result = comparison.result
        list.sort(key=lambda x:x.result, reverse=True)
        dict['fb_friends'] = fb_friends

        # Get facebook friends network aggregate view
        #my_connections = user.getMyConnections()
        #my_connections.compare = betabackend.getUserGroupComparison(user,my_connections).toJSON()
        #dict['my_connections'] = my_connections

        # dict['user'] doesn't translate well in the template
        dict['userProfile'] = user

        setPageTitle("lovegov: match",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/match.html', dict, request)
            url = '/match/'
            rebind = 'match'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            return renderToResponseCSRF(template='deployment/pages/match.html', dict=dict, request=request)

def matchNew(request, dict={}):
    def election(request,dict={}):
        user = dict['user']
        c1 = betamodels.UserProfile.objects.get(first_name="Clayton",last_name="Dunwell")
        c2 = betamodels.UserProfile.objects.get(first_name="Katy",last_name="Perry")

        list = [c1,c2]
        for c in list:
            comparison = betabackend.getUserUserComparison(user,c)
            c.compare = comparison.toJSON()
            c.result = comparison.result
        dict['c1'] = c1
        dict['c2'] = c2

        # dict['user'] doesn't translate well in the template
        dict['userProfile'] = user
        setPageTitle("lovegov: match2",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/match/match-election-center.html', dict, request)
            url = '/match/'
            rebind = 'match-new'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            dict['section'] = 'election'
            return renderToResponseCSRF(template='deployment/pages/match/match-new.html', dict=dict, request=request)

    def social(request,dict={}):
        user = dict['user']
        c1 = betamodels.UserProfile.objects.get(first_name="Clayton",last_name="Dunwell")
        comparison = betabackend.getUserUserComparison(user,c1)
        c1.compare = comparison.toJSON()
        c1.result = comparison.result
        dict['c1'] = c1

        dict['userProfile'] = user
        setPageTitle("lovegov: match2",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/match/match-social-network.html', dict, request)
            url = '/match/'
            rebind = 'match-new'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            dict['section'] = 'social'
            return renderToResponseCSRF(template='deployment/pages/match/match-new.html', dict=dict, request=request)


    if request.method == 'GET':
        if 'section' in request.GET:
            section = request.GET['section']
            if section == "social": return social(request,dict)
            elif section == "election": return election(request,dict)
            elif section == "cause":
                pass
            else:
                pass
        else:
            return election(request,dict)
    else:
        pass










#-----------------------------------------------
# helper for content-detail
#-----------------------------------------------------------------------------------------------------------------------
def contentDetail(request, content, dict):
    rightSideBar(request, dict)
    dict['thread_html'] = makeThread(request, content, dict['user'])
    dict['topic'] = content.getMainTopic()
    dict['content'] = content
    creator = content.getCreator()
    dict['creator'] = creator
    dict['iown'] = (creator == dict['user'])

#-----------------------------------------------------------------------------------------------------------------------
# displays a list of all questions of that topic, along with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def topicDetail(request, topic_alias=None, dict={}):
    if not topic_alias:
        return HttpResponse("list of all topics")
    else:
        topic = betamodels.Topic.objects.get(alias=topic_alias)
        contentDetail(request, topic.getForum(), dict)
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/topic_detail.html', dict, request)

#-----------------------------------------------------------------------------------------------------------------------
# detail of petition with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def petitionDetail(request, p_id, dict={}):
    petition = betamodels.Petition.objects.get(id=p_id)
    dict['pageTitle'] = "lovegov: " + petition.title
    dict['petition'] = petition
    signers = petition.getSigners()
    dict['signers'] = signers
    dict['i_signed'] = (dict['user'] in signers)
    contentDetail(request=request, content=petition, dict=dict)
    setPageTitle("lovegov: " + petition.title,dict)
    if request.is_ajax():
        html = ajaxRender('deployment/center/petition_detail.html', dict, request)
        url = '/petition/' + str(petition.id)
        rebind = 'petition'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/petition_detail.html', dict, request)

#-----------------------------------------------------------------------------------------------------------------------
# detail of news with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def newsDetail(request, n_id, dict={}):
    news = betamodels.News.objects.get(id=n_id)
    dict['pageTitle'] = "lovegov: " + news.title
    dict['news'] = news
    contentDetail(request=request, content=news, dict=dict)
    setPageTitle("lovegov: " + news.title,dict)
    if request.is_ajax():
        html = ajaxRender('deployment/center/news_detail.html', dict, request)
        url = '/news/' + str(news.id)
        rebind = 'news'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/news_detail.html', dict, request)

#-----------------------------------------------------------------------------------------------------------------------
# detail of question with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def questionDetail(request, q_id=-1, dict={}):
    if q_id==-1:
        question = getNextQuestion(request, dict)
        if question:
            q_id=question.id
        else:
            return HttpResponse("Congratulations, you have answered every question!")
    dictQuestion(request, q_id, dict)
    dict['pageTitle'] = "lovegov: " + dict['question'].question_text
    if request.is_ajax():
        html = ajaxRender('deployment/center/question_detail.html', dict, request)
        url = dict['question'].get_url()
        rebind = 'question'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/question_detail.html', dict, request)

def dictQuestion(request, q_id, dict={}):
    user = dict['user']
    question = betamodels.Question.objects.filter(id=q_id)[0]
    contentDetail(request=request, content=question, dict=dict)
    dict['question'] = question
    my_response = user.getView().responses.filter(question=question)
    if my_response:
        dict['response']=my_response[0]
    answers = []
    agg = betabackend.getLoveGovGroupView().filter(question=question)
    # get aggregate percentages for answers
    if agg:
        agg = agg[0].aggregateresponse
    for a in question.answers.all():
        if agg:
            tuple = agg.responses.get(answer_val=a.value)
            if agg.total:
                percent = int(100*float(tuple.tally)/float(agg.total))
            else:
                percent = 0
        else:
            percent = 0
        answers.append(AnswerClass(a.answer_text, a.value, percent))
    dict['answers'] = answers
    topic_text = question.topics.all()[0].topic_text
    dict['topic_img_ref'] = betaconstants.MAIN_TOPICS_IMG[topic_text]
    dict['topic_color'] = betaconstants.MAIN_TOPICS_COLORS[topic_text]['light']

class AnswerClass:
    def __init__(self, text, value, percent):
        self.text = text
        self.value = value
        self.percent = percent

#-----------------------------------------------------------------------------------------------------------------------
# Creates the html for a comment thread.
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, user, depth=0, user_votes=None, user_comments=None):
    """Creates the html for a comment thread."""
    if not user_votes:
        user_votes = betamodels.Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = betamodels.Comment.objects.filter(creator=user)
    comments = betamodels.Comment.objects.filter(on_content=object).order_by('-status')
    if comments:
        to_return = "<div>"     # open list
        for c in comments:
            my_vote = user_votes.filter(content=c) # check if i like comment
            if my_vote:
                i_vote = my_vote[0].value
            else: i_vote = 0
            i_own = user_comments.filter(id=c.id) # check if i own comment
            dict = {'comment': c,
                    'my_vote': i_vote,
                    'owner': i_own,
                    'votes': c.upvotes - c.downvotes,
                    'creator': c.getCreator(),
                    'margin': 30*(depth+1),
                    'width': 690-(30*depth+1)-30}
            try:
                comp = betabackend.getUserUserComparison(user, c.getCreator())  # get percent similar
            except AttributeError:
                comp = None
            if comp:
                dict['sim_percent'] = comp.result
            dict['defaultImage'] = betabackend.getDefaultImage().image
            context = RequestContext(request,dict)
            template = loader.get_template('deployment/snippets/cath_comment.html')
            comment_string = template.render(context)  # render comment html
            to_return += comment_string
            to_return += makeThread(request,c,user,depth+1,user_votes,user_comments)    # recur through children
        to_return += "</div>"   # close list
        return to_return
    else:
        return ''

#-----------------------------------------------------------------------------------------------------------------------
# sensibly redirects to next question
#-----------------------------------------------------------------------------------------------------------------------
def nextQuestion(request, dict={}):
    question = getNextQuestion(request, dict)
    dictQuestion(request, question.id, dict)
    setPageTitle("lovegov: " + question.question_text,dict)
    if request.is_ajax():
        html = ajaxRender('deployment/center/question_detail.html', dict, request)
        url = question.get_url()
        rebind = 'question'
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
        return HttpResponse(json.dumps(to_return))
    else:
        frame(request, dict)
        return renderToResponseCSRF('deployment/pages/question_detail.html', dict, request)

def getNextQuestion(request, dict={}):
    user = dict['user']
    responses = user.getView().responses
    answered_ids = responses.values_list('question__id', flat=True)
    unanswered = betamodels.Question.objects.exclude(id__in=answered_ids)
    if unanswered:
        return random.choice(unanswered)
    else:
        question = betamodels.Question.objects.all()
        return random.choice(question)

#-----------------------------------------------------------------------------------------------------------------------
# modify account, change password
#-----------------------------------------------------------------------------------------------------------------------
def account(request, dict={}):
    user = dict['user']
    dict['userProfile'] = user
    dict['uploadform'] = betaforms.UploadFileForm()
    if request.method == 'GET':
        dict['password_form'] = betaforms.PasswordForm()
        dict['uploadform'] = betaforms.UploadFileForm()
        setPageTitle("lovegov: account",dict)
        if request.is_ajax():
            html = ajaxRender('deployment/center/account.html', dict, request)
            url = '/account/'
            rebind = 'account'
            to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':dict['pageTitle']}
            return HttpResponse(json.dumps(to_return))
        else:
            frame(request, dict)
            return renderToResponseCSRF('deployment/pages/account.html', dict, request)
    elif request.method == 'POST':
        if request.POST['box'] == 'password':
            password_form = betaforms.PasswordForm(request.POST)
            if password_form.process(request):
                message = "You successfully changed your password. We sent you an email for your records."
            else:
                message = "Either the two new passwords you entered were not the same, "\
                          "or your old password was incorrect. Try again?"
            dict['pass_message'] = message
            dict['password_form'] = password_form
        elif request.POST['box'] == 'pic' and 'image' in request.FILES:
            try:
                file_content = ContentFile(request.FILES['image'].read())
                Image.open(file_content)
                user.setProfileImage(file_content)
                dict['pic_message'] = "You look great!"
            except IOError:
                dict['pic_message'] = "The image upload didn't work. Try again?"
                dict['uploadform'] = betaforms.UploadFileForm(request.POST)
        else:
            pass
        return renderToResponseCSRF('deployment/pages/account.html', dict, request)


#-----------------------------------------------------------------------------------------------------------------------
# facebook accept
#-----------------------------------------------------------------------------------------------------------------------
def facebookHandle(request, to_page="/web/", dict={}):
    if request.GET['state'] == request.COOKIES['fb_state']: #If this is the correct authorization state
        code = request.GET.get('code') #Get the associated code
        redirect_uri = facebook.getRedirectURI(request,'/fb/handle/') #Set the redirect URI
        access_token = facebook.fbGetAccessToken(request, code, redirect_uri) #Retrieve access token
        auth_to_page = request.COOKIES.get('auth_to_page') #Get the authorization to_page from Cookies
        if auth_to_page: #If it exists
            to_page = auth_to_page #set the to_page
        response = shortcuts.redirect(to_page) #Build a response
        response.set_cookie('fb_token', access_token) #Set the facebook authorization cookie
        if auth_to_page: #If there is an authorization to_page cookie
            response.delete_cookie('auth_to_page') #delete that cookie
        return response
    return shortcuts.redirect(to_page) #If this is the wrong state, go to default to_page

#-----------------------------------------------------------------------------------------------------------------------
# Authorize permission from facebook
# Inputs: GET[ fb_scope , fb_to_page ]
#----------------------------------------------------------------------------------------------------------------------
def facebookAuthorize(request, dict={}, scope="email"):
    auth_to_page = request.GET.get('auth_to_page') #Check for an authorization to_page
    fb_scope = request.GET.get('fb_scope') #Check for a scope
    if fb_scope: #Set the scope if there is one
        scope = fb_scope
    redir = facebook.getRedirectURI(request,'/fb/handle/') #Set the redirect URI
    fb_state = facebook.fbGetRedirect(request , dict , redir , scope) #Get the FB State and FB Link for the auth CODE
    response = shortcuts.redirect( dict['fb_link'] ) #Build a response to get authorization CODE
    response.set_cookie("fb_state", fb_state) #Set facebook state cookie
    if auth_to_page and not request.COOKIES.get('auth_to_page'): #If there is no authorization to_page in Cookies
        response.set_cookie("auth_to_page",auth_to_page) #use the retrieved one if there is one
    return response

def facebookAction(request, to_page="/web/", dict={}):
    fb_action = request.GET.get('fb_action')

    if not fb_action:
        dict['success'] = False
        dict['fb_error'] = '200'

    if fb_action == 'share': #Attempt a wall share!  Share destination (fb_share_to) and message specified in GET
        dict['success'] = facebook.fbWallShare(request, dict) #Wall Share Success Boolean (puts errors in dict[fb_error])
        dict['fb_scope'] = 'email,publish_stream' #Scope Needed if wall share fails
        action_path = request.path #Path for this action
        action_query = '?' + request.META.get('QUERY_STRING').replace("%2F","/") #Query String for this action
        dict['auth_to_page'] = action_path + action_query #Build authorization to_page
        auth_path = '/fb/authorize/' #Path to authorization
        auth_path += '?fb_scope=' + dict['fb_scope'] #Add Queries to authorization path
        dict['fb_auth_path'] = facebook.getRedirectURI( request , auth_path ) #Add authorization path to dictionary

    if request.is_ajax(): #Return AJAX response
        return_dict = { 'success':dict['success'], #Only return important dictionary values
            'fb_auth_path':dict['fb_auth_path'] } #Add authorization path to return dictionary
        if 'fb_error' in dict: #If there's an FB error
            return_dict['fb_error'] = dict['fb_error'] #Add it to the dictionary
        ajax_response = HttpResponse(json.dumps(return_dict)) #Build Ajax Response
        ajax_response.set_cookie('auth_to_page',dict['auth_to_page']) #Add authorization to_page cookie
        return ajax_response
    else: #Return regular response
        action_to_page = request.GET.get('action_to_page') #Look for an action to_page
        if action_to_page: #If there is one
            to_page = action_to_page #Set the to_page as the action to_page
        return shortcuts.redirect(to_page)


#-----------------------------------------------------------------------------------------------------------------------
# learn about our widget
#-----------------------------------------------------------------------------------------------------------------------
def widgetAbout(request, dict={}):
    return HttpResponse("Get our widget!")

#-----------------------------------------------------------------------------------------------------------------------
# Development login, login form for us + nice message for others.
# args: view
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def register(request, to_page='home/', message="", dict={}):
    """register/sign in through facebook or with form"""
    assert dict.get('FACEBOOK_APP_ID'), 'Please specify a facebook app id '\
                                        'and ensure the context processor is enabled'
    dict['login_form'] = betaforms.LoginForm()
    dict['recaptcha'] = betaconstants.RECAPTCHA_PUBLIC
    dict['message'] = message
    return renderToResponseCSRF('deployment/pages/register.html',dict,request)

    """    # checks if user requested to POST information
    if request.method == 'POST':
        if checkRECAPTCHA(request):
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None and user.is_active:
                auth.login(request, user)
                # check if user confirmed
                user_prof = dict['user']
                if user_prof.confirmed:
                    redirect_response = shortcuts.redirect('/' + to_page)
                    redirect_response.set_cookie('privacy', value='PUB')
                    return redirect_response
                else:
                    auth.logout(request)
                    dict['user'] = user_prof
                    return HttpResponse("need confirmation!")
            # else invalid, render login form with errors
            else:
                login_form = betaforms.LoginForm(request.POST)
    # else get request, render blank login form
    else:
        login_form = betaforms.LoginForm()"""

#-----------------------------------------------------------------------------------------------------------------------
# Checks recpatcha if on server, otherwise just returns true (local)
# args: view
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def checkRECAPTCHA(request):
    # check if local
    if LOCAL:
        return True
    # else check captcha
    else:
        return True
        """
        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], constants.RECAPTCHA_PRIVATE, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid is False:
            return False
        else:
            return True
            """

#-----------------------------------------------------------------------------------------------------------------------
# For serving local media
#-----------------------------------------------------------------------------------------------------------------------
def localMedia(request, path, dict={}):
    from django.views.static import serve
    from django.conf import settings
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.isfile(full_path):
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        return shortcuts.redirect('http://www.lovegov.com/' + path)

################################################################################################################### old

#-----------------------------------------------------------------------------------------------------------------------
# displays all questions
#-----------------------------------------------------------------------------------------------------------------------
def alphaTheQuestions(request, dict={}):
    user = dict['user']
    qr = []
    responses = user.getView().responses
    questions = betamodels.Question.objects.all()
    for q in questions:
        r = responses.filter(question=q)
        qr.append((q,r))
    dict['qr'] = qr
    dict['all_questions'] = betamodels.Question.objects.all()
    frame(request, dict)
    return renderToResponseCSRF('deployment/pages/questions_list.html', dict, request)

#-----------------------------------------------------------------------------------------------------------------------
# detail of question with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def alphaQuestionOld(request, q_id, dict={}):
    user = dict['user']
    question = betamodels.Question.objects.filter(id=q_id)[0]
    contentDetail(request=request, content=question, dict=dict)
    dict['question'] = question
    my_response = user.getView().responses.filter(question=question)
    if my_response:
        print "response"
        dict['response']=my_response[0]
        # get agg data
    answers = []
    agg = betabackend.getLoveGovGroupView().filter(question=question)
    if agg:
        agg = agg[0].aggregateresponse
    for a in question.answers.all():
        if agg:
            tuple = agg.responses.get(answer_val=a.value)
            if agg.total:
                percent = int(100*float(tuple.tally)/float(agg.total))
            else:
                percent = 0
        else:
            percent = 0
        answers.append(AnswerClass(a.answer_text, a.value, percent))
    dict['answers'] = answers
    return renderToResponseCSRF('deployment/pages/question_detail.html', dict, request)

