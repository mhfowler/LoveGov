HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $HERE/initializeCongressVotes.py > /log/legislation/votes_log.txt &

