mysqldump live -u root -p --complete-insert --no-create-info --ignore-table=live.django_site --ignore-table=live.auth_permission --ignore-table=live.django_content_type > $1
