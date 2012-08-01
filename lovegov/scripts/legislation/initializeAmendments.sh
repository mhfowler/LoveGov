HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $HERE/initializeAmendments.py > /log/legislation/amendments_log.txt &
