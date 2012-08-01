SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup "$SCRIPTPATH"/initializeAmendments.py > /log/legislation/amendments_log.txt &
