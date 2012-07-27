#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH 

# env
source $SCRIPTPATH/local_env.sh

#setup
python $SCRIPTPATH/lovegov/local_manage.py syncdb
python $SCRIPTPATH/lovegov/local_manage.py loaddata $SCRIPTPATH/lovegov/db/testdata.json
python $SCRIPTPATH/lovegov/scripts/scheduled.py initialize testdata
