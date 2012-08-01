SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $SCRIPTPATH/initializeCongressVotes.py > /log/legislation/votes_log.txt &

