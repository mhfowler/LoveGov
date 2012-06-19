########################################################################################################################
########################################################################################################################
#
#           Facebook + Twitter
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.defaults import *

# django
from django.contrib import auth

# python
from urllib import urlopen
import pprint
import urlparse
import oauth2 as oauth

#-----------------------------------------------------------------------------------------------------------------------
# Save a users facebook friends as lg relationships.
#-----------------------------------------------------------------------------------------------------------------------
def fbMakeFriends(request, vals={}):
    user = vals['viewer']
    path = user.getFBAlias() + '/friends'
    response =  fbGet(request, path)
    if response:
        friends = response['data']
        for f in friends:
            friend = UserProfile.lg.get_or_none( facebook_id=f['id'] )
            if friend:
                user.follow( friend , fb=True )
                friend.follow( user , fb=True )

#-----------------------------------------------------------------------------------------------------------------------
# Put in authenticate link.
#-----------------------------------------------------------------------------------------------------------------------
def fbGetRedirect(request, vals={}, redirect_uri=None, scope="email"):
    if not redirect_uri:
        redirect_uri = getRedirectURI(request, "/fb/handle/")
    fb_state = random.randint(0, 1000)
    url =  "https://www.facebook.com/dialog/oauth?"
    url += "client_id=" + settings.FACEBOOK_APP_ID
    url += "&redirect_uri=" + redirect_uri
    url += "&scope=" + scope
    url += "&state=" + str(fb_state)
    url += "&response_type=code"
    vals['fb_link'] = url
    return fb_state

def fbGetAccessToken(request, code, redirect_uri=None):
    if not redirect_uri:
        redirect_uri = getRedirectURI(request, "/fb/handle/")
    url = "https://graph.facebook.com/oauth/access_token?"
    url += "client_id=" + settings.FACEBOOK_APP_ID
    url += "&redirect_uri=" + redirect_uri
    url += "&client_secret=" + settings.FACEBOOK_APP_SECRET
    url += "&code=" + code
    returned = urlopen(url).read()
    parameters = returned.split("&")
    for x in parameters:
        splitted = x.split("=")
        key = splitted[0]
        if key == 'access_token':
            print "access_token: " + splitted[1]
            return splitted[1]
    print returned
    return "access_token_error: no access token"

def getRedirectURI(request, redirect):
    absolute_uri = request.build_absolute_uri()
    domain_regex = re.compile('.*\.com')
    regex = domain_regex.match( absolute_uri )
    new_domain = regex.group(0)
    if LOCAL:
        new_domain += ':8000'
    redirect_uri = new_domain + redirect
    return redirect_uri

#-----------------------------------------------------------------------------------------------------------------------
# Handles access token, and log in, register or deny appropriately
#-----------------------------------------------------------------------------------------------------------------------
def fbLogin(request, vals={}):
    from lovegov.modernpolitics.register import createFBUser
    me = fbGet(request, 'me')
    if me:
        fb_id = me['id']
        fb_email = me['email']
        user_prof = UserProfile.lg.get_or_none(facebook_id=fb_id)
        logging.debug("fb")
        # if there is not lg user with fb id, check for user with same email
        if not user_prof:
            logging.debug("fb - by email")
            user_prof = UserProfile.lg.get_or_none(email=fb_email)
            # if there is no user with facebook email
            if not user_prof:
                logging.debug("fb - register")
                name = me['first_name'] + " " + me['last_name']
                control = createFBUser(name, fb_email)
                user_prof = control.user_profile
                user_prof.refreshFB(me)
                vals['viewer'] = user_prof
                fbMakeFriends(request, vals)
        user_prof.refreshFB(me)
        user = user_prof.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)
        return True
    else:
        return False


#-----------------------------------------------------------------------------------------------------------------------
# Get something from facebook api.
#-----------------------------------------------------------------------------------------------------------------------
def fbGet(request, path):
    access_token = request.COOKIES.get('fb_token')
    if access_token:
        url = "https://graph.facebook.com/" + path + "?access_token=" + access_token
        print url
        returned = urlopen(url).read()
        response = json.loads(returned)
        #pprint.pprint(response)
        return response
    else:
        return None


#-----------------------------------------------------------------------------------------------------------------------
# Post something to the facebook api..
#-----------------------------------------------------------------------------------------------------------------------
def fbPost(request, path, post_data):
    access_token = request.COOKIES.get('fb_token')
    if access_token:
        post_data.append( ('access_token',access_token) )
        print 'posting access token: ' + access_token
        url = "https://graph.facebook.com/" + path
        returned = urlopen( url , urlencode(post_data) ).read()
        response = json.loads(returned)
        #pprint.pprint(response)
        return response
    else:
        return None




#-----------------------------------------------------------------------------------------------------------------------
# Shares LoveGov on a someones wall (Default: user wall)
#-----------------------------------------------------------------------------------------------------------------------
def fbWallShare(request, vals={}):
    # Get user FB info
    me = fbGet(request, 'me')
    if not me:
        vals['fb_error'] = "no_response_me"
        return False
    if 'error' in me:
        error = me['error']
        if 'code' in error:
            vals['fb_error'] = error['code']
        return False
    # Get Request Data
    fb_share_to = request.GET.get('fb_share_to')
    fb_share_message = request.GET.get('message')
    fb_link = request.GET.get('fb_link')
    #Set Post Variables
    facebook_id = me['id']
    link = "www.lovegov.com"
    share_id = me['id']
    #Look for Custom Post Variables
    if fb_share_to: # If there's a custom share id, use it
        share_id = fb_share_to
    message = "Compare your political views to mine on LoveGov!"
    if fb_share_message: #If there's a custom message, use it
        message = fb_share_message
    if fb_link: #If there's a custom link, us it
        link = fb_link
    # Set Post Data
    post_data = [   ('from' , facebook_id ),
                    ('message' , message ),
                    ('link' , link )    ]
    # Send Post Data to Facebook
    post_response = fbPost( request , share_id + "/feed/" , post_data )
    #Check for fail
    if not post_response:
        vals['fb_error'] = "no_response_post"
        return False
    if 'error' in post_response:
        error = post_response['error']
        pprint.pprint(error)
        if 'code' in error:
            vals['fb_error'] = error['code']
        return False
    return True

def fbTest(request):
    access_token = request.COOKIES['fb_token']
    url = "https://graph.facebook.com/me?access_token=" + access_token
    returned = urlopen(url).read()
    print returned


#-----------------------------------------------------------------------------------------------------------------------
# Authenticate with twitter.
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
    print

    redirect_uri="http://www.lovegov.com/comingsoon/"

    to_encode = {'oauth_token':request_token['oauth_token'],'oauth_callback':redirect_uri}
    redirect = authorize_url + "?"
    redirect += urlencode(to_encode)

    print "redirect: " + redirect

    response = shortcuts.redirect(redirect)
    response.set_cookie('twitter_secret', request_token['oauth_token_secret'])

    return response

def twitterGetAccessToken(request, to_page="/web/"):
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

    response = shortcuts.redirect(to_page)
    response.set_cookie("twitter_access_token", access_token)

    return response

def twitterLogin(request, to_page="/web/", vals={}):
    twitter_access_token = request.COOKIES.get('twitter_access_token')
    if twitter_access_token:
        tat = twitter_access_token.replace('\'','\"')
        tat = json.loads(str(tat))
        twitter_user_id = tat['user_id']
        user_prof = UserProfile.lg.get_or_none(twitter_user_id=twitter_user_id)
        logging.debug("twitter")
        if not user_prof:
            return twitterRegister(request)
        else:
            user_prof.twitter_screen_name = tat['screen_name']
            user_prof.save()
            user = user_prof.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, user)
            return shortcuts.redirect(to_page)
    else:
        return False


def twitterRegister(request):
    return HttpResponse("enter name, email and password[optional]")