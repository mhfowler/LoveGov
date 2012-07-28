echo "dump db"
/srv/server/scripts/live/live_backup.sh $1/db.sql
echo "backup folder"
sudo cp -r /srv/live $1/code
echo "backup media"
sudo cp -r /media/live $1/media
