# check if absoulte path
case $1 in
     /*) PRE="" ;;	# absolute path
     *) PRE=$PWD ;;	# relative path
esac
echo PRE: $PRE
# chgrp everything
sudo chgrp -R access $PRE/$1
# give all directories read and execute permission
for f in $(find $1 -type d)
do sudo chmod 550 $PRE/$f
done
# give all other files in directory read permission
for f in $(find $1 -type f)
do sudo chmod 440 $PRE/$f
done
# give all .sh files exec permission
for f in $(find $1 -name "*.sh"  -type f)
do sudo chmod 550 $PRE/$f
done
# give writing permission to all .log files
for f in $(find $1 -name "*.log"  -type f)
do sudo chmod 660 $PRE/$f
done
