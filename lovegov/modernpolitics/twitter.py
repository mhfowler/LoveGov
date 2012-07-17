#   Twitter authentication flow.
#   - try to log in with twitter (twitterTryLogin)
#   - if no twitter_access_token, redirect to twitter (twitterRedirect)
#   - other side of redirect is twitter handle,
#          - if registered user associated with twitter_access token, then log that user in
#          - if no registered user, then redirect to /twitter/register (twitterRegister)

from lovegov.modernpolitics.facebook import *

#-----------------------------------------------------------------------------------------------------------------------
# try to login with twitter, if no acces token, redirec to twitter
#-----------------------------------------------------------------------------------------------------------------------
def twitterTryLogin(request, to_page="/home/", vals={}):

    success = twitterLogin(request, to_page, vals)
    if success:
        return success
    else:
        return shortcuts.redirect('/twitter/redirect/')

#-----------------------------------------------------------------------------------------------------------------------
# redirect to twitter, to get twitter access token
#-----------------------------------------------------------------------------------------------------------------------
def twitterRedirect(request, redirect_uri=None):

    if not redirect_uri:
        redirect_uri = getRedirectURI(request, "/twitter/handle/")

    request_token_url = 'http://twitter.com/oauth/request_token'
    authorize_url = 'http://twitter.com/oauth/authorize'

    consumer = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    print "Request Token:"
    print "    - oauth_token        = %s" % request_token['oauth_token']
    print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    print "twit redirect: ", redirect_uri
    print

    to_encode = {'oauth_token':request_token['oauth_token'],'oauth_callback':redirect_uri}
    redirect = authorize_url + "?"
    redirect += urlencode(to_encode)

    response = shortcuts.redirect(redirect)
    response.set_cookie('twitter_secret', request_token['oauth_token_secret'])

    return response

#-----------------------------------------------------------------------------------------------------------------------
# on opposite side of twitter redirect, handle response by setting access token as cookie, and logging in or redirecting
# to /twitter/register/
#-----------------------------------------------------------------------------------------------------------------------
def twitterHandle(request, to_page="/home/", vals={}):
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    oauth_token_secret = request.COOKIES.get('twitter_secret')
    consumer = oauth.Consumer(settings.TWITTER_KEY, settings.TWITTER_SECRET)
    access_token_url = 'http://twitter.com/oauth/access_token'
    token = oauth.Token(oauth_token, oauth_token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above."
    print

    response = twitterLogin(request, to_page, vals=vals)
    if not response:
        response = shortcuts.redirect('/twitter/register/')

    response.set_cookie("twitter_access_token", access_token)

    return response

#-----------------------------------------------------------------------------------------------------------------------
# return true if succesfully logged in with twitter, or return false otherwise
#-----------------------------------------------------------------------------------------------------------------------
def twitterLogin(request, to_page="/web/", vals={}):
    tat = tatHelper(request)
    if tat:
        twitter_user_id = tat['user_id']
        user_prof = UserProfile.lg.get_or_none(twitter_user_id=twitter_user_id)
        if user_prof:
            user_prof.twitter_screen_name = tat['screen_name']
            user_prof.save()
            user = user_prof.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            return shortcuts.redirect(to_page)
        else:
            return False
    else:
        return False

#-----------------------------------------------------------------------------------------------------------------------
# tries to create a user account from form post and twitter access token,
# - if invalid returns forms with errors
# - if not twitter access token redirects
#-----------------------------------------------------------------------------------------------------------------------
def twitterRegister(request, vals={}):

    from lovegov.modernpolitics.register import createTwitterUser

    if request.method == 'POST':
        name = request.POST.get('twitter_name')
        email = request.POST.get('twitter_email')
        zip =  request.POST.get('twitter_zip')

        valid, twitter_name_error, twitter_email_error = validateTwitterForm(name, email)

        vals['twitter_name_error'] = twitter_name_error
        vals['twitter_email_error'] = twitter_email_error
        vals['twitter_zip'] = zip

        if valid:
            tat = tatHelper(request)
            if tat:                                                 # ready to twitter register
                twitter_user_id = tat['user_id']
                already = UserProfile.lg.get_or_none(twitter_user_id = twitter_user_id)
                if already:
                    return twitterTryLogin(request, to_page="/home/", vals=vals)
                else:
                    control = createTwitterUser(name, email, vals=vals)
                    user_prof = control.user_profile
                    vals['viewer'] = user_prof
                    user_prof.twitter_user_id = tat['user_id']
                    user_prof.save()
                    if zip:
                        user_prof.setZipCode(zip)
                    return renderToResponseCSRF(template='deployment/pages/login/login-main-register-success.html', vals=vals, request=request)
            else:
                response = shortcuts.redirect("/twitter/redirect/")
                return response

    vals['state'] = 'post-twitter'
    return renderToResponseCSRF(template='deployment/pages/login/login-main.html', vals=vals, request=request)

#-----------------------------------------------------------------------------------------------------------------------
# helper which returns dictionary from twitter access token cookie if it exists
#-----------------------------------------------------------------------------------------------------------------------
def tatHelper(request):
    twitter_access_token = request.COOKIES.get('twitter_access_token')
    if twitter_access_token:
        tat = twitter_access_token.replace('\'','\"')
        tat = json.loads(str(tat))
        return tat
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# helper which validates twitter post redirect registration form, returns tuple of (valid, name_error, email_error)
#-----------------------------------------------------------------------------------------------------------------------
def validateTwitterForm(name, email):

    valid = True
    if not email:
        valid = False
        twitter_email_error = "email"
    elif not "@" in email:
        valid = False
        twitter_email_error = "email"
    elif ControllingUser.lg.get_or_none(username=email):
        valid = False
        twitter_email_error = "User with given email already has registered."
    else:
        twitter_email_error = email

    if not name:
        valid = False
        twitter_name_error = "full name"
    else:
        splitted = name.split()
        length = len(splitted)
        if length <2:
            valid = False
            twitter_name_error = "full name"
        else:
            twitter_name_error = name

    return valid, twitter_name_error, twitter_email_error


