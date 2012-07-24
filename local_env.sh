# absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

#path stuff
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH
export PYTHONPATH=${PYTHONPATH}:$SCRIPTPATH/lovegov
export DJANGO_SETTINGS_MODULE=lovegov.local_settings

# run commands if given
$1 $2 $3 $4 $5 $6 $7 $8
