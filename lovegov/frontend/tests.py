from lovegov.frontend.views import *

def testBase(request, vals):
    frame(request, vals)
    return renderToResponseCSRF('development/base.html', vals, request)

def wsgi(request):
    return HttpResponse("it doesn't work except for new urls.")

def test(request, vals={}):
    user = vals['viewer']
    vals['main_topics'] = Topic.objects.filter(topic_text__in=MAIN_TOPICS)
    return renderToResponseCSRF('test/sorl_test.html',vals,request)

def test2(request, vals={}):
    if fbWallShare(request, 608803161):
        return HttpResponse("oh baby")
    return HttpResponse("fuck")

def test3(request, vals={}):

    frame(request, vals)

    html = ajaxRender('test/tooltip.html', vals, request)
    url = '/test3/'
    return framedResponse(request, html, url, vals)


def test4(request, vals={}):

    return renderToResponseCSRF(template='test/tooltip2.html', vals=vals, request=request)


def css(request, vals={}):
    return renderToResponseCSRF('test/css.html', vals, request)


def fbTest(request, vals):

    viewer = vals['viewer']

    fb_return = fbGet(request,'me/')
    fb_id = fb_return['id']
    picture_url = "https://graph.facebook.com/" + fb_id + "/picture?type=large"
    urlSavePhoto(picture_url, '/Users/maxfowler/Desktop/', 'fbtest')

    return renderToResponseCSRF(template='test/fb_test.html', vals=vals, request=request)

    """
    if viewer.facebook_id:
        fb_return = fbGet(request,'me/friends/')
        if fb_return:
            friends_list = fb_return['data']
            vals['facebook_authorized'] = False
            if friends_list:
                vals['facebook_authorized'] = True
                for friend in random.sample(friends_list, 4):
                    fb_friend = FBFriend()
                    fb_friend.name = friend['name']
                    fb_friend.id = friend['id']
                    fb_friend.picture_url = "https://graph.facebook.com/" + str(fb_friend.id) + "/picture?type=large"
                    fb_friends.append(fb_friend)
                    vals['facebook_friends'] = fb_friends

    return fb_friends

    vals['fb_image'] = 'what'
    return renderToResponseCSRF(template='test/fb_test.html', vals=vals, request=request)
    """

