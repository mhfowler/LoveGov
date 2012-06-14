from lovegov.alpha.splash.views import *
from django.http import HttpResponse
from lovegov.beta.modernpolitics import facebook as fb

def testBase(request, dict):
    frame(request, dict)
    return renderToResponseCSRF('development/base.html', dict, request)

def wsgi(request):
    return HttpResponse("it doesn't work except for new urls.")

def test(request, dict={}):
    user = dict['user']
    dict['notifications_dropdown'] = user.getNotifications(num=5, dropdown=True)
    dict['notifications_profile'] = user.getNotifications()
    dict['notifications_all'] = user.getAllNotifications()
    dict['actions'] = user.getActivity()
    return renderToResponseCSRF('test/newtest.html',dict,request)

def test2(request, dict={}):
    if fb.fbWallShare(request, 608803161):
        return HttpResponse("oh baby")
    return HttpResponse("fuck")

