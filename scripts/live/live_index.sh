# rebuild search index
echo "y\n" | python /srv/live/lovegov/live_manage.py rebuild_index
# reset permissions on search index
sudo chmod -R 770 /srv/live/lovegov/modernpolitics/search_indexes
sudo chgrp -R access /srv/live/lovegov/modernpolitics/search_indexes

