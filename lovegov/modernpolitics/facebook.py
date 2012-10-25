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
from urllib import urlopen, urlretrieve
from images import downloadImage
import pprint

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
    fb_link =  "https://www.facebook.com/dialog/oauth?"
    fb_link += "client_id=" + settings.FACEBOOK_APP_ID
    fb_link += "&redirect_uri=" + redirect_uri
    fb_link += "&scope=" + scope
    fb_link += "&state=" + str(fb_state)
    fb_link += "&response_type=code"
    return fb_link, fb_state

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
                control = createFBUser(name, fb_email, request=request)
                user_prof = control.user_profile
                vals['viewer'] = user_prof
                user_prof.facebook_id = fb_id
                user_prof.refreshFB(me)
                fbMakeFriends(request, vals)
                temp_file = saveFBProfPic(request)
                user_prof.setProfileImage(file(temp_file))
                user_prof.save()

        if refresh:                     # if not register and user.first_login=True
            user_prof.refreshFB(me)

        # login
        user = user_prof.user
        if not user:
            raise LGException("FB Login resulted in user that was NoneType. Fb return was: " + str(me))
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)
        return user_prof




def connectWithFacebook(request, to_page="/match/friends/", vals={}):

    viewer = vals['viewer']

    me = fbGet(request, 'me')

    if not me: #If there's no access token
        raise LGException(enc("fb connect: no me returned by fb for " + viewer.get_name()))

    elif 'error' in me: #If there's
        raise LGException(enc("fb connect: fb error for " + viewer.get_name()))

    else:
        fb_id = me['id']
        already = UserProfile.objects.filter(facebook_id=fb_id)
        if already:
            raise LGException(enc(viewer.get_name() + " tried to connect profile with fb account that was already connected to some other profile. " + str(fb_id)))
        else:
            viewer.facebook_id = fb_id
            viewer.refreshFB(me)
            fbMakeFriends(request, vals)
            if not viewer.profile_image:
                temp_file = saveFBProfPic(request)
                viewer.setProfileImage(file(temp_file))
            viewer.save()
            return shortcuts.redirect("/login" + to_page.replace("/login/", "/"))



#-----------------------------------------------------------------------------------------------------------------------
# Get something from facebook api.
#-----------------------------------------------------------------------------------------------------------------------
def fbGet(request, path):
    access_token = request.COOKIES.get('fb_token')
    if access_token:
        url = "https://graph.facebook.com/" + path
        if '?' in path: url += '&'
        else: url += '?'
        url += "access_token=" + access_token

        returned = urlopen(url).read()
        response = json.loads(returned)
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
    link = DEFAULT_FACEBOOK_LINK
    share_id = me['id']
    #Look for Custom Post Variables
    if fb_share_to: # If there's a custom share id, use it
        share_id = fb_share_to
    message = DEFAULT_FACEBOOK_MESSAGE
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

## save fb photo of user ##
def saveFBProfPic(request):
    fb_return = fbGet(request,'me/')
    fb_id = fb_return['id']
    picture_url = "https://graph.facebook.com/" + fb_id + "/picture?type=large"
    file_name = 'fb_temp_' + str(random.randint(0,100))
    urlSavePhoto(picture_url, TEMPDIR, file_name)
    return TEMPDIR + file_name + ".png"

## save photo from url to disc ##
def urlSavePhoto(url, file_save_dir, filename):
    urlretrieve (url, os.path.join(file_save_dir, filename + '.png'))

