# svn update
sudo svn update /srv/live
# collect static
python /srv/live/lovegov/live_manage.py collectstatic
# reset permissions
chmod -R 770 /static/live
chgrp -R access /static/live
# rewsgi
sudo touch /srv/live/lovegov/apache/live.wsgi
