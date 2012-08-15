
########################################################################################################################
########################################################################################################################
#
#           Views
#
#
########################################################################################################################
########################################################################################################################

from django.http import HttpResponse, HttpRequest

# lovegov
from lovegov.modernpolitics.backend import *
from lovegov.settings import UPDATE


#-----------------------------------------------------------------------------------------------------------------------
# Convenience method which returns a simple nice looking message in a frame
#-----------------------------------------------------------------------------------------------------------------------
def basicMessage(request,message,vals={}):
    vals['basic_message'] = message
    url = '/'
    html = ajaxRender('deployment/pages/basic_message.html', vals, request)
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method which is a switch between rendering a page center and returning via ajax or rendering frame.
#-----------------------------------------------------------------------------------------------------------------------
def framedResponse(request, html, url, vals):
    if request.is_ajax():
        to_return = {'html':html, 'url':url, 'title':vals['page_title']}
        return HttpResponse(json.dumps(to_return))
    else:
        vals['center'] = html
        frame(request, vals)
        return renderToResponseCSRF(template='deployment/templates/frame.html', vals=vals, request=request)

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for all views. Requires_login=True if requires login.
#-----------------------------------------------------------------------------------------------------------------------
def viewWrapper(view, requires_login=False):
    """Outer wrapper for all views"""
    def new_view(request, *args, **kwargs):

        vals = {}

        if not checkBrowserCompatible(request):
            return shortcuts.redirect("/upgrade/")

        vals['fb_state'] = fbGetRedirect(request, vals)
        vals['google'] = GOOGLE_LOVEGOV
        host_full = getHostHelper(request)
        vals['host_full'] = host_full
        vals['defaultProfileImage'] = host_full + DEFAULT_PROFILE_IMAGE_URL
        vals['to_page'] = request.path.replace('/login', '')
        vals['page_title'] = "LoveGov: Beta"


        if requires_login:
            try:
                controlling_user = getControllingUser(request)
                vals['controlling_user'] = controlling_user

                # if no ControllingUser (not logged in) return the Anonymous UserProfile, else returns associated user
                if controlling_user:
                    user = controlling_user.user_profile
                    vals['prohibited_actions'] = controlling_user.prohibited_actions
                else:
                    user = getAnonUser()
                    vals['prohibited_actions'] = ANONYMOUS_PROHIBITED_ACTIONS
                vals['user'] = user
                vals['viewer'] = user

                first_login = user.first_login
                vals['firstLoginStage'] = first_login

                # if not authenticated user, and not lovegov_try cookie, redirect to login page
                if user.isAnon() and not request.COOKIES.get('lovegov_try'):
                    return shortcuts.redirect("/login" + request.path)

                # IF NOT DEVELOPER AND IN UPDATE MODE or ON DEV SITE, REDIRECT TO CONSTRUCTION PAGE
                if UPDATE or ("dev" in host_full):
                    if not user.developer:
                        normal_logger.debug('blocked: ' + user.get_name())
                        #return shortcuts.redirect('/underconstruction/')

                if not user.confirmed:
                    return shortcuts.redirect("/need_email_confirmation/")

            except ImproperlyConfigured:
                response = shortcuts.redirect('/login' + request.path)
                response.delete_cookie('sessionid')
                errors_logger.error('deleted cookie')
                return response

        # SAVE PAGE ACCESS, if there isn't specifically set value to log-ignore
        if request.method == 'GET':
            ignore = request.GET.get('log-ignore')
        else:
            ignore = request.POST.get('log-ignore')
        if not ignore:
            def saveAccess(req): PageAccess().autoSave(req)
            thread.start_new_thread(saveAccess, (request,))
        return view(request,vals=vals,*args,**kwargs)

    return new_view

#-----------------------------------------------------------------------------------------------------------------------
# Splash page and learn more.
#-----------------------------------------------------------------------------------------------------------------------
def aliasDowncast(request, alias=None, vals={}):
    if UserProfile.lg.get_or_none(alias=alias):
        return viewWrapper(profile, requires_login=True)(request, alias)
    matched_group = Group.lg.get_or_none(alias=alias)
    if matched_group:
        return viewWrapper(group, requires_login=True)(request, matched_group.id)
    return redirect(request)


def redirect(request):
    return shortcuts.redirect('/home/')

def splash(request):
    return splashForm(request, 'deployment/pages/splash/splash.html')

def learnmore(request):
    return splashForm(request, 'deployment/pages/splash/learnmore.html')

def underConstruction(request):
    return render_to_response('deployment/pages/microcopy/construction.html')

def upgrade(request):
    return render_to_response('deployment/pages/microcopy/upgrade.html')

def continueAtOwnRisk(request):
    response = shortcuts.redirect("/web/")
    response.set_cookie('atyourownrisk', 'yes')
    return response

def splashForm(request,templateURL):
    vals = {}
    if request.method=='POST':
        emailform = EmailListForm(request.POST)
        if emailform.is_valid():
            emailform.save()
            return render_to_response(templateURL, vals, RequestContext(request))
        else:
            return render_to_response(templateURL, vals, RequestContext(request))
    else:
        emailform = EmailListForm()
        vals['emailform'] = emailform
        return render_to_response(templateURL, vals, RequestContext(request))

def postEmail(request):
    if request.method=='POST' and request.POST['email']:
        email = request.POST['email']
        emails = EmailList.objects.filter(email=email)
        if not emails:
            newEmail = EmailList(email=email)
            newEmail.save()
        if request.is_ajax():
            return HttpResponse('+')
        else:
            vals = {'emailMessage':"Thanks! We'll keep you updated!"}
            return renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)
    else:
        return shortcuts.redirect('/comingsoon/')

def blog(request,category=None,number=None,vals=None):
    if request.method == 'GET':

        user = getUserProfile(request)
        if user: vals['viewer'] = user
        else: vals['viewer'] = None

        blogPosts = BlogEntry.objects.all().order_by('-id')
        vals['blogPosts'] = []
        vals['ownBlog'] = False
        vals['categories'] = BlogEntry.CATEGORY_CHOICES
        vals['developers'] = UserProfile.objects.filter(developer=True)

        if number:
            blogPost = BlogEntry.lg.get_or_none(id=number)
            if blogPost:
                vals['blogPost'] = blogPost
                vals['blogPosts'] = blogPosts
                return renderToResponseCSRF('deployment/pages/blog/blog.html',vals=vals,request=request)
        elif category:
            if string.capitalize(category) in BlogEntry.CATEGORY_CHOICES:
                for blogPost in blogPosts:
                    if string.capitalize(category) in blogPost.category:
                        vals['blogPosts'].append(blogPost)
            else:
                creator = UserProfile.objects.get(alias=category)
                vals['ownBlog'] = creator == user
                vals['blogPosts'] = blogPosts.filter(creator=creator)
        else:
            vals['blogPosts'] = blogPosts

        return renderToResponseCSRF('deployment/pages/blog/blog.html',vals=vals,request=request)

#-----------------------------------------------------------------------------------------------------------------------
# Alpha login page.
#-----------------------------------------------------------------------------------------------------------------------
def login(request, to_page='web/', message="", vals={}):
    """
    Handles logging a user into LoveGov

    @param request:
    @type request: HttpRequest
    @param to_page:
    @param vals:
    @type vals: dictionary
    @return:
    """

    if not vals.get('firstLoginStage'):
        to_page = "match/representatives/"

    # Try logging in with facebook
    if fbLogin(request,vals,refresh=True):
        # to_page = to_page.replace("/login", "")
        # print ("to_page: " + to_page)
        return shortcuts.redirect('/' + to_page)

    # Try logging in with twitter
    twitter = twitterLogin(request, "/" + to_page, vals)
    if twitter:
        return twitter

    # Check for POST logins (LOGINS WITHOUT FACEBOOK) and build a response
    if request.method == 'POST' and 'button' in request.POST:
        response = loginPOST(request,to_page,message,vals)

    else: # Otherwise load the login page
        vals.update( {"registerform":RegisterForm(), "username":'', "error":'', "state":'fb'} )
        response = renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)
    response.delete_cookie('lovegov_try')
    return response

def loginAuthenticate(request,user,to_page=''):
    auth.login(request, user)
    redirect_response = shortcuts.redirect('/' + to_page)
    redirect_response.set_cookie('privacy', value='PUB')
    return redirect_response

def loginPOST(request, to_page='web',message="",vals={}):
    vals['registerform'] = RegisterForm()

    # LOGIN via POST
    if request.POST['button'] == 'login':
        # Authenticate user
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

        if user: # If the user authenticated
            user_prof = getUserProfile(control_id=user.id)
            if not user_prof: # If the controlling user has no profile, we're boned
                error = 'Your account is currently broken.  Our developers have been notified and your account should be fixed soon.'
            elif user_prof.confirmed: # Otherwise log this bitch in motherfuckas
                return loginAuthenticate(request,user,to_page)
            else: # If they can't authenticate, they probably need to validate
                error = 'Your account has not been validated yet. Check your email for a confirmation link.  It might be in your spam folder.'
        else: # Otherwise they're just straight up not in our database
            error = 'Invalid Login/Password'
        # Return whatever error was found
        vals.update({"login_email":request.POST['username'], "message":message, "error":error, "state":'login_error'})
        return renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)

    # REGISTER via POST
    elif request.POST['button'] == 'register':
        # Make the register form
        registerform = RegisterForm(request.POST)
        if registerform.is_valid():
            registerform.save()
            vals.update({"fullname":registerform.cleaned_data.get('fullname'), "email":registerform.cleaned_data.get('email'), 'zip':registerform.cleaned_data.get('zip')})
            return renderToResponseCSRF(template='deployment/pages/login/login-main-register-success.html', vals=vals, request=request)
        else:
            vals.update({"registerform":registerform, "state":'register_error'})
            return renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)

    elif request.POST['button'] == 'post-twitter':
        return twitterRegister(request, vals)

    # RECOVER via POST
    elif request.POST['button'] == 'recover':
        user = ControllingUser.lg.get_or_none(username=request.POST['username'])
        if user: resetPassword(user)
        message = u"This is a temporary recovery system! Your password has been reset. Check your email for your new password, you can change it from the account settings page after you have logged in."
        return HttpResponse(json.dumps(message))

def passwordRecovery(request,confirm_link=None, vals={}):

    # new password recovery request
    if request.method == 'POST' and "email" in request.POST:
        ResetPassword.create(username=request.POST['email'])
        msg = u"Check your email for instructions to reset your password."
        if request.is_ajax(): return HttpResponse(json.dumps({'message': msg}))
        else: return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password.html",vals=vals.update({'message':msg}),request=request)

    # else following link to actual password recovery page
    else:
        if confirm_link is not None:
            confirm = ResetPassword.lg.get_or_none(email_code=confirm_link)
            if confirm:
                vals['recoveryForm'] = RecoveryPassword()
                if request.POST:
                    recoveryForm = RecoveryPassword(request.POST)
                    if recoveryForm.is_valid():
                        username = recoveryForm.save(confirm_link)
                        user = auth.authenticate(username=username, password=recoveryForm.cleaned_data.get('password1'))
                        if user: return loginAuthenticate(request,user)
                    else:
                        vals['recoveryForm'] = recoveryForm
                        return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password-reset.html",vals=vals,request=request)
                else: return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password-reset.html",vals=vals,request=request)
        return renderToResponseCSRF(template="deployment/pages/login/login-forgot-password.html",vals=vals,request=request)

def logout(request, vals={}):
    auth.logout(request)
    response = shortcuts.redirect('/login/web/')
    response.delete_cookie('fb_token')
    response.delete_cookie('twitter_access_token')
    return response

def confirm(request, to_page='home', message="", confirm_link=None,  vals={}):

    redirect = ifConfirmedRedirect(request)
    if redirect: return redirect

    user = UserProfile.lg.get_or_none(confirmation_link=confirm_link)
    if user:
        user.confirmed = True
        user.save()
        vals['viewer'] = user
    if request.method == 'GET':
        return renderToResponseCSRF('deployment/pages/login/login-main-register-confirmation.html', vals=vals, request=request)
    else:
        return loginPOST(request,'/home/',message,vals)

def needConfirmation(request, vals={}):

    redirect = ifConfirmedRedirect(request)
    if redirect: return redirect

    vals['confirmation_message'] =         'Your account has not been validated yet. '\
                                           'Check your email for a confirmation link.  '\
                                           'It might be in your spam folder.'
    vals['state'] = 'need-confirmation'
    return renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)

#-----------------------------------------------------------------------------------------------------------------------
# gets frame values and puts in dictionary.
#-----------------------------------------------------------------------------------------------------------------------
def frame(request, vals):
    userProfile = vals['viewer']
    vals['new_notification_count'] = userProfile.getNumNewNotifications()
    vals['firstLogin'] = userProfile.checkFirstLogin()


#-----------------------------------------------------------------------------------------------------------------------
# gets values for right side bar and puts in dictionary
#-----------------------------------------------------------------------------------------------------------------------
def rightSideBar(request, vals):
    userProfile = vals['viewer']
    vals['questions_dict'] = getQuestionsDictionary(questions=getOfficialQuestions(vals), vals=vals)
    getMainTopics(vals)

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses to questions
#-----------------------------------------------------------------------------------------------------------------------
def getUserResponses(request,vals={}):
    userProfile = vals['viewer']
    vals['qr'] = userProfile.getUserResponses()

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses proper format for web
#-----------------------------------------------------------------------------------------------------------------------
def getUserWebResponsesJSON(request,vals={},webCompare=False):

    questionsArray = {}
    topics = getMainTopics(vals)
    for t in topics:
        questionsArray[t.topic_text] = []

    for (question,response) in vals['viewer'].getUserResponses():
        answerArray = []
        for answer in question.answers.all():
            if response and (not webCompare or response.privacy == "PUB"):
                checked = (answer.value == response.answer_val)
                weight = response.weight
            else:
                checked = False
                weight = 5
            answer = {'answer_text':answer.answer_text,'answer_value':answer.value,'user_answer':checked,'weight':weight}
            answerArray.append(answer)
        toAddquestion = {'id':question.id,'text':question.question_text,'answers':answerArray,'user_explanation':"",'childrenData':[]}
        if response: toAddquestion['user_explanation'] = response.downcast().explanation
        if not webCompare and response: toAddquestion['security'] = response.privacy
        else: toAddquestion['security'] = ""
        questionsArray[question.getMainTopic().topic_text].append(toAddquestion)
    vals['questionsArray'] = json.dumps(questionsArray)

#-----------------------------------------------------------------------------------------------------------------------
# This is the view that generates the QAWeb
#-----------------------------------------------------------------------------------------------------------------------
def web(request, vals={}):
    """
    This is the view that generates the QAWeb

    @param request: the request from the user to the server containing metadata about the request
    @type request: HttpRequest
    @param vals: the dictionary of values to pass into the template
    @type vals: dictionary
    @return:
    """
    if request.method == 'GET':
        getUserWebResponsesJSON(request,vals)
        vals['firstLogin'] = vals['viewer'].checkFirstLogin()
        html = ajaxRender('deployment/pages/qaweb/qaweb.html', vals, request)
        url = '/web/'
        return framedResponse(request, html, url, vals)
    if request.method == 'POST':
        if request.POST['action']:
            return answer(request, vals)
        else:
            return shortcuts.redirect('/alpha/')


def compareWeb(request,alias=None,vals={}):
    """
    This is the view that generates the QAWeb

    @param request: the request from the user to the server containing metadata about the request
    @type request: HttpRequest
    @param vals: the dictionary of values to pass into the template
    @type vals: dictionary
    @return: HttpResponse
    """
    if request.method == 'GET':
        if alias:
            user = vals['viewer']
            getUserWebResponsesJSON(request,vals=vals)
            vals['userAnswers'] = vals['questionsArray']

            tempvals = {}
            tempvals['viewer'] = UserProfile.objects.get(alias=alias)
            comparison, json = user.getComparisonJSON(tempvals['viewer'])
            vals['json'] = json
            getUserWebResponsesJSON(request,vals=tempvals,webCompare=True)
            vals['questionsArray'] = tempvals['questionsArray']                     # populates questionsArray with user from profile page that you are looking at.
            vals['compareUserProfile'] = tempvals['viewer']

            html = ajaxRender('deployment/pages/qaweb/qaweb-temp.html', vals, request)
            url = '/profile/web/' + alias + '/'
            return framedResponse(request, html, url, vals)
    if request.method == 'POST':
        if request.POST['action']:
            return answer(request, vals)
        else:
            return shortcuts.redirect('/alpha/')


#-----------------------------------------------------------------------------------------------------------------------
# new feeds page
#-----------------------------------------------------------------------------------------------------------------------
def theFeed(request, vals={}):

    rightSideBar(request, vals)
    shareButton(request, vals)

    viewer = vals['viewer']

    filter_name = request.GET.get('filter_name')
    if not filter_name:
        filter_name = 'default'

    feed_json = {'ranking': 'N',
                 'levels':[],
                 'topics':[],
                 'types':[],
                 'groups':[],
                 'submissions_only': 1,
                 'display': 'L',
                 'feed_start': 0,
                 'filter_name': filter_name}

    vals['feed_json'] = json.dumps(feed_json)
    vals['my_filters'] = viewer.my_filters.all().order_by("created_when")
    vals['num_pinterest'] = range(3)

    html = ajaxRender('deployment/pages/feed/feed.html', vals, request)
    url = '/home/'
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# page to display all of your friends comparisons
#-----------------------------------------------------------------------------------------------------------------------
def iFollow(request, vals={}):

    viewer = vals['viewer']

    group = viewer.i_follow
    vals['ifollow'] = group

    friends = list(viewer.getIFollow())
    for x in friends:
        comparison = x.getComparison(viewer)
        x.result = comparison.result
    friends.sort(key=lambda x:x.result,reverse=True)
    vals['friends'] = friends

    loadHistogram(5, group.id, 'mini', vals=vals)

    html = ajaxRender('deployment/pages/match/friends.html', vals, request)
    url = '/friends/'
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# page to display all of your groups
#-----------------------------------------------------------------------------------------------------------------------
def groups(request, vals={}):

    viewer = vals['viewer']

    mygroups = viewer.getUserGroups()
    vals['mygroups'] = mygroups

    mygroups_ids = mygroups.values_list("id", flat=True)
    groups = list(UserGroup.objects.all())
    groups = random.sample(groups, min(10, len(groups)))
    for x in groups:
        x.prepComparison(viewer)
        x.you_are_member = (x.id in mygroups_ids)
    groups.sort(key=lambda x:x.result,reverse=True)
    vals['groups'] = groups

    vals['what'] = "Groups"

    html = ajaxRender('deployment/pages/match/groups.html', vals, request)
    url = '/groups/'
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# page to display all of your networks
#-----------------------------------------------------------------------------------------------------------------------
def networks(request, vals={}):

    viewer = vals['viewer']

    mygroups = viewer.getNetworks()
    vals['mygroups'] = mygroups

    mygroups_ids = mygroups.values_list("id", flat=True)
    groups = list(Network.objects.all())
    groups = random.sample(groups, min(10, len(groups)))
    for x in groups:
        x.prepComparison(viewer)
        x.you_are_member = (x.id in mygroups_ids)
    groups.sort(key=lambda x:x.result,reverse=True)
    vals['groups'] = groups

    vals['what'] = "Networks"

    html = ajaxRender('deployment/pages/match/groups.html', vals, request)
    url = '/networks/'
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Profile Link
#-----------------------------------------------------------------------------------------------------------------------
def profile(request, alias=None, vals={}):
    viewer = vals['viewer']
    if request.method == 'GET':
        if alias:
            frame(request, vals)
            getUserResponses(request,vals)
            # get comparison of person you are looking at
            user_prof = UserProfile.objects.get(alias=alias).downcast()
            comparison, json = user_prof.getComparisonJSON(viewer)
            vals['user_prof'] = user_prof
            vals['comparison'] = comparison
            vals['json'] = json

            # Get users followers
            if user_prof.user_type == "U":
                prof_follow_me = list(user_prof.getFollowMe())
                for follow_me in prof_follow_me:
                    comparison = getUserUserComparison(user_prof, follow_me)
                    follow_me.compare = comparison.toJSON()
                    follow_me.result = comparison.result
                prof_follow_me.sort(key=lambda x:x.result,reverse=True)
                vals['prof_follow_me'] = prof_follow_me[0:5]
            else:       # get politician supporters
                user_prof = user_prof.downcast()
                prof_support_me = user_prof.getSupporters()
                vals['prof_support_me'] = prof_support_me[0:5]


            num_groups = GROUP_INCREMENT
            vals['prof_groups'] = user_prof.getUserGroups(num=num_groups)
            vals['num_groups'] = num_groups

            # Get user's random 5 groups
            #vals['prof_groups'] = user_prof.getGroups(5)

            # Get Follow Requests
            vals['prof_requests'] = list(user_prof.getFollowRequests())
            vals['prof_invites'] = list(user_prof.getGroupInvites())

            # Get Schools and Locations:
            networks = user_prof.networks.all()
            vals['prof_locations'] = networks.filter(network_type='L')
            vals['prof_schools'] = networks.filter(network_type='S')
            vals['prof_parties'] = user_prof.parties.all()

            vals['is_following_you'] = False
            if viewer.id != user_prof.id:
                following_you = UserFollow.lg.get_or_none( user=user_prof, to_user=viewer )
                if following_you and following_you.confirmed:
                    vals['is_following_you'] = True

            # Is the current user already (requesting to) following this profile?
            vals['is_user_requested'] = False
            vals['is_user_confirmed'] = False
            vals['is_user_rejected'] = False
            user_follow = UserFollow.lg.get_or_none(user=viewer,to_user=user_prof)
            if user_follow:
                if user_follow.requested:
                    vals['is_user_requested'] = True
                if user_follow.confirmed:
                    vals['is_user_confirmed'] = True
                if user_follow.rejected:
                    vals['is_user_rejected'] = True

            # Get Activity
            num_actions = NOTIFICATION_INCREMENT
            actions = user_prof.getActivity(num=num_actions)
            actions_text = []
            for action in actions:
                actions_text.append( action.getVerbose(view_user=viewer) )
            vals['actions_text'] = actions_text
            vals['num_actions'] = num_actions

            # Get Notifications
            if viewer.id == user_prof.id:
                notifications_text = []

                num_notifications = NOTIFICATION_INCREMENT
                notifications = viewer.getNotifications(num=num_notifications)
                for notification in notifications:
                    notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )

                vals['notifications_text'] = notifications_text
                vals['num_notifications'] = num_notifications

            # get politician page values
            if user_prof.user_type != "U":
                supported = Supported.lg.get_or_none(user=viewer, to_user=user_prof)
                if supported:
                    vals['yousupport'] = supported.confirmed

            # get responses
            vals['responses'] = user_prof.getView().responses.count()
            html = ajaxRender('deployment/pages/profile/profile.html', vals, request)
            url = '/profile/' + alias
            return framedResponse(request, html, url, vals)
        else:
            return shortcuts.redirect('/profile/' + viewer.alias)
    else:
        if request.POST['action']:
            return answer(request, vals)
        else:
            to_alias = request.POST['alias']
            return shortcuts.redirect('/alpha/' + to_alias)

#-----------------------------------------------------------------------------------------------------------------------
# Network page
#-----------------------------------------------------------------------------------------------------------------------
def network(request, alias=None, vals={}):
    if not alias:
        user = vals['viewer']
        return shortcuts.redirect(user.getNetwork().get_url())
    network = Network.lg.get_or_none(alias=alias)
    if not network:
        vals['basic_message'] = "No network matches the given network ID"
        html = ajaxRender('deployment/pages/basic_message.html', vals, request)
        url = '/network/' + alias + '/'
        return framedResponse(request, html, url, vals)
    return group(request,g_id=network.id,vals=vals)

#-----------------------------------------------------------------------------------------------------------------------
# Group page
#-----------------------------------------------------------------------------------------------------------------------
def group(request, g_id=None, vals={}):

    viewer = vals['viewer']

    if not g_id:
        return HttpResponse('Group id not provided to view function')
    group = Group.lg.get_or_none(id=g_id)
    if not group:
        return HttpResponse('Group id not found in database')

    vals['group'] = group
    comparison, json = group.getComparisonJSON(viewer)
    vals['comparison'] = comparison
    vals['json'] = json

    loadHistogram(5, group.id, 'mini', increment=5, vals=vals)

    # Get Follow Requests
    vals['group_requests'] = list(group.getFollowRequests())

    # Get Activity
    num_actions = NOTIFICATION_INCREMENT
    actions = group.getActivity(num=num_actions)
    actions_text = []
    for action in actions:
        actions_text.append( action.getVerbose(view_user=viewer) )
    vals['actions_text'] = actions_text
    vals['num_actions'] = num_actions

    # Is the current viewer already (requesting to) following this group?
    vals['is_user_follow'] = False
    vals['is_user_confirmed'] = False
    vals['is_user_rejected'] = False
    vals['is_visible'] = False
    group_joined = GroupJoined.lg.get_or_none(user=viewer,group=group)
    if group_joined:
        if group_joined.confirmed:
            vals['is_visible'] = True
        if group_joined.requested:
            vals['is_user_follow'] = True
        if group_joined.confirmed:
            vals['is_user_confirmed'] = True
        if group_joined.rejected:
            vals['is_user_rejected'] = True

    if not group.group_privacy == 'S':
        vals['is_visible'] = True

    if group == viewer.i_follow:
        vals['is_visible'] = True

    vals['is_user_admin'] = False
    admins = list( group.admins.all() )
    for admin in admins:
        if admin.id == viewer.id:
            vals['is_user_admin'] = True
    vals['group_admins'] = group.admins.all()

    all_members = list(group.getMembers())
    num_members = MEMBER_INCREMENT
    vals['group_members'] = all_members[:num_members]
    vals['num_members'] = num_members

    vals['num_group_members'] = group.num_members

    followers = list(viewer.getFollowMe())
    for member in all_members:
        if member in followers:
            followers.remove(member)

    vals['non_member_followers'] = followers

    html = ajaxRender('deployment/pages/group/group.html', vals, request)
    url = group.get_url()
    return framedResponse(request, html, url, vals)

def histogramDetail(request, g_id, vals={}):

    viewer = vals['viewer']
    group = Group.objects.get(id=g_id)

    vals['group'] = group
    getMainTopics(vals)

    loadHistogram(20, group.id, 'full', vals=vals)

    html = ajaxRender('deployment/pages/histogram/histogram.html', vals, request)
    url = group.getHistogramURL()
    return framedResponse(request, html, url, vals)


def loadHistogram(resolution, g_id, which, increment=1, vals={}):
    bucket_list = getBucketList(resolution)
    vals['buckets'] = bucket_list
    bucket_uids = {}
    for x in bucket_list:
        bucket_uids[x] = []
    histogram_metadata = {'total':0,
                          'identical':0,
                          'identical_uids':[],
                          'resolution':resolution,
                          'g_id':g_id,
                          'which':which,
                          'increment':increment,
                          'topic_alias':'all',
                          'bucket_uids': bucket_uids,
                          'current_bucket': -1 }
    vals['histogram_metadata'] = json.dumps(histogram_metadata)


#-----------------------------------------------------------------------------------------------------------------------
# About Link
#-----------------------------------------------------------------------------------------------------------------------
def about(request, start="video", vals={}):
    if request.method == 'GET':
        vals['start_page'] = start
        developers = UserProfile.objects.filter(developer=True).order_by('id')
        developers = developers.reverse()
        skew = 185
        side = 110
        main_side = 165
        offset = 450
        angle_offset = math.pi/3
        for num in range(0,len(developers)):
            angle = 2.0*math.pi*(float(num)/float(len(developers)))+angle_offset
            cosine = math.cos(angle)
            sine = math.sin(angle)
            developers[num].x = int(cosine*skew)+(offset/2)-(side/2)
            developers[num].y = int(sine*skew)+skew
            developers[num].angle = math.degrees(angle)-180
            developers[num].x2 = int(cosine*skew/2)+(offset/2)-(side/2)
            developers[num].y2 =  int(sine*skew/2)+(offset/2)-(side/2)
        vals['developers'] = developers
        vals['side'] = side
        vals['skew'] = skew
        vals['side_half'] = side/2
        vals['main_side'] = main_side
        vals['main_side_half'] = main_side/2
        vals['x'] = (offset-main_side)/2
        vals['y'] = skew - ((main_side-side)/2)
        vals['colors'] = MAIN_TOPIC_COLORS_LIST
        vals['colors_cycle'] = ["who-are-we-circle-div-green", "who-are-we-circle-div-blue","who-are-we-circle-div-yellow", "who-are-we-circle-div-purple", "who-are-we-circle-div-pink", "who-are-we-circle-div-orange", "who-are-we-circle-div-teal"]

        html = ajaxRender('deployment/pages/about/about.html', vals, request)
        url = '/about/'
        return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Legislation-related pages
#-----------------------------------------------------------------------------------------------------------------------

def legislation(request, session=None, type=None, number=None, vals={}):
    vals['session'], vals['type'], vals['number'] = session, type, number
    if session==None:
        vals['sessions'] = [x['bill_session'] for x in Legislation.objects.values('bill_session').distinct()]
        return renderToResponseCSRF(template='deployment/pages/legislation/legislation.html', vals=vals, request=request)
    legs = Legislation.objects.filter(bill_session=session)
    if type==None:
        type_list = [x['bill_type'] for x in Legislation.objects.filter(bill_session=session).values('bill_type').distinct()]
        vals['types'] = [(x, BILL_TYPES[x]) for x in type_list]
        return renderToResponseCSRF(template='deployment/pages/legislation/legislation-session.html', vals=vals, request=request)
    if number==None:
        vals['numbers'] = [x['bill_number'] for x in Legislation.objects.filter(bill_session=session, bill_type=type).values('bill_number').distinct()]
        return renderToResponseCSRF(template='deployment/pages/legislation/legislation-type.html', vals=vals, request=request)
    legs = Legislation.objects.filter(bill_session=session, bill_type=type, bill_number=number)
    if len(legs)==0:
        vals['error'] = "No legislation found with the given parameters."
    else:
	leg = legs[0]
        vals['leg_titles'] = leg.legislationtitle_set.all()
        vals['leg'] = leg
    return renderToResponseCSRF(template='deployment/pages/legislation/legislation-view.html', vals=vals, request=request)


#-----------------------------------------------------------------------------------------------------------------------
# Match page.
#-----------------------------------------------------------------------------------------------------------------------
def newMatch(request,start='presidential', vals={}):

    sections = {'presidential':0,
                'senate':1,
                'social':2,
                'representatives':3,
                'news':4}
    vals['start_sequence'] = sections[start]

    viewer = vals['viewer']
    comparison, json = viewer.getComparisonJSON(viewer)
    viewer.compare = json
    viewer.result = comparison.result

    matchSocial(request, vals)
    matchPresidential(request, vals)
    matchSenate(request, vals)
    matchRepresentatives(request, vals)
    matchNews(request, vals)

    html = ajaxRender('deployment/pages/match/match-new.html', vals, request)
    url = "/match/"
    return framedResponse(request, html, url, vals)

def matchSocial(request, vals={}):
    viewer = vals['viewer']
    vals['friends'] = viewer.getIFollow(num=6)
    vals['groups'] = viewer.getUserGroups(num=6)
    vals['networks'] = viewer.getNetworks()[:4]

def matchPresidential(request, vals={}):
    viewer = vals['viewer']
    if not LOCAL:
        obama = ElectedOfficial.objects.get(first_name="Barack",last_name="Obama")
        paul = ElectedOfficial.objects.get(first_name="Ronald",last_name="Paul")
        romney = Politician.objects.get(first_name="Mitt",last_name="Romney")
    else:
        obama = viewer
        paul = viewer
        romney = viewer
    list = [obama,paul,romney]
    for x in list:
        x.prepComparison(viewer)

    list.sort(key=lambda x:x.result,reverse=True)
    vals['presidential'] = list

def matchSenate(request, vals={}):
    viewer = vals['viewer']
    if not LOCAL:
        elizabeth = Politician.objects.get(first_name="Elizabeth", last_name="Warren")
        brown = ElectedOfficial.objects.get(first_name="Scott", last_name="Brown")
        voters = getLoveGovGroup()
    else:
        elizabeth = viewer
        brown = viewer
        voters = viewer

    for x in [elizabeth, brown, voters]:
        x.prepComparison(viewer)

    vals['elizabeth'] = elizabeth
    vals['brown'] = brown
    vals['mass'] = voters

def matchRepresentatives(request, vals={}):

    viewer = vals['viewer']
    congressmen = []

    if viewer.location:
        address = viewer.location
        congressmen = []
        representative = Representative.lg.get_or_none(congresssessions=112,state=address.state,district=address.district)
        if representative:
            congressmen.append(representative)
        senators = Senator.objects.filter(congresssessions=112,state=address.state)
        for senator in senators:
            congressmen.append(senator)
        vals['congressmen'] = congressmen
        vals['state'] = address.state
        vals['district'] = address.district
        vals['latitude'] = address.latitude
        vals['longitude'] = address.longitude

    for x in congressmen:
        x.prepComparison(viewer)

    congressmen.sort(key=lambda x:x.result,reverse=True)

    if not congressmen:
        vals['invalid_address'] = True

def matchNews(request, vals):
    viewer = vals['viewer']
    if not LOCAL:
        paul = ElectedOfficial.objects.get(first_name="Paul", last_name="Ryan")
    else:
        paul = viewer
    paul.prepComparison(viewer)
    vals['paul'] = paul

#-----------------------------------------------------------------------------------------------------------------------
# helper for content-detail
#-----------------------------------------------------------------------------------------------------------------------
def contentDetail(request, content, vals):
    rightSideBar(request, vals)
    shareButton(request, vals)
    vals['thread_html'] = makeThread(request, content, vals['viewer'], vals=vals)
    vals['topic'] = content.getMainTopic()
    vals['content'] = content
    viewer = vals['viewer']
    creator_display = content.getCreatorDisplay(viewer)
    vals['creator'] = creator_display
    vals['recent_actions'] = Action.objects.filter(privacy="PUB").order_by('-when')[:5]
    user_votes = Voted.objects.filter(user=vals['viewer'])
    my_vote = user_votes.filter(content=content) 
    if my_vote:
        vals['my_vote'] = my_vote[0].value
    else:
        vals['my_vote'] = 0
    vals['iown'] = (creator_display.you)

#-----------------------------------------------------------------------------------------------------------------------
# displays a list of all questions of that topic, along with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def topicDetail(request, topic_alias=None, vals={}):
    if not topic_alias:
        return HttpResponse("list of all topics")
    else:
        topic = Topic.objects.get(alias=topic_alias)
        contentDetail(request, topic.getForum(), vals)
        frame(request, vals)
        return renderToResponseCSRF('deployment/pages/content/topic_detail.html', vals, request)

#-----------------------------------------------------------------------------------------------------------------------
# detail of petition with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def petitionDetail(request, p_id, vals={}, signerLimit=8):

    petition = Petition.lg.get_or_none(id=p_id)
    if not petition:
        return HttpResponse("This petition does not exist")
    vals['petition'] = petition
    signers = petition.getSigners()
    vals['signers'] = signers[:signerLimit]
    vals['i_signed'] = (vals['viewer'] in signers)
    vals['num_signers'] = len(signers)

    contentDetail(request=request, content=petition, vals=vals)
    html = ajaxRender('deployment/pages/content/petition_detail.html', vals, request)
    url = '/petition/' + str(petition.id)
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of news with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def newsDetail(request, n_id, vals={}):
    news = News.objects.get(id=n_id)
    vals['news'] = news
    contentDetail(request=request, content=news, vals=vals)

    html = ajaxRender('deployment/pages/content/news_detail.html', vals, request)
    url = '/news/' + str(news.id)
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# get share button values
#-----------------------------------------------------------------------------------------------------------------------
def shareButton(request, vals={}):
    viewer = vals['viewer']
    vals['my_followers'] = viewer.getFollowMe()
    groups = viewer.getGroups()
    vals['my_groups'] = groups.filter(group_type="U")
    vals['my_networks'] = groups.filter(group_type="N")


#-----------------------------------------------------------------------------------------------------------------------
# detail of question with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def questionDetail(request, q_id=-1, vals={}):
    if q_id==-1:
        question = getNextQuestion(request, vals)
        if question:
            q_id=question.id
        else:
            return HttpResponse("Congratulations, you have answered every question!")
    valsQuestion(request, q_id, vals)
    user = vals['user']

    html = ajaxRender('deployment/pages/content/question_detail.html', vals, request)
    url = vals['question'].get_url()
    return framedResponse(request, html, url, vals)

def valsQuestion(request, q_id, vals={}):
    user = vals['viewer']
    question = Question.objects.filter(id=q_id)[0]
    contentDetail(request=request, content=question, vals=vals)
    vals['question'] = question
    my_response = user.getView().responses.filter(question=question)
    if my_response:
        vals['response']=my_response[0]
    answers = []
    agg = getLoveGovGroupView().filter(question=question)
    # get aggregate percentages for answers
    if agg:
        agg = agg[0].aggregateresponse
    for a in question.answers.all():
        if agg:
            tuple = agg.responses.filter(answer_val=a.value)
            if tuple and agg.total:
                tuple = tuple[0]
                percent = int(100*float(tuple.tally)/float(agg.total))
            else:
                percent = 0
        else:
            percent = 0
        answers.append(AnswerClass(a.answer_text, a.value, percent))
    vals['answers'] = answers
    topic_text = question.getMainTopic().topic_text
    vals['topic_img_ref'] = MAIN_TOPICS_IMG[topic_text]
    vals['topic_color'] = MAIN_TOPICS_COLORS[topic_text]['light']

class AnswerClass:
    def __init__(self, text, value, percent):
        self.text = text
        self.value = value
        self.percent = percent

#-----------------------------------------------------------------------------------------------------------------------
# Creates the html for a comment thread.
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, user, depth=0, user_votes=None, user_comments=None, vals={}):
    """Creates the html for a comment thread."""
    if not user_votes:
        user_votes = Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = Comment.objects.filter(creator=user)
    comments = Comment.objects.filter(on_content=object).order_by('-status')
    viewer = vals['viewer']
    if comments:
        to_return = ''
        for c in comments:
            if c.active or c.num_comments:
                margin = 30*(depth+1)
                to_return += "<span class='collapse'>[-]</span><div class='threaddiv'>"     # open list
                my_vote = user_votes.filter(content=c) # check if i like comment
                if my_vote:
                    i_vote = my_vote[0].value
                else: i_vote = 0
                i_own = user_comments.filter(id=c.id) # check if i own comment
                vals.update({'comment': c,
                        'my_vote': i_vote,
                        'owner': i_own,
                        'votes': c.upvotes - c.downvotes,
                        'display_name': c.getThreadDisplayName(viewer, getSourcePath(request)),
                        'creator': c.getCreatorDisplay(viewer),
                        'public': c.getPublic(),
                        'margin': margin,
                        'width': 690-(30*depth+1)-30,
                        'defaultImage':getDefaultImage().image,
                        'depth':depth})

                context = RequestContext(request,vals)
                template = loader.get_template('deployment/snippets/cath_comment.html')
                comment_string = template.render(context)  # render comment html
                to_return += comment_string
                to_return += makeThread(request,c,user,depth+1,user_votes,user_comments,vals=vals)    # recur through children
                to_return += "</div>"   # close list
        return to_return
    else:
        return ''

#-----------------------------------------------------------------------------------------------------------------------
# sensibly redirects to next question
#-----------------------------------------------------------------------------------------------------------------------
def nextQuestion(request, vals={}):
    question = getNextQuestion(request, vals)
    valsQuestion(request, question.id, vals)

    html = ajaxRender('deployment/pages/content/question_detail.html', vals, request)
    url = question.get_url()
    return framedResponse(request, html, url, vals)

def getNextQuestion(request, vals={}):
    user = vals['viewer']
    responses = user.getView().responses
    answered_ids = responses.values_list('question__id', flat=True)
    unanswered = Question.objects.exclude(id__in=answered_ids)
    if unanswered:
        return random.choice(unanswered)
    else:
        question = Question.objects.all()
        return random.choice(question)

#-----------------------------------------------------------------------------------------------------------------------
# modify account, change password
#-----------------------------------------------------------------------------------------------------------------------
def account(request, section="", vals={}):
    user = vals['viewer']
    vals['uploadform'] = UploadFileForm()
    vals['parties'] = Party.objects.all()
    vals['user_parties'] = user.parties.all()

    if section == "profile": vals['profile_message'] = " "

    if request.method == 'GET':
        html = ajaxRender('deployment/pages/account/account.html', vals, request)
        url = '/account/'
        return framedResponse(request, html, url, vals)
    elif request.method == 'POST':
        if request.POST['box'] == 'password':
            password_form = PasswordForm(request.POST)
            if password_form.process(request):
                message = "You successfully changed your password. We sent you an email for your records."
            else:
                message = "Failure.  Either the two new passwords you entered were not the same, "\
                          "or you entered your old password incorrectly."
            vals['password_message'] = message
        elif request.POST['box'] == 'profile':
            if 'image' in request.FILES:
                try:
                    file_content = ContentFile(request.FILES['image'].read())
                    Image.open(file_content)
                    user.setProfileImage(file_content)
                    vals['profile_message'] = "You look great!"
                except IOError:
                    vals['profile_message'] = "The image upload didn't work. Try again?"
                    vals['uploadform'] = UploadFileForm(request.POST)


            vals['profile_message'] = " "
        elif request.POST['box'] == 'basic_info':
            pass
        else:
            pass

        html = ajaxRender('deployment/pages/account/account.html', vals, request)
        url = '/account/'
        return framedResponse(request, html, url, vals)


def groupEdit(request, g_id=None, section="", vals={}):
    viewer = vals['viewer']

    if not g_id:
        return basicMessage(request,'Requested group does not exist',vals)

    group = Group.lg.get_or_none(id=g_id)
    if not group:
        return basicMessage(request,'Requested group does not exist',vals)
    vals['group'] = group

    admins = list( group.admins.all() )
    if viewer.id not in map( lambda x : x.id , admins ):
        return basicMessage(request,'You are not an administrator of this group',vals)

    vals['group_admins'] = admins

    all_members = group.getMembers()
    vals['group_members'] = all_members
    members = list( all_members )
    for admin in admins:
        members.remove(admin)
    vals['normal_members'] = members

    vals['uploadform'] = UploadFileForm()

    if section == "profile": vals['profile_message'] = " "

    if request.method == 'GET':
        html = ajaxRender('deployment/pages/group/group_edit.html', vals, request)
        url = '/account/'
        return framedResponse(request, html, url, vals)

    elif request.method == 'POST':
        if request.POST['box'] == 'profile':
            if 'image' in request.FILES:
                try:
                    file_content = ContentFile(request.FILES['image'].read())
                    Image.open(file_content)
                    viewer.setProfileImage(file_content)
                    vals['profile_message'] = "You look great!"
                except IOError:
                    vals['profile_message'] = "The image upload didn't work. Try again?"
                    vals['uploadform'] = UploadFileForm(request.POST)


            vals['profile_message'] = " "
        elif request.POST['box'] == 'basic_info':
            pass
        else:
            pass

        html = ajaxRender('deployment/pages/group/group_edit.html', vals, request)
        url = '/account/'
        return framedResponse(request, html, url, vals)


#-----------------------------------------------------------------------------------------------------------------------
# facebook accept
#-----------------------------------------------------------------------------------------------------------------------
def facebookHandle(request, to_page="/login/home/", vals={}):
    cookie_state = request.COOKIES.get('fb_state')
    returned_state = request.GET.get('state')
    if cookie_state and returned_state == cookie_state: #If this is the correct authorization state
        code = request.GET.get('code') #Get the associated code
        redirect_uri = getRedirectURI(request,'/fb/handle/') #Set the redirect URI

        access_token = fbGetAccessToken(request, code, redirect_uri) #Retrieve access token
        if not access_token: #If there's no access token, it's being logged so return the login page
            return shortcuts.redirect('/login/')

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
def facebookAuthorize(request, vals={}, scope=""):
    auth_to_page = request.GET.get('auth_to_page') #Check for an authorization to_page
    fb_scope = request.GET.get('fb_scope') #Check for a scope
    if fb_scope: #Set the scope if there is one
        scope = fb_scope
    redir = getRedirectURI(request,'/fb/handle/') #Set the redirect URI
    if not scope == "":
        fb_state = fbGetRedirect(request , vals , redir , scope) #Get the FB State and FB Link for the auth CODE
    else:
        fb_state = fbGetRedirect(request , vals , redir) #Get the FB State and FB Link for the auth CODE
    response = shortcuts.redirect( vals['fb_link'] ) #Build a response to get authorization CODE
    response.set_cookie("fb_state", fb_state) #Set facebook state cookie
    if auth_to_page and not request.COOKIES.get('auth_to_page'): #If there is no authorization to_page in Cookies
        response.set_cookie("auth_to_page",auth_to_page) #use the retrieved one if there is one
    return response


def facebookAction(request, to_page="/web/", vals={}):
    fb_action = request.GET.get('fb_action')
    action_path = request.path #Path for this action
    action_query = '?' + request.META.get('QUERY_STRING').replace("%2F","/") #Query String for this action

    if not fbLogin(request,vals):
        vals['success'] = False #If the user cannot login with fb, authorization required
        vals['auth_to_page'] = action_path + action_query #Build authorization to_page (If the user isn't authorized, try authorizing and repeat action)
        vals['fb_auth_path'] = getRedirectURI( request , '/fb/authorize/' ) #Authorize me!

    elif not fb_action:
        vals['success'] = False
        vals['fb_error'] = '200'

    elif fb_action == 'share': #Attempt a wall share!  Share destination (fb_share_to) and message specified in GET
        vals['success'] = fbWallShare(request, vals) #Wall Share Success Boolean (puts errors in vals[fb_error])
        vals['fb_scope'] = 'publish_stream,' + FACEBOOK_SCOPE #Scope Needed if wall share fails
        vals['auth_to_page'] = action_path + action_query #Build authorization to_page
        auth_path = '/fb/authorize/' #Path to authorization
        auth_path += '?fb_scope=' + vals['fb_scope'] #Add Queries to authorization path
        vals['fb_auth_path'] = getRedirectURI( request , auth_path ) #Add authorization path to dictionary

    elif fb_action == 'make_friends':
        vals['success'] = fbMakeFriends(request, vals) #Make Friends Success Boolean (puts errors in vals[fb_error])
        vals['auth_to_page'] = action_path + action_query #Build authorization to_page
        auth_path = '/fb/authorize/' #Path to authorization
        vals['fb_auth_path'] = getRedirectURI( request , auth_path ) #Add authorization path to dictionary

    if request.is_ajax(): #Return AJAX response
        return_vals = { 'success':vals['success'], #Only return important dictionary values
            'fb_auth_path':vals['fb_auth_path'] } #Add authorization path to return dictionary
        if 'fb_error' in vals: #If there's an FB error
            return_vals['fb_error'] = vals['fb_error'] #Add it to the dictionary
        ajax_response = HttpResponse(json.dumps(return_vals)) #Build Ajax Response
        ajax_response.set_cookie('auth_to_page',vals['auth_to_page']) #Add authorization to_page cookie
        return ajax_response

    else: #Return regular response
        if vals['success']:
            action_to_page = request.GET.get('action_to_page') #Look for an action to_page
            if action_to_page: #If there is one
                to_page = action_to_page #Set the to_page as the action to_page
            return shortcuts.redirect(to_page)
        else:
            to_page = vals['fb_auth_path']
            response = shortcuts.redirect(to_page)
            response.set_cookie('auth_to_page',vals['auth_to_page'])
            return response

#-----------------------------------------------------------------------------------------------------------------------
# learn about our widget
#-----------------------------------------------------------------------------------------------------------------------
def widgetAbout(request, vals={}):
    return HttpResponse("Get our widget!")

#-----------------------------------------------------------------------------------------------------------------------
# Search page
#-----------------------------------------------------------------------------------------------------------------------
def search(request, term='', vals={}):
    userProfiles, petitions, questions, news, groups = lovegovSearch(term)
    vals['num_results'] = sum(map(len, (userProfiles, petitions, questions, news, groups)))
    vals['userProfiles'] = userProfiles
    vals['petitions'] = petitions
    vals['questions'] = questions
    vals['news'] = news
    vals['groups'] = groups
    vals['term'] = term
    html = ajaxRender('deployment/pages/search/search.html', vals, request)
    url = '/search/' + term
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Tryin' to love some gov
#-----------------------------------------------------------------------------------------------------------------------
def tryLoveGov(request, to_page="home/", vals={}):
    response = shortcuts.redirect("/" + to_page)
    response.set_cookie('lovegov_try', 1)
    return response

#-----------------------------------------------------------------------------------------------------------------------
# LoveGov API
#-----------------------------------------------------------------------------------------------------------------------


