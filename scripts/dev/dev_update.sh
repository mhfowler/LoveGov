# git pull
cd /srv/dev
sudo git pull
# sass
/srv/server/scripts/dev/dev_run.sh python /srv/dev/lovegov/bash/sasscompile.py
# collect static
sudo python /srv/dev/lovegov/dev_manage.py collectstatic --noinput
# reset permissions
sudo chmod -R 770 /static/dev
sudo chgrp -R access /static/dev
# rewsgi
sudo touch /srv/dev/lovegov/apache/dev.wsgi
