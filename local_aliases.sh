# absolute path to the directory of this script
LG="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# aliases
alias cmdcreate='vi $LG/local_aliases.sh'
alias sshserver='ssh -p 7822 75.98.168.114 -l '
alias applerun='/scripts/applerun.sh'

# git
alias lgdir='cd $LG'
alias lgpull="cd $LG && git pull && cd -"
alias lgcommit="cd $LG && git commit -a && cd -"
alias lgpush="cd $LG && git push && cd -"
alias lgpull="cd $LG && git pull && cd -"

# functionality
alias lgscript='python $LG/lovegov/scripts/scheduled.py'
alias lgcleardb='rm $LG/lovegov/db/local.db'
alias lgresyncdb='python $LG/lovegov/local_manage.py syncdb'
alias lginitdb='python $LG/lovegov/local_manage.py loaddata $LG/lovegov/db/migrate.json && python $LG/lovegov/frontend/scripts.py initialize testdata'
alias lgresetdb='$LG/local_reset.sh'
alias lgserver="$LG/local_server.sh"
alias jserver="jpermission && lgserver"
alias lgsass="sass --watch $LG/lovegov/frontend/static/css/scss:$LG/lovegov/frontend/static/css/compiled"
alias lgshell="python $LG/lovegov/local_manage.py shell" 

# permission
alias projectpermission="sudo chmod -R 770 $LG"
alias jpermission="sudo chown jvkoh -R $LG && sudo chmod -R 770 $LG"
alias mpermission="sudo chown -R maxfowler $LG && sudo chmod -R 770 $LG"

# python environment
export PYTHONSTARTUP=$LG/autopython.py
export PYTHONPATH=${PYTHONPATH}:$LG/lovegov
export PYTHONPATH=${PYTHONPATH}:$LG
export DJANGO_SETTINGS_MODULE=lovegov.local_settings


