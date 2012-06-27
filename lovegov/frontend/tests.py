from lovegov.frontend.views import *

def testBase(request, vals):
    frame(request, vals)
    return renderToResponseCSRF('development/base.html', vals, request)

def wsgi(request):
    return HttpResponse("it doesn't work except for new urls.")

def test(request, vals={}):
    user = vals['viewer']
    vals['main_topics'] = Topic.objects.filter(topic_text__in=MAIN_TOPICS)
    return renderToResponseCSRF('test/newtest.html',vals,request)

def test2(request, vals={}):
    if fbWallShare(request, 608803161):
        return HttpResponse("oh baby")
    return HttpResponse("fuck")

def test3(request, vals={}):

    frame(request, vals)

    vals['p'] = Petition.objects.all()[0]

    setPageTitle("lovegov: beta",vals)
    html = ajaxRender('test/petition.html', vals, request)
    url = '/test3/'
    return framedResponse(request, html, url, vals)


def css(request, vals={}):
    return renderToResponseCSRF('test/css.html', vals, request)

