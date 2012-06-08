# script is run every day

RUN="/srv/server/scripts/live/live_run.sh"
PROJECT="/srv/live/lovegov"

# update lovegov group and user responses
$RUN python $PROJECT/beta/modernpolitics/scripts.py update lovegovresponses
