# sets correct permissions for whole server
sudo chmod -R 640 /srv
sudo chmod -R 660 /media
sudo chmod -R 660 /log
sudo chmod -R 660 /static
sudo chmod -R 660 /srv/dev/lovegov/modernpolitics/migrations
sudo chmod -R 660 /srv/live/lovegov/modernpolitics/migrations
sudo chmod -R 660 /srv/dev/lovegov/modernpolitics/search_indexes
sudo chmod -R 660 /srv/live/lovegov/modernpolitics/search_indexes
sudo chmod -R 770 /srv/server/scripts
sudo chmod -R 660 /backup
# set everything to be group access
sudo chgrp -R access /srv
sudo chgrp -R access /media
sudo chgrp -R access /log
sudo chgrp -R access /static
sudo chgrp -R access /backup
# set everything to be owned by root
sudo chown -R root /srv
sudo chown -R root /media
sudo chown -R root /log
sudo chown -R root /static
sudo chown -R root /backup

