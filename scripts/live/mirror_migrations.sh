LIVEMIGRATIONS=/srv/live/lovegov/modernpolitics/migrations
DEVMIGRATIONS=/srv/dev/lovegov/modernpolitics/migrations
sudo rm -r $LIVEMIGRATIONS
sudo cp -r $DEVMIGRATIONS $LIVEMIGRATIONS
