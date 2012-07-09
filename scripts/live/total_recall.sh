echo "dump db"
mysqldump live -u root -p --complete-insert > $1/db.sql
echo "backup folder"
sudo cp -r /srv/live $1/backup
