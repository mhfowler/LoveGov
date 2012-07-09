PRE="/srv/server"

# reset db
echo "cleardb?"
#read \n
sudo mysql --user=root --password=texers787 < $PRE/scripts/mysql/dev_reset.sql 

# dump questions and topics from live db
echo "dumpdata?"
#read \n
sudo /srv/server/scripts/live/live_backup.sh /dump/live_to_dev.sql

# load data from dump
echo "loaddata?"
#read \n
sudo mysql --user=root --password=texers787 dev < /dump/live_to_dev.sql

# copy over media files
echo "copymedia?"
#read \n
#cp -r /media/live/* /media/dev/* --force

# rebuild search indexi
echo "searchindex?"
#read \n
$PRE/scripts/dev/dev_index.sh
