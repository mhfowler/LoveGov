# script is run every day

RUN="/srv/server/scripts/dev/dev_run.sh"
PROJECT="/srv/dev/lovegov"

# update lovegov group and user responses
$RUN python $PROJECT/scripts/daily_summary.py
$RUN python $PROJECT/scripts/scheduled.py update groupviews
$RUN python $PROJECT/scripts/scheduled.py update lovegovresponses
