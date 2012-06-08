# set environmental variables
export PYTHONPATH=${PYTHONPATH}:/srv/live
export PYTHONPATH=${PYTHONPATH}:/srv/live/lovegov
export DJANGO_SETTINGS_MODULE=lovegov.live_settings
# run command
$1 $2 $3 $4 $5 $6 $7 $8

