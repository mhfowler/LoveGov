echo "dump db"
mysqldump --host=lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com --user=root --password=lglglg12 --complete-insert lglive > $1/db.sql
echo "backup folder"
sudo cp -r /srv/live/lovegov $1/lovegov
