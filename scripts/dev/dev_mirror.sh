PRE="/srv/server"

# reset db
echo "cleardb?"
#read \n
$PRE/scripts/mysql/remote_mysql.sh < $PRE/scripts/mysql/dev_reset.sql 

# dump all data from live
echo "dumpdata?"
#read \n
/srv/server/scripts/live/live_backup.sh /dump/live_to_dev.sql

# load data from dump
echo "loaddata?"
#read \n
$PRE/scripts/mysql/remote_mysql.sh lgdb < /dump/live_to_dev.sql

# copy over media files
echo "copymedia?"
#read \n
$PRE/scripts/dev/dev_mirror_media.sh

# rebuild search indexi
echo "searchindex?"
#read \n
$PRE/scripts/dev/dev_index.sh
