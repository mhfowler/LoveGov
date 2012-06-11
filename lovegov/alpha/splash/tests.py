from lovegov.alpha.splash import *
from django.http import HttpResponse
from lovegov.beta.modernpolitics import facebook as fb

def testBase(request, dict):
    frame(request, dict)
    return betaviews.renderToResponseCSRF('development/base.html', dict, request)

def wsgi(request):
    return HttpResponse("it doesn't work except for new urls.")

def test(request, dict={}):
    return renderToResponseCSRF('test/test.html',dict,request)

def test2(request, dict={}):
    if fb.fbWallShare(request, 608803161):
        return HttpResponse("oh baby")
    return HttpResponse("fuck")

