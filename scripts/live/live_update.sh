# git pull
cd /srv/live
sudo git pull
# lgsass
/srv/server/scripts/live/live_run.sh python /srv/live/lovegov/bash/sasscompile.py
# collect static
sudo python /srv/live/lovegov/live_manage.py collectstatic --noinput
# reset permissions
sudo chmod -R 770 /static/live
sudo chgrp -R access /static/live
# rewsgi
sudo touch /srv/live/lovegov/apache/live.wsgi
