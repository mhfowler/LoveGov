#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# cleardb
rm $SCRIPTPATH/lovegov/db/local.db

# setup
$SCRIPTPATH/local_setup_with_initialize.sh

# dump result
echo "dumping result."
python $SCRIPTPATH/lovegov/local_manage.py dumpdata modernpolitics > $SCRIPTPATH/lovegov/tests/fixtures/test_fixture.json

