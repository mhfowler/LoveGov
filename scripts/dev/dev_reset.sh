PRE="/srv/server"
DEV="/srv/dev"

# reset db
echo "cleardb?"
read \n
mysql --password=texers787 < $PRE/scripts/mysql/dev_reset.sql 

# resync db
echo "syncdb?"
read \n
$PRE/scripts/dev/dev_run.sh python $DEV/lovegov/dev_manage.py syncdb

#load question data from dump
echo "loaddata?"
read \n
$PRE/scripts/dev/dev_run.sh python $DEV/lovegov/dev_manage.py loaddata $DEV/lovegov/db/migrate.json

# initialize testdata and admins
echo "initdata?"
read \n
$PRE/scripts/dev/dev_run.sh python $DEV/lovegov/beta/modernpolitics/scripts.py initialize testdata

# rebuild search index
$PRE/scripts/dev/dev_searchindex.sh

