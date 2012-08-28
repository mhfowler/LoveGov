read -p "This will overwrite your local database with the remote dev database. Are you sure you want to do this? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
 mysqldump --host=lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com --user=root --password=lglglg12 --complete-insert lgdb | mysql -u root -p localmirror  
fi

