SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $SCRIPTPATH/initializeLegislation.py > /log/legislation/legislation_log.txt &

