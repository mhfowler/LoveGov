# absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

source $SCRIPTPATH/remote_env.sh

# runserver
python $SCRIPTPATH/lovegov/devremote_manage.py runserver

