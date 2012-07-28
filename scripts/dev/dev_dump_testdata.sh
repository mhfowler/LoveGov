DEV="/srv/dev"
RUN="/srv/server/scripts/dev/dev_run.sh"

$RUN python $DEV/lovegov/dev_manage.py dumpdata modernpolitics.topic modernpolitics.question modernpolitics.answer modernpolitics.content > $1 
