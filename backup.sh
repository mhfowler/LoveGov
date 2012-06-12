SCRIPT=`readlink -f $0`
# Absolute path this script is in
SCRIPTPATH=`dirname $SCRIPT`
echo 'whereami: '$SCRIPTPATH
python $SCRIPTPATH/lovegov/live_manage.py dumpdata > $SCRIPTPATH/backup/backup.json
