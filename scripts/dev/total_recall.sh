echo "dump db"
mysqldump dev -u root -p --complete-insert > $1/db.sql
echo "backup folder"
sudo cp -r /srv/dev/lovegov $1/lovegov
