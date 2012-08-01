SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup ./initializeLegislation.py > /log/legislation/legislation_log.txt &

