#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

# cleardb
rm $SCRIPTPATH/lovegov/db/local.db

# resetup
$SCRIPTPATH/local_setup.sh