SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup ./initializeAmendments.py > /log/legislation/amendments_log.txt &
