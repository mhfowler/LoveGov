# script is run every hour

RUN="/srv/server/scripts/dev/dev_run.sh"
PROJECT="/srv/dev/lovegov"

# update feeds
$RUN python $PROJECT/scripts/scheduled.py update hot_scores

# update index
#$RUN python $PROJECT/dev_manage.py update_index --remove
