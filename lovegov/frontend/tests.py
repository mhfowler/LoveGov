from lovegov.frontend.views import *

def testBase(request, vals):
    frame(request, vals)
    return renderToResponseCSRF('development/base.html', vals, request)

def wsgi(request):
    return HttpResponse("it doesn't work except for new urls.")

def test(request, vals={}):
    user = vals['user']
    vals['notifications_dropdown'] = user.getNotifications(num=5, dropdown=True)
    vals['notifications_profile'] = user.getNotifications()
    vals['notifications_all'] = user.getAllNotifications()
    vals['actions'] = user.getActivity()
    return renderToResponseCSRF('test/newtest.html',vals,request)

def test2(request, vals={}):
    if fbWallShare(request, 608803161):
        return HttpResponse("oh baby")
    return HttpResponse("fuck")

