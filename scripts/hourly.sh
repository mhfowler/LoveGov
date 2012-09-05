# script is run every hour

RUN="/srv/server/scripts/dev/dev_run.sh"
PROJECT="/srv/dev/lovegov"

# update index

$RUN python $PROJECT/live_manage.py update_index --remove
