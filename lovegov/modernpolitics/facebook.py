########################################################################################################################
########################################################################################################################
#
#           Facebook + Twitter
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.initialize import *

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
    if user.getFBAlias() == '':
        return False
    path = user.getFBAlias() + '/friends'
    response =  fbGet(request, path)
    if 'data' in response:
        friends = response['data']
        for f in friends:
            friend = UserProfile.lg.get_or_none( facebook_id=f['id'] )
            if friend:
                user.follow( friend , fb=True )
                friend.follow( user , fb=True )
        return True
    return False


#-----------------------------------------------------------------------------------------------------------------------
# Put in authenticate link.
#-----------------------------------------------------------------------------------------------------------------------
def fbGetRedirect(request, vals={}, redirect_uri=None, scope=FACEBOOK_SCOPE):
    if not redirect_uri:
        redirect_uri = getRedirectURI(request, "/fb/handle/")
    fb_state = random.randint(0, 100000)
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
    normal_logger.debug("Facebook Access Token Error (in fbGetAccessToken): " + str(returned))
    return None

#-----------------------------------------------------------------------------------------------------------------------
# Handles access token, and log in, register or deny appropriately
#-----------------------------------------------------------------------------------------------------------------------
def fbLogin(request, vals={}, refresh=False):

    from lovegov.modernpolitics.register import createFBUser
    me = fbGet(request, 'me')

    if not me: #If there's no access token
        return False

    elif 'error' in me: #If there's
        fb_error = "Facebook login error: " + pprint.pformat(me)
        normal_logger.debug(fb_error)
        return False

    else:
        fb_id = me['id']
        fb_email = me['email']
        user_prof = UserProfile.lg.get_or_none(facebook_id=fb_id)
        # if there is not lg user with fb id, check for user with same email
        if not user_prof:
            user_prof = UserProfile.lg.get_or_none(email=fb_email)

            # REGISTER
            if not user_prof:
                refresh = False
                name = (me.get('first_name') or "Unknown") + " " + (me.get('last_name') or "User")
                control = createFBUser(name, fb_email)
                user_prof = control.user_profile
                vals['viewer'] = user_prof
                user_prof.facebook_id = fb_id
                user_prof.refreshFB(me)
                fbMakeFriends(request, vals)
                user_prof.save()

        if refresh:                     # if not register and user.first_login=True
            user_prof.refreshFB(me)

        # login
        user = user_prof.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)
        return True


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

