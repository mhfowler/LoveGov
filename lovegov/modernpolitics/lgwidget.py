########################################################################################################################
########################################################################################################################
#
#           LoveGov Widget
#
#
########################################################################################################################
########################################################################################################################

# django
from django.http import *

# python
from random import sample

# lovegov
from lovegov.modernpolitics.initialize import *

#-----------------------------------------------------------------------------------------------------------------------
# Widget switcher, also saves widget access.
#-----------------------------------------------------------------------------------------------------------------------
def access(request):
    host = request.GET.get('host')
    path = request.GET.get('path')
    which = request.GET.get('which')
    WidgetAccess(host=host, path=path, which=which).save()
    if which=='questions':
        return questions(request)
    else:
        return questions(request)

#-----------------------------------------------------------------------------------------------------------------------
# Displays a few lovegov questions.
#-----------------------------------------------------------------------------------------------------------------------
def questions(request, vals={}):
    random = request.GET.get('random')
    if not random:
        random=3
    ids = request.GET.get('selected')
    if not ids:
        ids = []
    vals['widget_domain'] = 'http://dev.lovegov.com'
    if random:
        questions = Question.objects.all()
        sample_size = min(random, len(questions))
        random_questions = sample(questions, sample_size)
        vals['random_questions'] = random_questions
    if ids:
        selected_questions = Question.objects.filter(id__in=ids)
        vals['selected_questions'] = selected_questions
    html = ajaxRender('widget/top_sidebar_main.html', request=request, vals=vals)
    to_return = {'html': html}
    callback = request.GET.get('callback', '')
    response = json.dumps(to_return)
    response = callback + '(' + response + ');'
    return HttpResponse(response)