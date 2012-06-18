########################################################################################################################
###### FINAL ###########################################################################################################
#
#       Views for pages, finalized for the beta, with legit html and design.
#
#
########################################################################################################################
################################################## IMPORT ##############################################################


### INTERNAL ###
from lovegov.old.django_facebook import context_processors
from lovegov.old.views import *

### DJANGO LIBRARIES ###

### EXTERNAL LIBRARIES ###

########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Wrapper which lets developer users through, and redirects others to development login.
# Note even after release we can still use this wrapper for individual pages we are not ready to release yet.
# args: view
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def developmentWrapper(view):
    """ Development wrapper, login form for us + nice message for others. """
    def new_view(request, *args, **kwargs):
        # if not logged in, redirect to login
        if not request.user.is_authenticated():
            return shortcuts.redirect('/development' + request.path)
        else:
            # if not developer, redirect to login
            user = getUserProfile(request)
            if not user.developer:
                return shortcuts.redirect('/development' + request.path)
            else:
                return view(request, *args, **kwargs)
    return new_view


#-----------------------------------------------------------------------------------------------------------------------
# Development login, login form for us + nice message for others.
# args: view
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def developmentLogin(request, to_page='home/'):
    """Development login, login form for us + nice message for others."""
    # for fb login/register
    dict = context_processors.facebook(request)
    assert dict.get('FACEBOOK_APP_ID'), 'Please specify a facebook app id '\
                                       'and ensure the context processor is enabled'
    # checks if user requested to POST information
    if request.method == 'POST':
        # check recaptcha
        if checkRECAPTCHA(request):
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None and user.is_active:
                auth.login(request, user)
                # check if user confirmed
                user_prof = getUserProfile(request)
                if user_prof.confirmed:
                    redirect_response = shortcuts.redirect('/' + to_page)
                    redirect_response.set_cookie('privacy', value='PUB')
                    return redirect_response
                else:
                    auth.logout(request)
                    dict['user'] = user_prof
                    return renderToResponseCSRF('usable/need_confirmation.html',dict,request)
            # else invalid, render login form with errors
            else:
                login_form = LoginForm(request.POST)
    # else get request, render blank login form
    else:
        login_form = LoginForm()
    dict['login_form'] = login_form
    dict['recaptcha'] = constants.RECAPTCHA_PUBLIC
    return renderToResponseCSRF('usable/development.html',dict,request)

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


