# absolute path to the directory of this script
PROJECT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEV=$PROJECT/dev
LIVE=$PROJECT/live

# aliases
alias cmdcreate='vi $PROJECT/local_aliases.sh'
alias sshserver='ssh -p 7822 75.98.168.114 -l '
alias applerun='/scripts/applerun.sh'

# local development
alias projectdir='cd $PROJECT'
alias projectupdate="sudo svn update $PROJECT"
alias projectcommit="$PROJECT/autocommit.sh "
alias svnignore="sudo svn propset svn:ignore"
alias svnrm="sudo svn rm --keep-local" 

# dev
alias devdir="cd $DEV"
alias devcommit="$PROJECT/autocommit.sh dev"
alias devupdate="sudo svn update $DEV"
alias devbetascript='python $DEV/lovegov/beta/modernpolitics/scripts.py'
alias devcleardb='rm $DEV/lovegov/db/local.db'
alias devresyncdb='python $DEV/lovegov/local_manage.py syncdb'
alias devinitdb='python $DEV/lovegov/local_manage.py loaddata $DEV/lovegov/db/migrate.json && python $DEV/lovegov/beta/modernpolitics/scripts.py initialize testdata'
alias devresetdb='$DEV/local_reset.sh'
alias devserver="$DEV/local_server.sh"
alias devsync="sudo svn merge -r0:HEAD $LIVE $DEV"
alias devchop="svn rm $DEV && sudo rm -r $DEV"
alias devbranch="svn copy $LIVE $DEV"

#live
alias livedir="cd $LIVE"
alias livecommit="$PROJECT/autocommit.sh live"
alias liveupdate="sudo svn update $LIVE"
alias livebetascript='python $LIVE/lovegov/beta/modernpolitics/scripts.py'
alias livecleardb='rm $LIVE/lovegov/db/localdb'
alias liveresyncdb='python $LIVE/lovegov/local_manage.py syncdb'
alias liveinitdb='python $LIVE/lovegov/local_manage.py loaddata ~/Desktop/cs/lovegov/backup/migrate.json && python ~/Desktop/cs/lovegov/lovegov/beta/modernpolitics/scripts.py initialize testdata'
alias liveresetdb='$LIVE/local_reset.sh'
alias liveserver="$LIVE/local_server.sh"
alias livereintegrate="sudo svn -r0:HEAD merge $DEV $LIVE"

# permission
alias projectpermission="sudo chmod -R 770 $PROJECT"
alias jpermission="sudo chown jvkoh -R $PROJECT && sudo chmod -R 770 $PROJECT"

# python environment
export PYTHONSTARTUP=$DEV/autopython.py
export PYTHONPATH=${PYTHONPATH}:$DEV/lovegov
export PYTHONPATH=${PYTHONPATH}:$DEV
export DJANGO_SETTINGS_MODULE=lovegov.local_settings


