# old way
#/srv/server/scripts/live/live_run.sh python /srv/live/lovegov/live_manage.py dumpdata modernpolitics auth django_facebook > $1

# new way
# mysqldump live -u root -ptexers787 --default-character-set=utf8 --compatible=ansi --skip-opt --ignore-table=live.django_content_type > $1

# full backup
mysqldump --host=lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com --user=root --password=lglglg12 --complete-insert lglive > $1

echo "$(date)" 
