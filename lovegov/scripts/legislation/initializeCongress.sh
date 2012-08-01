SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $SCRIPTPATH/initializeCongress.py > /log/legislation/congress_log.txt &
