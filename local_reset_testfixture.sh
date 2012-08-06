#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# cleardb
rm $SCRIPTPATH/lovegov/db/local.db

# setup
$SCRIPTPATH/local_setup_with_initialize.sh

# dump result
python $SCRIPTPATH/lovegov/local_manage.py dumpdata > $SCRIPTPATH/lovegov/db/test_fixture.json

