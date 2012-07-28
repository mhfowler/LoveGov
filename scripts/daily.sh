# script is run every day

RUN="/srv/server/scripts/live/live_run.sh"
PROJECT="/srv/live/lovegov"

# update lovegov group and user responses
$RUN python $PROJECT/scripts/daily_summary.py
$RUN python $PROJECT/scripts/scheduled.py update lovegovresponses
$RUN python $PROJECT/scripts/scheduled.py update groupviews
