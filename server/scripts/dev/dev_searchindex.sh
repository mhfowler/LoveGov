# rebuild search index
echo "y\n" | python /srv/dev/lovegov/dev_manage.py rebuild_index
# reset permissions on search index
chmod -R 770 /srv/dev/lovegov/beta/modernpolitics/search_indexes
chgrp -R access /srv/dev/lovegov/beta/modernpolitics/search_indexes

