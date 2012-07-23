# absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

source $SCRIPTPATH/local_env.sh

# runserver
python $SCRIPTPATH/lovegov/local_manage.py runserver

