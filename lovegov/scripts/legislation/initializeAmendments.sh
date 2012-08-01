SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $SCIRPTPATH/initializeAmendments.py > /log/legislation/amendments_log.txt &
