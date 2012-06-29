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

    group = Group.objects.all()[0]
    vals['g'] = group

    histogram = group.getComparisonHistogram(vals['viewer'])
    vals['histogram_json'] = json.dumps(histogram)

    buckets = []
    for bucket in histogram['buckets']:
        buckets.append(bucket)
    buckets.sort()
    vals['buckets'] = buckets

    setPageTitle("lovegov: beta",vals)
    html = ajaxRender('test/petition.html', vals, request)
    url = '/test3/'
    return framedResponse(request, html, url, vals)


def css(request, vals={}):
    return renderToResponseCSRF('test/css.html', vals, request)

