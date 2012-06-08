
### INTERNAL ###
from lovegov.beta.modernpolitics import models, backend
from lovegov.beta.modernpolitics.models import UserProfile
from lovegov.local_manage import LOCAL

### DJANGO ###
from django.contrib import auth
from django import shortcuts
from django.http import *

### EXTERNAL ####
from urllib import urlopen
import re
import random
import json
import logging
import pprint
import logging

logger = logging.getLogger('filelogger')

#-----------------------------------------------------------------------------------------------------------------------
# Save a users facebook friends as lg relationships.
#-----------------------------------------------------------------------------------------------------------------------
def fbGetFriends(request, dict={}):
    user = dict['user']
    path = user.getFBAlias() + '/friends'
    print "path: " + path
    response =  fbGet(request, path)
    if response:
        friends = response['data']
        for f in friends:
            friend = UserProfile.lg.get_or_none( facebook_id=f['id'] )
            if friend:
                user.makeFriends( friend )
        flist = models.UserFollow.objects.filter( user=user )
        return_string = ""
        for x in flist:
            return_string += " || " + x.to_user.get_name()
        return HttpResponse( return_string )
    else:
        return HttpResponse( "FAIL" )


#-----------------------------------------------------------------------------------------------------------------------
# Put in authenticate link.
#-----------------------------------------------------------------------------------------------------------------------
def fbGetRedirect(request, dict={}, redirect_uri=None, scope="email"):
    if not redirect_uri:
        redirect_uri = getRedirectURI(request, "/fb/handle/")
    fb_state = random.randint(0, 1000)
    url =  "https://www.facebook.com/dialog/oauth?"
    url += "client_id=" + settings.FACEBOOK_APP_ID
    url += "&redirect_uri=" + redirect_uri
    url += "&scope=" + scope
    url += "&state=" + str(fb_state)
    url += "&response_type=code"
    dict['fb_link'] = url
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
def fbLogin(request):
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
                control = backend.createUser(name, fb_email, 'password')
                user_prof = control.user_profile
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
def fbWallShare(request, dict={}):
    # Get user FB info
    me = fbGet(request, 'me')
    if not me:
        dict['fb_error'] = "no_response_me"
        return False
    if 'error' in me:
        error = me['error']
        if 'type' in error:
            dict['fb_error'] = error['type']
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
        dict['fb_error'] = "no_response_post"
        return False
    if 'error' in post_response:
        error = post_response['error']
        pprint.pprint(error)
        if 'type' in error:
            dict['fb_error'] = error['type']
        return False
    return True

def fbTest(request):
    access_token = request.COOKIES['fb_token']
    url = "https://graph.facebook.com/me?access_token=" + access_token
    returned = urlopen(url).read()
    print returned


