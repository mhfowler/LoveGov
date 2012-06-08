# returns absolute path to inputted path
case $1 in
     /*) PRE=$1 ;;      # absolute path
     *) PRE=$PWD/$1 ;;     # relative path
esac
echo $PRE
