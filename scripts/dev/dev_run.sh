# set environmental variables
export PYTHONPATH=${PYTHONPATH}:/srv/dev
export PYTHONPATH=${PYTHONPATH}:/srv/dev/lovegov
export DJANGO_SETTINGS_MODULE=lovegov.dev_settings
# run command
$1 $2 $3 $4 $5 $6 $7 $8

