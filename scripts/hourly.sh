# script is run every hour

RUN="/srv/server/scripts/live/live_run.sh"
PROJECT="/srv/live/lovegov"

# update feeds
$RUN python $PROJECT/scripts/scheduled.py update sitefeeds
