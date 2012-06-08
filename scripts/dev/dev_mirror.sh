PRE="/srv/server"

# reset db
echo "cleardb?"
read \n
mysql --user=root --password=texers787 < $PRE/scripts/mysql/dev_reset.sql 

# dump questions and topics from live db
echo "dumpdata?"
read \n
/srv/server/scripts/live/live_backup.sh /dump/live_to_dev.sql

# load data from dump
echo "loaddata?"
read \n
mysql --user=root --password=texers787 dev < /dump/live_to_dev.sql

# copy over media files
cp -r /media/live/* /media/dev/* --force

# rebuild search index
$PRE/scripts/dev/dev_searchindex.sh
