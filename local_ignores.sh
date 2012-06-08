# absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
echo 'whereami: '$SCRIPTPATH

# local ignores
sudo svn propset svn:ignore $SCRIPTPATH/.idea/ $SCRIPTPATH

