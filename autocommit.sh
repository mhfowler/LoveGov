#absolute path to this script
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo 'whereami: '$SCRIPTPATH

# parse arguments
if [ $# -gt 1 ]; then
	COMMIT=$SCRIPTPATH/$1
	MESSAGE=$2
else
	COMMIT=$SCRIPTPATH
	MESSAGE=$1
fi

echo 'commit: '$COMMIT
echo 'mess: '$MESSAGE

# commit
sudo svn add $COMMIT/* --force
sudo svn commit $COMMIT -m "$MESSAGE" --username modernpolitics --password P0litics!

# changelog
CLOG=$SCRIPTPATH/changelog.txt
echo $(date)' by '$(whoami) >> $CLOG
echo >> $CLOG
echo $MESSAGE >> $CLOG
echo >> $CLOG
echo -------------------------- >> $CLOG

if [ $COMMIT != $SCRIPTPATH ]; then
	echo 'changelog: '$CLOG
	sudo svn commit $CLOG -m "update changelog" --username modernpolitics --password P0litics!
fi
