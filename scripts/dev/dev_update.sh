# svn update
sudo svn update /srv/dev
# collect static
python /srv/dev/lovegov/dev_manage.py collectstatic --noinput
# reset permissions
chmod -R 770 /static/dev
chgrp -R access /static/dev
# rewsgi
sudo touch /srv/dev/lovegov/apache/dev.wsgi
