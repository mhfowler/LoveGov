HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

nohup $HERE/initializeLegislation.py > /log/legislation/legislation_log.txt &

