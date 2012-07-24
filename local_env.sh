# absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

#path stuff
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH/lovegov
export DJANGO_SETTINGS_MODULE=lovegov.local_settings
