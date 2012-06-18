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
from lovegov.modernpolitics.defaults import *

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
def questions(request, dict={}):
    random = request.GET.get('random')
    if not random:
        random=3
    ids = request.GET.get('selected')
    if not ids:
        ids = []
    dict['widget_domain'] = 'http://dev.lovegov.com'
    if random:
        questions = Question.objects.all()
        sample_size = min(random, len(questions))
        random_questions = sample(questions, sample_size)
        dict['random_questions'] = random_questions
    if ids:
        selected_questions = Question.objects.filter(id__in=ids)
        dict['selected_questions'] = selected_questions
    html = ajaxRender('widget/questions.html', request=request, dict=dict)
    to_return = {'html': html}
    callback = request.GET.get('callback', '')
    response = json.dumps(to_return)
    response = callback + '(' + response + ');'
    return HttpResponse(response)