########################################################################################################################
########################################################################################################################
#
#           Views
#
#
########################################################################################################################
########################################################################################################################

from lovegov.frontend.views_helpers import *

from pprint import pprint

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method which returns a simple nice looking message in a frame
#-----------------------------------------------------------------------------------------------------------------------
def basicMessage(request,message,vals={}):
    vals['basic_message'] = message
    url = '/'
    html = ajaxRender('site/pages/basic_message.html', vals, request)
    return framedResponse(request, html, url, vals)

def errorMessage(request,message,vals={}):
    vals['basic_message'] = message
    url = '/'
    html = ajaxRender('site/pages/basic_message.html', vals, request)
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Convenience method which is a switch between rendering a page center and returning via ajax or rendering frame.
#-----------------------------------------------------------------------------------------------------------------------
def framedResponse(request, html, url, vals={}, rebind="home"):
    if request.is_ajax():
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':vals['page_title']}
        return HttpResponse(json.dumps(to_return))
    else:
        vals['center'] = html
        vals['notifications_num'] = vals['viewer'].getNotifications(new=True).count()
        frame(request, vals)
        return renderToResponseCSRF(template='site/frame/frame.html', vals=vals, request=request)

def homeResponse(request, focus_html, url, vals):
    if request.is_ajax() and request.method == 'POST':
            to_return = {'focus_html':focus_html, 'url':url, 'title':vals['page_title']}
            return HttpResponse(json.dumps(to_return))
    else:
        vals['focus_html'] = focus_html
        homeSidebar(request, vals)
        html = ajaxRender('site/pages/home/home_frame.html', vals, request)
        return framedResponse(request, html, url, vals, rebind="home")

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for all views. Requires_login=True if requires login.
#-----------------------------------------------------------------------------------------------------------------------
def viewWrapper(view, requires_login=False):
    """Outer wrapper for all views"""
    def new_view(request, *args, **kwargs):
        vals = {'STATIC_URL':settings.STATIC_URL}
        try: # Catch all error messages

            # if ie<9 redirect to upgrade page
            if not checkBrowserCompatible(request):
                return shortcuts.redirect("/upgrade/")

            # google analytics
            vals['google'] = GOOGLE_LOVEGOV

            # Error otherwise?
            vals['fb_state'] = fbGetRedirect(request, vals)

            # static file serving and host
            host_full = getHostHelper(request)
            vals['host_full'] = host_full
            if 's3' in settings.DEFAULT_FILE_STORAGE:
                vals['MEDIA_PREFIX'] = settings.MEDIA_URL.replace('/media', '')
            else:
                vals['MEDIA_PREFIX'] = host_full

            # optimization for profile image
            vals['defaultProfileImage'] = host_full + DEFAULT_PROFILE_IMAGE_URL

            # page info
            vals['to_page'] = request.path.replace('/login', '')
            vals['page_title'] = "LoveGov: Beta"

            # helper for key stroke sequences
            vals['sequence'] = [0]

            if requires_login:

                    # who is logged in?
                    controlling_user = getControllingUser(request)
                    vals['controlling_user'] = controlling_user

                    # if no ControllingUser (not logged in) return the Anonymous UserProfile, else returns associated user
                    if controlling_user:
                        user = controlling_user.user_profile
                        vals['prohibited_actions'] = controlling_user.prohibited_actions
                    else:
                        user = getAnonUser()
                        vals['prohibited_actions'] = ANONYMOUS_PROHIBITED_ACTIONS

                    # get user profile associated with controlling user
                    vals['user'] = user
                    vals['viewer'] = user

                    # first login
                    first_login = user.first_login
                    vals['firstLoginStage'] = first_login

                    # if not authenticated user, and not lovegov_try cookie, redirect to login page
                    if user.isAnon() and not request.COOKIES.get('lovegov_try'):
                        # If this action can't be performed without being authenticated
                        if not request.POST.get('action') in UNAUTHENTICATED_ACTIONS:
                            # Redirect to login page
                            return shortcuts.redirect("/login" + request.path)
                        else: # otherwise action can be done without authentication
                            return view(request,vals=vals,*args,**kwargs)

                    # IF NOT DEVELOPER AND IN UPDATE MODE or ON DEV SITE, REDIRECT TO CONSTRUCTION PAGE
                    if UPDATE or ("dev" in host_full):
                        if not user.developer:
                            normal_logger.debug('blocked: ' + user.get_name())
                            return shortcuts.redirect('/underconstruction/')

                    # if user not confirmed redirect to login page
                    if not user.confirmed:
                        return shortcuts.redirect("/need_email_confirmation/")

            # vals for not logged in pages
            else:
                vals['fb_state'] = fbGetRedirect(request, vals)

            # if everything worked, and there wasn't an error, return the view
            return view(request,vals=vals,*args,**kwargs)

        # Any errors caught here
        except LGException as e:
            return errorMessage(request, message=e.getClientMessage(), vals=vals)

        finally:  # save page access, if there isn't specifically set value to log-ignore
            ignore = request.REQUEST.get('log-ignore')
            if not ignore:
                saveAccess(request)

    return new_view

#-----------------------------------------------------------------------------------------------------------------------
# basic pages
#-----------------------------------------------------------------------------------------------------------------------
def redirect(request, vals={}):
    return shortcuts.redirect('/home/')

def underConstruction(request):
    return render_to_response('site/pages/microcopy/construction.html')

def upgrade(request):
    return render_to_response('site/pages/microcopy/upgrade.html')

def continueAtOwnRisk(request):
    response = shortcuts.redirect("/web/")
    response.set_cookie('atyourownrisk', 'yes')
    return response

def tryLoveGov(request, to_page="home/", vals={}):
    response = shortcuts.redirect("/" + to_page)
    response.set_cookie('lovegov_try', 1)
    return response

#-----------------------------------------------------------------------------------------------------------------------
# da blog
#-----------------------------------------------------------------------------------------------------------------------
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
                return renderToResponseCSRF('site/pages/blog/blog.html',vals=vals,request=request)
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

        return renderToResponseCSRF('site/pages/blog/blog.html',vals=vals,request=request)

#-----------------------------------------------------------------------------------------------------------------------
# points alias urls to correct pages
#-----------------------------------------------------------------------------------------------------------------------
def aliasDowncast(request, alias=None, vals={}):
    if UserProfile.lg.get_or_none(alias=alias):
        return viewWrapper(profile, requires_login=True)(request, alias)
    matched_group = Group.lg.get_or_none(alias=alias)
    if matched_group:
        the_view = viewWrapper(groupPage, requires_login=True)
        return the_view(request=request, g_alias=matched_group.alias)
    return redirect(request)

#-----------------------------------------------------------------------------------------------------------------------
# points alias urls to correct pages
#-----------------------------------------------------------------------------------------------------------------------
def aliasDowncastEdit(request, alias=None, vals={}):
    if UserProfile.lg.get_or_none(alias=alias):
        return viewWrapper(account, requires_login=True)(request, alias)
    matched_group = Group.lg.get_or_none(alias=alias)
    if matched_group:
        the_view = viewWrapper(groupEdit, requires_login=True)
        return the_view(request=request, g_alias=matched_group.alias)
    return redirect(request)

#-----------------------------------------------------------------------------------------------------------------------
# login, password recovery and authentication
#-----------------------------------------------------------------------------------------------------------------------
def login(request, to_page='web/', message="", vals={}):
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
        response = renderToResponseCSRF(template='site/pages/login/login-main.html', vals=vals, request=request)
    response.delete_cookie('lovegov_try')
    return response

def loginAuthenticate(request,user,to_page=''):
    auth.login(request, user)
    redirect_response = shortcuts.redirect('/' + to_page)
    redirect_response.set_cookie('privacy', value='PUB')
    return redirect_response

def loginPOST(request, to_page='web',message="",vals={}):
    vals['registerform'] = RegisterForm()
    # LOGIN
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
        return renderToResponseCSRF(template='site/pages/login/login-feed.html', vals=vals, request=request)

    # REGISTER
    elif request.POST['button'] == 'register':
        # Make the register form
        registerform = RegisterForm(request.POST)
        if registerform.is_valid():
            registerform.save()
            vals.update({"fullname":registerform.cleaned_data.get('fullname'),
                         "email":registerform.cleaned_data.get('email'),
                         'zip':registerform.cleaned_data.get('zip'),
                         'age':registerform.cleaned_data.get('age')})
            return renderToResponseCSRF(template='site/pages/login/login-main-register-success.html', vals=vals, request=request)
        else:
            vals.update({"registerform":registerform, "state":'register_error'})
            return renderToResponseCSRF(template='site/pages/login/login-feed.html', vals=vals, request=request)

    elif request.POST['button'] == 'post-twitter':
        return twitterRegister(request, vals)

    # RECOVER
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
        else: return renderToResponseCSRF(template="site/pages/login/login-forgot-password.html",vals=vals.update({'message':msg}),request=request)

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
                        return renderToResponseCSRF(template="site/pages/login/login-forgot-password-reset.html",vals=vals,request=request)
                else: return renderToResponseCSRF(template="site/pages/login/login-forgot-password-reset.html",vals=vals,request=request)
        return renderToResponseCSRF(template="site/pages/login/login-forgot-password.html",vals=vals,request=request)

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
        return renderToResponseCSRF('site/pages/login/login-main-register-confirmation.html', vals=vals, request=request)
    else:
        return loginPOST(request,'/home/',message,vals)

def needConfirmation(request, vals={}):

    redirect = ifConfirmedRedirect(request)
    if redirect: return redirect

    vals['confirmation_message'] =         'Your account has not been validated yet. '\
                                           'Check your email for a confirmation link.  '\
                                           'It might be in your spam folder.'
    vals['state'] = 'need-confirmation'

    return renderToResponseCSRF(template='site/pages/login/login-main.html', vals=vals, request=request)

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
        html = ajaxRender('site/pages/qaweb/qaweb.html', vals, request)
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
    @type request: HttpRequestquestions
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

            html = ajaxRender('site/pages/qaweb/qaweb-temp.html', vals, request)
            url = '/profile/web/' + alias + '/'
            return framedResponse(request, html, url, vals)
    if request.method == 'POST':
        if request.POST['action']:
            return answer(request, vals)
        else:
            return shortcuts.redirect('/alpha/')


#-----------------------------------------------------------------------------------------------------------------------
# MAIN HOME PAGES
#-----------------------------------------------------------------------------------------------------------------------
def home(request, vals):
    focus_html =  ajaxRender('site/pages/home/home.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def groups(request, vals):
    viewer = vals['viewer']
    #groups = viewer.getUserGroups()
    groups = UserGroup.objects.all()
    groups = groups[:6]
    vals['groups'] = groups
    focus_html =  ajaxRender('site/pages/groups/groups.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def elections(request, vals):
    focus_html =  ajaxRender('site/pages/elections/elections.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def politicians(request, vals):
    focus_html =  ajaxRender('site/pages/politicians/politicians.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def presidential(request, vals):
    focus_html =  ajaxRender('site/pages/politicians/presidential.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def representatives(request, vals):
    focus_html =  ajaxRender('site/pages/politicians/representatives.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def congress(request, vals):
    focus_html =  ajaxRender('site/pages/politicians/congress.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)


#-----------------------------------------------------------------------------------------------------------------------
# friends focus (home page)
#-----------------------------------------------------------------------------------------------------------------------
def friends(request, vals):
    class FBFriend:
        pass

    viewer = vals['viewer']

    if viewer.facebook_id:
        friends_list = fbGet(request,'me/friends/')['data']
        vals['facebook_authorized'] = False
        if friends_list:
            vals['facebook_authorized'] = True
            fb_friends = []
            for friend in friends_list[:4]:
                fb_friend = FBFriend()
                fb_friend.name = friend['name']
                fb_friend.id = friend['id']
                fb_friend.picture_url = "https://graph.facebook.com/" + str(fb_friend.id) + "/picture?type=large"
                fb_friends.append(fb_friend)

                vals['facebook_friends'] = fb_friends
    focus_html =  ajaxRender('site/pages/friends/friends.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def questions(request, vals={}):

    getMainTopics(vals)
    getQuestionStats(vals)

    html =  ajaxRender('site/pages/qa/questions.html', vals, request)
    url = request.path
    return framedResponse(request, html, url, vals, rebind="questions")

#-----------------------------------------------------------------------------------------------------------------------
# browse all
#-----------------------------------------------------------------------------------------------------------------------
def browseGroups(request, vals={}):

    html =  ajaxRender('site/pages/browse/browse_groups.html', vals, request)
    url = request.path
    return framedResponse(request, html, url, vals, rebind="browse")

#-----------------------------------------------------------------------------------------------------------------------
# group detail
#-----------------------------------------------------------------------------------------------------------------------
def groupPage(request, g_alias, vals={}):
    # Get the group and current viewer
    viewer = vals['viewer']
    group = Group.objects.get(alias=g_alias)
    vals['group'] = group

    # fill dictionary with group stuff
    vals['info'] = valsGroup(viewer, group, {})

    # Render and return HTML
    focus_html =  ajaxRender('site/pages/group/group_focus.html', vals, request)
    url = group.get_url()
    return homeResponse(request, focus_html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# election detail
#-----------------------------------------------------------------------------------------------------------------------
def electionPage(request, e_alias, vals={}):
    focus_html =  ajaxRender('site/pages/home/focus.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# profile page
#-----------------------------------------------------------------------------------------------------------------------
def profile(request, alias=None, vals={}):

    viewer = vals['viewer']
    if not alias:
        return shortcuts.redirect(viewer.get_url())

    getMainTopics(vals)
    user_profile = UserProfile.objects.get(alias=alias)
    vals['profile'] = user_profile

    # Is the current user already (requesting to) following this profile?
    vals['is_user_requested'] = False
    vals['is_user_confirmed'] = False
    vals['is_user_rejected'] = False
    user_follow = UserFollow.lg.get_or_none(user=viewer,to_user=user_profile)
    if user_follow:
        if user_follow.requested:
            vals['is_user_requested'] = True
        if user_follow.confirmed:
            vals['is_user_confirmed'] = True
        if user_follow.rejected:
            vals['is_user_rejected'] = True
    
    vals['profile_groups'] = user_profile.getGroups()[:4]
    vals['profile_politicians'] = UserProfile.objects.all()[:6]

    comparison = user_profile.getComparison(viewer)
    vals['to_compare'] = profile
    vals['comparison'] = comparison.toBreakdown()

    # Num Follow requests and group invites
    if viewer.id == user_profile.id:
        vals['num_follow_requests'] = user_profile.getNumFollowRequests()
        vals['num_group_invites'] = user_profile.getNumGroupInvites()

    html = ajaxRender('site/pages/profile/profile.html', vals, request)
    url = user_profile.get_url()
    return framedResponse(request, html, url, vals, rebind="profile")

def worldview(request, alias, vals={}):

    viewer = vals['viewer']
    getMainTopics(vals)
    user_profile = UserProfile.objects.get(alias=alias)
    vals['profile'] = user_profile

    vals['followsyou'] = True

    comparison = user_profile.getComparison(viewer)
    vals['comparison_object'] = comparison
    vals['comparison'] = comparison.toBreakdown()

    html = ajaxRender('site/pages/profile/profile_questions.html', vals, request)
    url = user_profile.get_url()
    return framedResponse(request, html, url, vals)

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
    html = ajaxRender('site/pages/content/petition/petition_detail.html', vals, request)
    url = petition.get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of motion with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def motionDetail(request, m_id, vals={}):

    motion = Motion.objects.get(id=m_id)
    vals['motion'] = motion

    contentDetail(request=request, content=motion, vals=vals)
    html = ajaxRender('site/pages/content/motion/motion_detail.html', vals, request)
    url = motion.get_url()

    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of news with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def newsDetail(request, n_id, vals={}):
    news = News.objects.get(id=n_id)
    vals['news'] = news
    contentDetail(request=request, content=news, vals=vals)

    html = ajaxRender('site/pages/news_detail.html', vals, request)
    url =  news.get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of question with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def questionDetail(request, q_id=None, vals={}):

    viewer = vals['viewer']
    if not q_id:
        question = random.choice(Question.objects.all())
    else:
        question = Question.objects.get(id=q_id)

    response = viewer.view.responses.filter(question=question)
    if response:
        response = response[0]
    vals['response'] = response
    vals['question'] = question

    if response:
        vals['group_tuples'] = getGroupTuples(viewer, question, response)

    friends = viewer.getIFollow()
    friends_answered = []
    for f in friends:
        if f.view.responses.filter(question=question):
            friends_answered.append(f)
    vals['friends_answered'] = friends_answered

    html = ajaxRender('site/pages/content_detail/question_detail.html', vals, request)
    url = vals['question'].get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail for a poll
#-----------------------------------------------------------------------------------------------------------------------
def pollDetail(request, p_id=-1, vals={}):

    viewer = vals['viewer']
    poll = Poll.objects.get(id=p_id)
    vals['poll'] = poll
    contentDetail(request, poll, vals)

    q_items = getQuestionItems(viewer, 'B', p_id=poll.id, num=None)
    vals['q_items'] = q_items

    poll_progress = getPollProgress(viewer, poll)
    vals['poll_progress'] = poll_progress

    html = ajaxRender('site/pages/content_detail/poll_detail.html', vals, request)
    url = poll.get_url()
    return framedResponse(request, html, url, vals, rebind="poll_detail")

#-----------------------------------------------------------------------------------------------------------------------
# detail for a discussion
#-----------------------------------------------------------------------------------------------------------------------
def discussionDetail(request, p_id=-1, vals={}):
    return HttpResponse("Discussion!")

#-----------------------------------------------------------------------------------------------------------------------
# closeup of histogram
#-----------------------------------------------------------------------------------------------------------------------
def histogramDetail(request, alias, vals={}):

    group = Group.objects.get(alias=alias)

    vals['group'] = group
    getMainTopics(vals)

    loadHistogram(20, group.id, 'full', vals=vals)

    html = ajaxRender('site/pages/histogram/histogram.html', vals, request)
    url = group.getHistogramURL()
    return framedResponse(request, html, url, vals)

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

        html = ajaxRender('site/pages/about.html', vals, request)
        url = '/about/'
        return framedResponse(request, html, url, vals)

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
        html = ajaxRender('site/pages/account.html', vals, request)
        url = '/settings/'
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

        html = ajaxRender('site/pages/account.html', vals, request)
        url = '/settings/'
        return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# group edit
#-----------------------------------------------------------------------------------------------------------------------
def groupEdit(request, g_alias=None, section="", vals={}):
    viewer = vals['viewer']

    if not g_alias:
        return basicMessage(request,'Requested group does not exist',vals)

    group = Group.lg.get_or_none(alias=g_alias)
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

    html = ajaxRender('site/pages/group/group_edit.html', vals, request)
    url = '/' + str(group.alias) + '/edit/'
    return framedResponse(request, html, url, vals)


#-----------------------------------------------------------------------------------------------------------------------
# Legislation-related pages
#-----------------------------------------------------------------------------------------------------------------------
def legislation(request, session=None, type=None, number=None, vals={}):
    vals['session'], vals['type'], vals['number'] = session, type, number
    if session==None:
        vals['sessions'] = [x['congress_session'] for x in Legislation.objects.values('congress_session').distinct()]
        return renderToResponseCSRF(template='site/pages/legislation/legislation.html', vals=vals, request=request)
    legs = Legislation.objects.filter(congress_session=session)
    if type==None:
        type_list = [x['bill_type'] for x in Legislation.objects.filter(congress_session=session).values('bill_type').distinct()]
        vals['types'] = [(x, BILL_TYPES[x]) for x in type_list]
        return renderToResponseCSRF(template='site/pages/legislation/legislation-session.html', vals=vals, request=request)
    if number==None:
        vals['numbers'] = [x['bill_number'] for x in Legislation.objects.filter(congress_session=session, bill_type=type).values('bill_number').distinct()]
        return renderToResponseCSRF(template='site/pages/legislation/legislation-type.html', vals=vals, request=request)
    legs = Legislation.objects.filter(congress_session=session, bill_type=type, bill_number=number)
    if len(legs)==0:
        vals['error'] = "No legislation found with the given parameters."
    else:
        leg = legs[0]
        vals['leg_titles'] = leg.legislationtitle_set.all()
        vals['leg'] = leg
    return renderToResponseCSRF(template='site/pages/legislation/legislation-view.html', vals=vals, request=request)

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


def facebookAction(request, to_page="/home/", vals={}):
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
        ## If the action wasn't successful and the authorization of this action wasn't already attempted
        if not vals['success'] and not request.COOKIES.get('attempted_fb_auth_action') == fb_action:
            ## Attempt FB Authorization for this action ##
            to_page = vals['fb_auth_path']
            response = shortcuts.redirect(to_page)
            response.set_cookie('auth_to_page',vals['auth_to_page'])
            response.set_cookie('attempted_fb_auth_action',fb_action)
            return response

        else: ## Otherwise it was successful or unsuccessfully authorized
            ## Return the post-action to_page and delete any attempt action cookies
            action_to_page = request.GET.get('action_to_page') #Look for an action to_page
            if action_to_page: #If there is one
                to_page = action_to_page #Set the to_page as the action to_page
            response = shortcuts.redirect(to_page)
            response.delete_cookie('attempted_fb_auth_action')
            return response

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
    html = ajaxRender('site/pages/search/search.html', vals, request)
    url = '/search/' + term
    return framedResponse(request, html, url, vals)
