# celery tasks
from lovegov.modernpolitics.initialize import *
from celery.task.base import task

@task
def testTask(message):
    temp_logger.debug("celery message! \n" + message)
    return message

@task
def saveAccess(request):
    PageAccess().autoSave(request)











