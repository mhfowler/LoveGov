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
from collections import OrderedDict

######## new match pages

def match(request, section=None, vals={}):

    viewer = vals['viewer']

    url = None
    if not section:
        section = viewer.getFirstNotCompletedMatchSection()
        if section:
            if section == 'getInvolved':
                url = "/home/"
            else:
                url = '/match/' + section + '/'
        if not section:
            url = '/match/representatives/'
            section = 'representatives'
        if not request.is_ajax():
            return shortcuts.redirect(url)


    vals['show_welcome'] = show_welcome = not viewer.checkTask("M")
    if show_welcome:
        viewer.completeTask("M")
    vals['show_welcome'] = True

    if section == 'presidential':
        match_body_html = getMatchPresidentialHTML(request, vals)
        viewer.completeMatchSection("P")
    elif section == 'representatives':
        match_body_html = getRepresentativesHTML(request, vals)
        viewer.completeMatchSection("R")
    elif section == 'friends':
        match_body_html = getMatchFriendsHTML(request, vals)
        viewer.completeMatchSection("F")
    elif section == 'groups':
        match_body_html = getMatchGroupsHTML(request, vals)
        viewer.completeMatchSection("G")
    elif section == 'congress':
        vals['match_with_congress'] = 1
        match_body_html = getHistogramDetailHTML(request, 'congress', vals)
        viewer.completeMatchSection("C")
    elif section == 'getInvolved':
        if viewer.getFirstNotCompletedMatchSection()=='getInvolved':
            viewer.completeMatchSection("I")
        match_body_html = getHomeHTML(request, vals)

    lastNotDone = viewer.getFirstNotCompletedMatchSection()

    progress_down = ''
    if lastNotDone=='presidential':
        progress_down = ''
    elif lastNotDone=='representatives':
        progress_down = 'one-down'
    elif lastNotDone=='groups':
        progress_down = 'two-down'
    elif lastNotDone=='friends':
        progress_down = 'three-down'
    elif lastNotDone=='congress':
        progress_down = 'four-down'
    elif lastNotDone=='getInvolved':
        progress_down = 'five-down'
    else:
        progress_down = 'all-down'


    vals['progress_down'] = progress_down
    vals['match_sections_completed'] = viewer.match_sections_completed
    vals['match_body_html'] = match_body_html
    focus_html =  ajaxRender('site/pages/match/match.html', vals, request)
    if not url:
        url = request.path
    return homeResponse(request, focus_html, url, vals)

def getMatchGroupsHTML(request, vals):

    viewer = vals['viewer']

    focus_html =  ajaxRender('site/pages/match/match_groups.html', vals, request)
    return focus_html

def getMatchPresidentialHTML(request, vals):
    viewer = vals['viewer']
    election = Election.objects.get(alias="presidential_election")
    vals['group'] = election
    vals['info'] = valsElection(viewer, election, {})

    valsQuestionsThreshold(vals)
    getMainTopics(vals)

    focus_html =  ajaxRender('site/pages/match/match_presidential.html', vals, request)
    return focus_html

def getMatchFriendsHTML(request, vals):
    viewer = vals['viewer']
    likeMindedVals(request, vals)
    focus_html =  ajaxRender('site/pages/match/match_friends.html', vals, request)
    return focus_html

#########

def basicMessage(request,message,vals={}):
    """
    Convenience method which returns a simple nice looking message in a frame
    """
    vals['basic_message'] = message
    url = '/'
    html = ajaxRender('site/pages/basic_message.html', vals, request)
    return framedResponse(request, html, url, vals)

def errorMessage(request,message,vals={}):
    vals['basic_message'] = message
    url = '/'
    html = ajaxRender('site/pages/basic_message.html', vals, request)
    return framedResponse(request, html, url, vals)


def framedResponse(request, html, url, vals={}, rebind="home"):
    """
    Convenience method which is a switch between rendering a page center and returning via ajax or rendering frame.
    """
    if request.is_ajax():
        to_return = {'html':html, 'url':url, 'rebind':rebind, 'title':vals['page_title']}
        return HttpResponse(json.dumps(to_return))
    else:
        vals['center'] = html
        viewer = vals.get("viewer")
        if viewer:
            vals['notifications_num'] = viewer.getNotifications(new=True).count()
        frame(request, vals)
        return renderToResponseCSRF(template='site/frame/frame.html', vals=vals, request=request)

def homeResponse(request, focus_html, url, vals):
    vals['home_link'] = True
    if request.is_ajax() and request.GET.get('has_sidebar'):
            to_return = {'focus_html':focus_html, 'url':url, 'title':vals['page_title']}
            return HttpResponse(json.dumps(to_return))
    else:
        vals['focus_html'] = focus_html
        homeSidebar(request, vals)
        html = ajaxRender('site/pages/home/home_frame.html', vals, request)
        return framedResponse(request, html, url, vals, rebind="home")

def loginResponse(request, central_html, url, vals):
    if request.is_ajax() and request.GET.get('has_login_frame'):
        to_return = {'html':central_html, 'url':url, 'title':vals['page_title']}
        return HttpResponse(json.dumps(to_return))
    else:
        vals['central_html'] = central_html
        return renderToResponseCSRF(template='site/pages/october_login/october_login.html', vals=vals, request=request)

def viewWrapper(view, requires_login=False):
    """Outer wrapper for all views"""
    def new_view(request, *args, **kwargs):
        vals = {'STATIC_URL':settings.STATIC_URL_NOSLASH}
        user = None
        try: # Catch all error messages

#            return shortcuts.redirect('/underconstruction/')

            # if ie<9 redirect to upgrade page
            if not checkBrowserCompatible(request):
                return shortcuts.redirect("/upgrade/")

            # google analytics
            vals['google'] = GOOGLE_LOVEGOV

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
            vals['back_url'] = request.COOKIES.get('back_url')

            # privacy
            vals['anonymous_mode'] = getPrivacy(request) == "PRI"

            # helper for key stroke sequences
            vals['sequence'] = [0]

            vals['requires_login'] = requires_login

            if requires_login:

                # who is logged in?
                controlling_user = getControllingUser(request)
                vals['controlling_user'] = controlling_user

                # if no ControllingUser (not logged in) return the Anonymous UserProfile, else returns associated user
                if controlling_user:
                    user = controlling_user.user_profile
                    if not user:
                        LGException(enc("Controlling User without user_profile! controlling_user: " + controlling_user.email + " | id: " + str(controlling_user.id)))
                    vals['prohibited_actions'] = controlling_user.prohibited_actions
                else:
                    to_page = vals['to_page']
                    # if not unauthenticated action, redirect to login page
                    if not request.POST.get('action') in UNAUTHENTICATED_ACTIONS:
                        if not request.REQUEST.get('robotscantlove'):
                            return shortcuts.redirect("/login" + request.path)
                        else:
                            user = getAnonUser()
                            vals['i_am_anonymous'] = True
                            vals['prohibited_actions'] = ANONYMOUS_PROHIBITED_ACTIONS
                            vals['controlling_user'] = user.user
                    else: # otherwise action can be done without AUTHENTICATION
                        vals['prohibited_actions'] = ANONYMOUS_PROHIBITED_ACTIONS
                        return view(request,vals=vals,*args,**kwargs)

                # get user profile associated with controlling user
                vals['user'] = user
                vals['viewer'] = user

                # first login
                first_login = user.first_login
                vals['firstLoginStage'] = first_login


# try lovegov without an account
#                # if not authenticated user, and not lovegov_try cookie, redirect to login page
#                if user.isAnon() and not request.COOKIES.get('lovegov_try'):
#                    # If this action can't be performed without being authenticated
#                    if not request.POST.get('action') in UNAUTHENTICATED_ACTIONS:
#                        # Redirect to login page
#                        return shortcuts.redirect("/login" + request.path)
#                    else: # otherwise action can be done without AUTHENTICATION
#                        return view(request,vals=vals,*args,**kwargs)



                # IF NOT DEVELOPER AND IN UPDATE MODE or ON DEV SITE, REDIRECT TO CONSTRUCTION PAGE
                if UPDATE:
                    if not user.developer:
                        normal_logger.debug('blocked: ' + user.get_name())
                        return shortcuts.redirect('/underconstruction/')

                # if user not confirmed redirect to login page
                if not user.confirmed:
                    return needConfirmation(request, vals)

                # background tasks
                user.valsBackgroundTasks(vals)


            # if everything worked, and there wasn't an error, return the view
            return view(request,vals=vals,*args,**kwargs)

        # Any errors caught here
        except LGException as e:
            return errorMessage(request, message=e.getClientMessage(), vals=vals)

        finally:  # save page access, if there isn't specifically set value to log-ignore
            ignore = request.REQUEST.get('log-ignore')
            if not ignore:
                #saveAccess(request)
                PageAccess().autoSave(request, user)

    return new_view

#-----------------------------------------------------------------------------------------------------------------------
# basic pages
#-----------------------------------------------------------------------------------------------------------------------
def redirect(request, page='/home', vals={}):
    return shortcuts.redirect(page)

def linkRedirect(request, n_id, vals={}):
    news = News.objects.get(id=n_id)
    news.link_clicks += 1
    news.save()
    return shortcuts.redirect(news.link)

def underConstruction(request):
    return render_to_response('site/pages/microcopy/construction.html')

def upgrade(request):
    return render_to_response('site/pages/microcopy/upgrade.html', {'STATIC_URL': settings.STATIC_URL})

def continueAtOwnRisk(request):
    response = shortcuts.redirect("/web/")
    response.set_cookie('atyourownrisk', 'yes')
    return response

def tryLoveGov(request, to_page="home/", vals={}):
    response = shortcuts.redirect("/" + to_page)
    response.set_cookie('lovegov_try', 1)
    return response

def unsubscribe(request, email, vals={}):
    already = UnsubscribedToEmail.lg.get_or_none(email=email)
    if not already:
        UnsubscribedToEmail(email=email).save()
    return HttpResponse("You have unsubscribed from LoveGov emails.")

def goToLoveGov(request, link_id, vals={}):
    to_lovegov = toLoveGov.lg.get_or_none(id=link_id)
    if to_lovegov:
        to_lovegov.clicks += 1
        to_lovegov.save()
    else:
        error_logger.error("to lovegov with code that does not exist: " + str(link_id))
    return shortcuts.redirect("/home/")

def lgAlias(request, alias, vals={}):
    lg_alias = LoveGovAlias(alias=alias, ipaddress=request.META.get('REMOTE_ADDR'))
    lg_alias.save()
    return shortcuts.redirect("/")

def updateHotFeedPage(request, vals={}):
    viewer = vals['viewer']
    return HttpResponse(viewer.updateHotFeed())

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

        elif category:
            if string.capitalize(category) in BlogEntry.CATEGORY_CHOICES:
                for blogPost in blogPosts:
                    if string.capitalize(category) in blogPost.category:
                        vals['blogPosts'].append(blogPost)
            else:
                creator = UserProfile.lg.get_or_none(alias=category)
                vals['ownBlog'] = creator == user
                vals['blogPosts'] = blogPosts.filter(creator=creator)
        else:
            vals['blogPosts'] = blogPosts

        central_html = ajaxRender(template='site/pages/october_login/blog.html', vals=vals, request=request)
        url = request.path
        return loginResponse(request, central_html, url, vals)


def aliasDowncast(request, alias=None, vals={}):
    """
    points alias urls to correct pages
    """
    if UserProfile.lg.get_or_none(alias=alias):
        return viewWrapper(profile, requires_login=True)(request, alias)
    matched_group = Group.lg.get_or_none(alias=alias)
    if matched_group:
        the_view = viewWrapper(groupPage, requires_login=True)
        return the_view(request=request, g_alias=matched_group.alias)
    return error404(request)

#-----------------------------------------------------------------------------------------------------------------------
# points alias urls to correct pages, and then on to edit page
#-----------------------------------------------------------------------------------------------------------------------
def aliasDowncastEdit(request, alias=None, vals={}):
    """
    points alias urls to correct pages
    """
    if UserProfile.lg.get_or_none(alias=alias):
        return viewWrapper(account, requires_login=True)(request, alias)
    matched_group = Group.lg.get_or_none(alias=alias)
    if matched_group:
        the_view = viewWrapper(groupEdit, requires_login=True)
        return the_view(request=request, g_alias=matched_group.alias)
    return error404(request)

def error404(request, vals={}):
    return render_to_response('404.html')


#-----------------------------------------------------------------------------------------------------------------------
# login, password recovery and authentication
#-----------------------------------------------------------------------------------------------------------------------
def hello(request, vals={}):
    vals['name'] = request.GET.get('name')
    vals['email'] = request.GET.get('email')
    central_html = ajaxRender(template='site/pages/october_login/hello.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def privacyPolicy(request, vals={}):
    central_html = ajaxRender(template='site/pages/october_login/privacy_policy.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def termsOfUse(request, vals={}):
    central_html = ajaxRender(template='site/pages/october_login/terms_of_use.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def login(request, to_page='home/', message="", vals={}):
    """
    login, password recovery and authentication
    """
    to_page = "/" + to_page

    # Check if already logged in
    if request.user.is_authenticated():
        user_profile = getUserProfile(request)
        go_to_page = loginRedirectToPage(request, user_profile, to_page)
        return shortcuts.redirect(go_to_page)

    # Try logging in with facebook
    user_prof = fbLogin(request,vals,refresh=False)
    if user_prof:
        go_to_page = loginRedirectToPage(request, user_prof, to_page)
        return shortcuts.redirect(go_to_page)

    # Try logging in with twitter
    twitter = twitterLogin(request,to_page, vals)
    if twitter:
        return twitter

   # Otherwise load the login page
    central_html = ajaxRender(template='site/pages/october_login/front_page.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)


def loginMission(request, vals):
    valsMission(vals)
    central_html = ajaxRender(template='site/pages/october_login/mission.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def loginHowItWorks(request, vals):
    central_html = ajaxRender(template='site/pages/how-it-works.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def loginSignUp(request, claimed_by="", vals={}):
    vals['email'] = vals['email2'] = claimed_by
    central_html = ajaxRender(template='site/pages/october_login/sign_up.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def loginFAQ(request, vals={}):
    central_html = ajaxRender(template='site/pages/faq.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

def presidentialMatching(request, vals):
#    if not LOCAL:
    obama = UserProfile.lg.get_or_none(alias='barack_obama') or getUser("Randy Johnson")
    mitt = UserProfile.lg.get_or_none(alias='mitt_romney') or getUser("Katy Perry")
    vals['obama'] = obama
    vals['mitt'] = mitt
    vals['candidates'] = [obama, mitt]
    vals['agreement_ids'] = [int(obama.id), int(mitt.id)]

    ip = request.META.get('REMOTE_ADDR', None)
    jregion = None
    if ip and ip!='127.0.0.1':
        import requests
        r = requests.get('http://smart-ip.net/geoip-json/'+ip)
        jcity = str(r.json['city'])
        jregion = str(r.json['region'])
        if jcity and jregion:
            city = '<strong>' + jcity + ', ' + jregion + '</strong>'
        else:
            city = 'your city'
    else:
        city = 'your city' # default city

    vals['local_location'] = city
    if jregion:
        from modernpolitics.constants import STATES
        stateDict = dict([reversed(x) for x in STATES])
        stateAbbr = stateDict.get(jregion)
        if stateAbbr:
            senators = getSensFromState(stateAbbr)
            if senators:
              vals['local_candidate1'], vals['local_candidate2'] = senators

    vals['lgpoll'] = getLoveGovPoll()

    cookie_data, new_cookie = getCookieData(request)

    central_html = ajaxRender(template='site/pages/october_login/presidential_matching.html', vals=vals, request=request)
    url = request.path
    response = loginResponse(request, central_html, url, vals)

    if new_cookie:
        response.set_cookie("cookie_data_id", cookie_data.id)
    return response



def passwordRecovery(request,confirm_link=None, vals={}):

    # password recovery request
    if not confirm_link:
        central_html = ajaxRender(template='site/pages/october_login/password_recovery_request.html', vals=vals, request=request)
        return loginResponse(request, central_html, request.path, vals)

    # password recovery reset
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
        central_html = ajaxRender(template='site/pages/october_login/password_recovery_reset.html', vals=vals, request=request)
        return loginResponse(request, central_html, request.path, vals)

def logout(request, vals={}):
    auth.logout(request)
    response = shortcuts.redirect('/login/')
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
        central_html = ajaxRender(template='site/pages/october_login/confirm.html', vals=vals, request=request)
        url = request.path
        return loginResponse(request, central_html, url, vals)
    else:
        return loginPOST(request,'/home/',message,vals)

def needConfirmation(request, vals={}):

    redirect = ifConfirmedRedirect(request)
    if redirect: return redirect

    central_html = ajaxRender(template='site/pages/october_login/need_confirmation.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)



def register(request, vals={}):
    return loginSignUp(request, vals)


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
    return shortcuts.redirect("/home/")
#    if request.method == 'GET':
#        getUserWebResponsesJSON(request,vals)
#        vals['firstLogin'] = vals['viewer'].checkFirstLogin()
#        html = ajaxRender('site/pages/qaweb/qaweb.html', vals, request)
#        url = '/web/'
#        return framedResponse(request, html, url, vals)
#    if request.method == 'POST':
#        if request.POST['action']:
#            return answer(request, vals)
#        else:
#            return shortcuts.redirect('/alpha/')


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
# MAIN PAGES
#-----------------------------------------------------------------------------------------------------------------------
def welcome(request, vals):

    viewer = vals['viewer']
    if viewer.location and viewer.location.state and not viewer.checkTask("S"):
        sg = getStateGroupFromState(viewer.location.state)
        if sg:
            return shortcuts.redirect(sg.get_url())

    focus_html =  ajaxRender('site/pages/home/welcome.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)


def home(request, vals={}):
    focus_html = getHomeHTML(request, vals)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def getHomeHTML(request, vals):
    viewer = vals['viewer']
    viewer.completeTask("L")

    # feed tutorial
    vals['feedtut_tutorial'] = not viewer.checkTask("I")

    vals['feedtut'] = True

    # vals for page parts
    valsFirstLogin(vals)
    valsLikeMinded(vals)
    valsDismissibleHeader(request, vals)

    focus_html =  ajaxRender('site/pages/home/home.html', vals, request)
    return focus_html


def myGroups(request, vals):
    viewer = vals['viewer']
    vals['group_subscriptions'] = viewer.getGroupSubscriptions()
    focus_html =  ajaxRender('site/pages/groups/my_groups.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def myElections(request, vals):
    viewer = vals['viewer']
    vals['group_subscriptions'] = viewer.getGroupSubscriptions()
    focus_html =  ajaxRender('site/pages/elections/my_elections.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def representatives(request, vals):
    focus_html = getRepresentativesHTML(request, vals)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def getRepresentativesHTML(request, vals):
    viewer = vals['viewer']
    viewer.completeTask("F")

    valsRepsHeader(vals)
    vals['no_create_button'] = True

    valsQuestionsThreshold(vals)
    valsFirstLogin(vals)

    focus_html =  ajaxRender('site/pages/match/match_representatives.html', vals, request)
    return focus_html

def friends(request, vals):
    focus_html = getFriendsHTML(request, vals)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def getFriendsHTML(request, vals):
    viewer = vals['viewer']
    friends = viewer.getIFollow().filter(num_answers__gte=10)
    vals['i_follow'] = viewer.i_follow
    top_friends = []
    for f in friends:
        f.comparison = f.getComparison(viewer)
        if f.comparison.num_q > 10:
            top_friends.append(f)
    top_friends.sort(key=lambda x:x.comparison.result,reverse=True)
    vals['friends'] = top_friends[:9]

    # visual stuff for feed
    vals['no_create_button'] = True

    focus_html =  ajaxRender('site/pages/friends/friends.html', vals, request)
    return focus_html

def likeMinded(request, vals):
    focus_html = getLikeMindedHTML(request, vals)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def getLikeMindedHTML(request, vals):

    likeMindedVals(request, vals)

    focus_html =  ajaxRender('site/pages/like_minded/like_minded.html', vals, request)
    return focus_html

def likeMindedVals(request, vals):
    viewer = vals['viewer']
    like_minded = viewer.getLikeMindedGroup()
    vals['like_minded'] = like_minded
    vals['num_members'] = like_minded.members.count()
    vals['num_processed'] = like_minded.processed.count()

    if LOCAL:
        vals['members'] = UserProfile.objects.all()[:10]
    else:
        vals['members'] = like_minded.members.all().order_by("-created_when")

    valsQuestionsThreshold(vals)

#-----------------------------------------------------------------------------------------------------------------------
# qa
#-----------------------------------------------------------------------------------------------------------------------
def questions(request, vals={}):

    getMainTopics(vals)

    valsLGPoll(vals)
    getQuestionStats(vals)

    html =  ajaxRender('site/pages/qa/qa.html', vals, request)
    url = request.path
    return homeResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# browse all
#-----------------------------------------------------------------------------------------------------------------------
def browseGroups(request, vals={}):

    viewer = vals['viewer']
    viewer.completeTask("J")

    valsFirstLogin(vals)
    valsParties(vals)

    # Render and return HTML
    getStateTuples(vals)
    focus_html =  ajaxRender('site/pages/groups/all_groups.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)


def browseElections(request, vals):
    # Render and return HTML
    getStateTuples(vals)
    focus_html =  ajaxRender('site/pages/browse/browse_elections.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# group detail
#-----------------------------------------------------------------------------------------------------------------------
def groupPage(request, g_alias, vals={}):
    # Get the group and current viewer
    viewer = vals['viewer']
    group = Group.objects.get(alias=g_alias)
    group.setNewContentSeen(viewer)
    vals['group'] = group
    if group.group_type=="E":
        return electionPage(request, group.downcast(), vals)

    if group.group_type=="S" and viewer.location and viewer.location.state == group.location.state:
        viewer.completeTask("S")
        vals['first_state_group'] = True
    vals['first_state_group'] = True

    # fill dictionary with group stuff
    vals['info'] = valsGroup(viewer, group, {})

    # visual stuff for feed
    if g_alias == 'congress':
        vals['no_create_button'] = True
        vals['no_feed_filter'] = True

    # Render and return HTML
    focus_html =  ajaxRender('site/pages/group/group_focus.html', vals, request)
    url = group.get_url()
    return homeResponse(request, focus_html, url, vals)


def electionPage(request, election, vals={}):
    focus_html = getElectionHTML(request, election ,vals)
    url = request.path
    return homeResponse(request, focus_html, url, vals)

def getElectionHTML(request, election, vals):
    viewer = vals['viewer']
    if election.alias == 'presidential_election':
        viewer.completeTask("P")
        vals['presidential_election'] = True

    vals['info'] = valsElection(viewer, election, {})

    valsQuestionsThreshold(vals)
    valsFirstLogin(vals)

    focus_html =  ajaxRender('site/pages/elections/election_focus.html', vals, request)
    return focus_html

def getPresidentialHTML(request, vals):
    election= Election.objects.get(alias="presidential_election")
    return getElectionHTML(request, election, vals)

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
    valsAmIFollowing(viewer, user_profile, vals)

    vals['profile_groups'] = user_profile.getRealGroups()[:4]
    vals['profile_politicians'] = user_profile.getPoliticians()

    comparison, web_json = user_profile.getComparisonJSON(viewer)
    vals['web_comparison'] = comparison
    vals['web_json'] = web_json

    # check if user is my rep
    if user_profile.politician:
        reps = viewer.getRepresentatives(viewer.location)
        if reps:
            vals['my_rep'] = user_profile in reps
        vals['you_asked_to_join'] =  you_asked_to_join = AskedAction.objects.filter(user=viewer, politician=user_profile)
        if you_asked_to_join:
            vals['num_asked'] = user_profile.num_asked - 1
        else:
            vals['num_asked'] = user_profile.num_asked

    vals['my_rep'] = True
    # Num Follow requests and group invites
    if viewer.id == user_profile.id:
        vals['num_follow_requests'] = user_profile.getNumFollowRequests()
        vals['num_group_invites'] = user_profile.getNumGroupInvites()

    if user_profile.politician:
        vals['is_user_supporting'] = Supported.lg.get_or_none(confirmed=True, user=viewer, to_user=user_profile)

    html = ajaxRender('site/pages/profile/profile.html', vals, request)
    url = user_profile.get_url()
    return framedResponse(request, html, url, vals, rebind="profile")



def worldview(request, alias, vals={}):

    viewer = vals['viewer']
    getMainTopics(vals)
    user_profile = UserProfile.objects.get(alias=alias)
    vals['profile'] = user_profile

    valsAmIFollowing(viewer, user_profile, vals)

    vals['followsyou'] = True

    comparison = user_profile.getComparison(viewer)
    vals['comparison_object'] = comparison
    vals['comparison'] = comparison.toBreakdown()

    html = ajaxRender('site/pages/profile/profile_questions.html', vals, request)
    url = user_profile.get_url()
    return framedResponse(request, html, url, vals)


def thread(request, c_id, vals={}):
    content = Content.lg.get_or_none(id=c_id)
    if not content:
        return HttpResponse("The indicated content item does not exist.")
    vals['content'] = content
    html = ajaxRender('site/pieces/thread.html', vals, request)
    url = request.path
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of petition with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def petitionDetail(request, p_id, c_id=None, vals={}, signerLimit=8):

    petition = Petition.lg.get_or_none(id=p_id)
    if not petition:
        return HttpResponse("This petition does not exist")

    viewer = vals['viewer']
    vals['c_id'] = c_id
    valsPetition(viewer, petition, vals)

    contentDetail(request=request, content=petition, vals=vals)
    html = ajaxRender('site/pages/content_detail/petition_detail.html', vals, request)
    url = petition.get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of motion with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def motionDetail(request, m_id, c_id=None, vals={}):

    motion = Motion.objects.get(id=m_id)
    vals['motion'] = motion
    vals['c_id'] = c_id

    contentDetail(request=request, content=motion, vals=vals)
    html = ajaxRender('site/pages/content/motion/motion_detail.html', vals, request)
    url = motion.get_url()

    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of news with attached forum
#-----------------------------------------------------------------------------------------------------------------------

def commentDetail(request, type, content_id, comment_id, vals={}):
    vals['onComment'] = comment_id
    comment = Comment.lg.get_or_none(id=comment_id, root_content__id=content_id)
    if not comment:
        c = Content.lg.get_or_none(id=content_id)
        if c:
            return HttpResponseRedirect(c.get_url())
        else:
            return HttpResponseBadRequest("Requested content does not exist")
    if type == 'news':
        return newsDetail(request, content_id, vals=vals)
    elif type == 'question':
        return questionDetail(request, content_id, vals=vals)
    elif type == 'poll':
        return pollDetail(request, content_id, vals=vals)
    elif type == 'discussion':
        return discussionDetail(request, content_id, vals=vals)
    elif type == 'motion':
        return motionDetail(request, content_id, vals=vals)
    elif type == 'petition':
        return petitionDetail(request, content_id, vals=vals)
    else:
        return error404(request, vals=vals)

def newsDetail(request, n_id, vals={}):
    news = News.objects.get(id=n_id)
    vals['news'] = news
    liked = news.getSupporters()
    vals['liked'] = liked
    contentDetail(request=request, content=news, vals=vals)
    html = ajaxRender('site/pages/content_detail/news_detail.html', vals, request)
    url =  news.get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail of question with attached forum
#-----------------------------------------------------------------------------------------------------------------------
def questionDetail(request, q_id=None, c_id=None, vals={}):

    viewer = vals['viewer']
    if not q_id:
        question = random.choice(Question.objects.all())
    else:
        question = Question.objects.get(id=q_id)

    response = viewer.getResponseToQuestion(question)
    question.my_response = response
    vals['response'] = response
    vals['question'] = question

    contentDetail(request, question, vals)
    html = ajaxRender('site/pages/content_detail/question_detail.html', vals, request)
    url = vals['question'].get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# detail for a poll
#-----------------------------------------------------------------------------------------------------------------------
def pollDetail(request, p_id=-1, c_id=None, vals={}):

    viewer = vals['viewer']
    poll = Poll.objects.get(id=p_id)
    vals['poll'] = poll
    contentDetail(request, poll, vals)

    poll_progress = poll.getPollProgress(viewer)
    vals['poll_progress'] = poll_progress
    getMainTopics(vals)

    if poll.isLoveGovPoll():
        viewer.completeTask("L")

    html = ajaxRender('site/pages/content_detail/poll_detail.html', vals, request)
    url = poll.get_url()
    return framedResponse(request, html, url, vals, rebind="poll_detail")

#-----------------------------------------------------------------------------------------------------------------------
# detail for a discussion
#-----------------------------------------------------------------------------------------------------------------------
def discussionDetail(request, d_id=-1, c_id=None, vals={}):

    viewer = vals['viewer']
    discussion = Discussion.objects.get(id=d_id)
    vals['discussion'] = discussion
    vals['liked'] = discussion.getSupporters()
    contentDetail(request, discussion, vals)
    html = ajaxRender('site/pages/content_detail/discussion_detail.html', vals, request)
    url = discussion.get_url()
    return framedResponse(request, html, url, vals, rebind="discussion_detail")

#-----------------------------------------------------------------------------------------------------------------------
# closeup of histogram
#-----------------------------------------------------------------------------------------------------------------------
def histogramDetail(request, alias, vals={}):
    html = getHistogramDetailHTML(request, alias, vals)
    url = request.path
    return framedResponse(request, html, url, vals)

def getHistogramDetailHTML(request, alias, vals):

    viewer = vals['viewer']
    if alias == 'congress':
        viewer.completeTask("C")

    if LOCAL:
        group = getLoveGovGroup()
    else:
        group = Group.objects.get(alias=alias)

    vals['group'] = group
    getMainTopics(vals)

    loadHistogram(20, group.id, 'full', vals=vals)

    html = ajaxRender('site/pages/histogram/histogram.html', vals, request)
    return html

#-----------------------------------------------------------------------------------------------------------------------
# About Link
#-----------------------------------------------------------------------------------------------------------------------
def about(request, start="video", vals={}):
    if request.method == 'GET':
        vals['start_page'] = start
        valsMission(vals)
        html = ajaxRender('site/pages/about.html', vals, request)
        url = '/about/'
        return framedResponse(request, html, url, vals)

def valsMission(vals):
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

#-----------------------------------------------------------------------------------------------------------------------
# modify account, change password
#-----------------------------------------------------------------------------------------------------------------------
def account(request, section="", vals={}):

    user = vals['viewer']
    vals['uploadform'] = UploadFileForm()

    valsParties(vals)
    getStateTuples(vals)

    if section == "profile": vals['profile_message'] = " "

    if request.method == 'GET':
        html = ajaxRender('site/pages/settings/settings.html', vals, request)
        url = '/settings/'
        return framedResponse(request, html, url, vals, rebind="settings")

    elif request.method == 'POST':
        if request.POST['box'] == 'password':
            password_form = PasswordForm(request.POST)
            if password_form.process(request):
                message = "You successfully changed your password."
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

        html = ajaxRender('site/pages/settings/settings.html', vals, request)
        url = '/settings/'
        return framedResponse(request, html, url, vals, rebind="settings")

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
def legislation (request, vals={}):

    vals['legislation_items'] = Legislation.objects.all()
    vals['sessions'] = LEGISLATION_SESSIONS

    type_list = []
    for k,v in BILL_TYPES.items():
        type_list.append({'abbreviation':k,'verbose':v})

    vals['types'] = type_list
    #vals['subjects'] = LEGISLATION_SUBJECTS
    vals['committees'] = LEGISLATION_COMMITTEES
    vals['bill_numbers'] = LEGISLATION_BILLNUMBERS

    now = datetime.datetime.now()
    time_range = [1464,732,366,183]
    introduced_dates = []
    for x in time_range:
        date = now - datetime.timedelta(days=x)
        json_date = json.dumps({'year':date.year, 'month':date.month, 'day':date.day})
        date_tuple = {'json':json_date, 'date':date}
        introduced_dates.append(date_tuple)
    vals['introduced_dates'] = introduced_dates

    vals['sponsors'] = LEGISLATION_SPONSORS
    vals['sponsor_parties'] = LEGISLATION_PARTIES

    focus_html =  ajaxRender('site/pages/legislation/legislation.html', vals, request)
    url = request.path
    return homeResponse(request, focus_html, url, vals)


def legislationDetail(request, l_id, vals={}):
    legislation = Legislation.objects.get(id=l_id)
    vals['l'] = legislation
    vals['actions'] = legislation.legislation_actions.all().order_by("-datetime")
    vals['action_states'] = [x.state for x in vals['actions']]
    action_states = [x.state for x in vals['actions']]
    vals['back_url'] = '/legislation/'
    vals['content_string'] = 'legislation'

    if legislation.congress_body == "H":
        if "ENACTED:SIGNED" in action_states:
            bill_progress = "Passed House and Senate, Signed into Law"
        if "PASSED:BILL" in action_states:
            bill_progress = "Passed House and Senate"
        if "PASSED_OVER:HOUSE" in action_states:
            if legislation.bill_type == 'hc':
                if legislation.bill_relation.count() != 0:
                    bill_progress = "Concurrent Resolution Passed House and Senate"
                elif legislation.bill_relation.count() == 0:
                    bill_progress = "Concurrent Resolution Passed House"
            else:
                if legislation.bill_relation.count() != 0:
                    bill_progress = "Passed House and Senate"
                elif legislation.bill_relation.count() == 0:
                    bill_progress = "Passed House"
        elif "PASSED:JOINTRES" in action_states:
            if legislation.bill_relation.count() != 0:
                bill_progress = "Joint Resolution Passed House and Senate"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Joint Resolution Passed House"
        elif "PASSED:CONCURRENTRES" in action_states:
            if legislation.bill_relation.count() != 0:
                bill_progress = "Concurrent Resolution Passed House and Senate"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Concurrent Resolution Passed House"
        elif "PASSED:SIMPLERES" in action_states:
            bill_progress = "Resolution Passed House"
        elif legislation.bill_type == 'h':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Passed Senate, Not Passed House"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Not Passed House"
        elif legislation.bill_type == 'hr':
            bill_progress = "Resolution Not Passed House"
        elif legislation.bill_type == 'hj':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Joint Resolution Passed Senate, Not Passed House"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Joint Resolution Not Passed House"
        elif legislation.bill_type == 'hc':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Concurrent Resolution Passed Senate, Not Passed House"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Concurrent Resolution Not Passed House"
        else:
            bill_progress = "Not Passed House"
    elif legislation.congress_body == "S":
        if "ENACTED:SIGNED" in action_states:
            bill_progress = "Passed Senate and House, Signed into Law"
        if "PASSED:BILL" in action_states:
            bill_progress = "Passed Senate and House"
        if "PASSED_OVER:SENATE" in action_states:
            if legislation.bill_type == 'sc':
                if legislation.bill_relation.count() != 0:
                    bill_progress = "Concurrent Resolution Passed House, Not Passed Senate"
                elif legislation.bill_relation.count() == 0:
                    bill_progress = "Concurrent Resolution Not Passed Senate"
            else:
                if legislation.bill_relation.count() != 0:
                    bill_progress = "Passed Senate and House"
                elif legislation.bill_relation.count() == 0:
                    bill_progress = "Passed Senate"
        elif "PASSED:JOINTRES" in action_states:
            if legislation.bill_relation.count() != 0:
                bill_progress = "Joint Resolution Passed Senate and House"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Joint Resolution Passed Senate"
        elif "PASSED:CONCURRENTRES" in action_states:
            if legislation.bill_relation.count() != 0:
                bill_progress = "Joint Resolution Passed Senate and House"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Joint Resolution Passed Senate"
        elif "PASSED:SIMPLERES" in action_states:
            bill_progress = "Resolution Passed Senate"
        elif legislation.bill_type == 's':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Passed House, Not Passed Senate"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Not Passed Senate"
        elif legislation.bill_type == 'sr':
            bill_progress = "Resolution Not Passed Senate"
        elif legislation.bill_type == 'sj':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Joint Resolution Passed House, Not Passed Senate"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Joint Resolution Not Passed Senate"
        elif legislation.bill_type == 'sc':
            if legislation.bill_relation.count() != 0:
                bill_progress = "Concurrent Resolution Passed House, Not Passed Senate"
            elif legislation.bill_relation.count() == 0:
                bill_progress = "Concurrent Resolution Not Passed Senate"
        else:
            bill_progress = "Not Passed Senate"
    vals['bill_progress'] = bill_progress

    vals['cosponsors'] = legislation.legislation_cosponsors.all()
    vals['related'] = legislation.bill_relation.all()

    contentDetail(request, legislation, vals)
    html = ajaxRender('site/pages/content_detail/legislation_detail.html', vals, request)
    url = legislation.get_url()
    return framedResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# facebook accept
#-----------------------------------------------------------------------------------------------------------------------
def facebookHandle(request, to_page="/login/home/", vals={}):
    cookie_state = request.COOKIES.get('fb_state')
    returned_state = request.GET.get('state')
    if cookie_state and returned_state == cookie_state: #If this is the correct authorization state
        code = request.GET.get('code') #Get the associated code

        redirect_uri = getRedirectURI(request, request.path) #Set the redirect URI

        access_token = fbGetAccessToken(request, code, redirect_uri) #Retrieve access token
        if not access_token: #If there's no access token, it's being logged so return the login page
            return shortcuts.redirect('/login/')

        auth_to_page = request.COOKIES.get('auth_to_page') #Get the authorization to_page from Cookies
        if auth_to_page: #If it exists
            to_page = auth_to_page
            if not to_page.startswith("/login/") and not to_page in ['/fb/connect/']:
                to_page = "/login" + to_page

        response = shortcuts.redirect(to_page) #Build a response
        response.set_cookie('fb_token', access_token) #Set the facebook authorization cookie

        if auth_to_page: #If there is an authorization to_page cookie
            response.delete_cookie('auth_to_page') #delete that cookie

        return response

    return shortcuts.redirect(to_page) #If this is the wrong state, go to default to_page

def facebookRedirect(request, to_page="/login/home/", redirect_uri=None, vals={}):
    fb_link, fb_state = fbGetRedirect(request, redirect_uri=redirect_uri, vals=vals)
    response = shortcuts.redirect(fb_link)
    response.set_cookie("fb_state", fb_state)
    response.set_cookie("auth_to_page", to_page)
    return response

# the return side of the above redirect
def facebookConnect(request, vals):
    return connectWithFacebook(request, vals=vals)


def facebookAuthorize(request, vals={}, scope=""):

    auth_to_page = request.GET.get('auth_to_page') #Check for an authorization to_page
    fb_scope = request.GET.get('fb_scope') #Check for a scope

    if fb_scope: #Set the scope if there is one
        scope = fb_scope

    if not scope == "":
        fb_link, fb_state = fbGetRedirect(request , vals , scope=scope) #Get the FB State and FB Link for the auth CODE
    else:
        fb_link, fb_state = fbGetRedirect(request , vals) #Get the FB State and FB Link for the auth CODE
    response = shortcuts.redirect(fb_link) #Build a response to get authorization CODE
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
# tries to create a user account from form post and twitter access token,
# - if invalid returns forms with errors
# - if not twitter access token redirects
#-----------------------------------------------------------------------------------------------------------------------
def twitterRegister(request, vals={}):
    already = twitterLogin(request, to_page='/home/', vals=vals)
    if already:
        return already

    central_html = ajaxRender(template='site/pages/october_login/post_twitter.html', vals=vals, request=request)
    url = request.path
    return loginResponse(request, central_html, url, vals)

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
    html = ajaxRender('site/pages/search.html', vals, request)
    url = '/search/' + term
    return homeResponse(request, html, url, vals)

#-----------------------------------------------------------------------------------------------------------------------
# Scorecards
#-----------------------------------------------------------------------------------------------------------------------
def scorecardDetail(request, s_id, vals={}):

    viewer = vals['viewer']
    scorecard = Scorecard.objects.get(id=s_id)
    vals['scorecard'] = scorecard

    reps = viewer.getRepresentatives()
    politicians = scorecard.politicians.all().order_by("-num_supporters")
    for r in reps:
        r.comparison = scorecard.getComparison(r)
        r.scorecard_comparison_url = scorecard.getScorecardComparisonURL(r)
    for p in politicians:
        p.comparison = scorecard.getComparison(p)
        p.scorecard_comparison_url = scorecard.getScorecardComparisonURL(p)

    vals['representatives'] = reps
    vals['politicians'] = politicians

    vals['i_can_edit'] = scorecard.getPermissionToEdit(viewer)

    contentDetail(request=request, content=scorecard, vals=vals)
    html = ajaxRender('site/pages/content_detail/scorecards/scorecard_detail.html', vals, request)
    url = scorecard.get_url()
    return framedResponse(request, html, url, vals)

def scorecardEdit(request, s_id, vals={}):

    viewer = vals['viewer']
    scorecard = Scorecard.objects.get(id=s_id)
    vals['scorecard'] = scorecard
    permission = scorecard.getPermissionToEdit(viewer)
    if permission:
        getMainTopics(vals)
        vals['editing_scorecard'] = True
        vals['i_can_edit'] = permission
        contentDetail(request=request, content=scorecard, vals=vals)
        html = ajaxRender('site/pages/content_detail/scorecards/scorecard_edit.html', vals, request)
        url = scorecard.get_url()
        return framedResponse(request, html, url, vals)
    else:
        LGException(str(viewer.id) + " is trying to edit scorecard without permission." + str(scorecard.id))
        return HttpResponse("you dont have permissinon to edit this scorecard")


def scorecardCompare(request, s_id, p_alias, vals={}):
    viewer = vals['viewer']
    scorecard = Scorecard.objects.get(id=s_id)
    vals['scorecard'] = scorecard

    to_compare = UserProfile.objects.get(alias=p_alias)
    vals['to_compare'] = to_compare
    to_compare.comparison = scorecard.getComparison(to_compare)
    getMainTopics(vals)

    html = ajaxRender('site/pages/content_detail/scorecards/scorecard_compare.html', vals, request)
    url = scorecard.get_url()
    return framedResponse(request, html, url, vals)

def scorecardMe(request, s_id, vals={}):
    viewer = vals['viewer']
    return scorecardCompare(request, s_id, viewer.alias, vals)

def state(request, state, vals={}):
    stategroup = StateGroup.lg.get_or_none(location__state=state)
    if stategroup:
        return HttpResponseRedirect(stategroup.get_url())
    return HttpResponse("Requested state group does not exist.")

# for use by popups - popup will close and redirect to given redirect page
def popupRedirect(request, vals={}):
    redirect = request.REQUEST.get('redirect') or '/home/'
    return HttpResponse("<script>window.opener.location.href = \""+redirect+"\"; window.close();</script>");
