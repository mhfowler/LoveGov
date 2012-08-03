# celery tasks
from lovegov.modernpolitics.initialize import *
from celery.task.base import task

@task
def testTask(message):
    temp_logger.debug("celery message! \n" + message)
    return message


def saveAccess(request):
    user_prof_id = getUserProfile(request).id
    page = getSourcePath(request)
    ipaddress = request.META['REMOTE_ADDR']
    type = request.method
    if type == 'POST' and 'action' in request.POST:
        action = request.POST['action']
    elif 'action' in request.GET:
        action = request.GET['action']
    else:
        action = None
    when = datetime.datetime.now()
    task_saveAccess.delay(user_prof_id, page, ipaddress, type, action, when)
@task
def task_saveAccess(user_prof_id, page, ipaddress, type, action, when):
    PageAccess(user_id=user_prof_id,
                page=page,
                ipaddress=ipaddress,
                type=type,
                action=action,
                when=when).save()











