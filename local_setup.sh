#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH 

#path stuff
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH/lovegov
export DJANGO_SETTINGS_MODULE=lovegov.local_settings

#setup
python $SCRIPTPATH/lovegov/local_manage.py syncdb
python $SCRIPTPATH/lovegov/local_manage.py loaddata $SCRIPTPATH/lovegov/db/migrate.json
python $SCRIPTPATH/lovegov/scripts/scheduled.py initialize testdata
