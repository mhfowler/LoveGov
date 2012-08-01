HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $HERE/initializeCongress.py > /log/legislation/congress_log.txt &
