# rebuild search index
echo "y\n" | python /srv/live/lovegov/live_manage.py rebuild_index
# reset permissions on search index
chmod -R 770 /srv/live/lovegov/modernpolitics/search_indexes
chgrp -R access /srv/live/lovegov/modernpolitics/search_indexes

