# absolute path to the directory of this script
LG="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LG=$(dirname $0)
echo "lg: $LG"

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
alias mastermerge="$LG/local_merge.sh"

# functionality
alias lgscript='python $LG/lovegov/scripts/scheduled.py'
alias lgcleardb='rm $LG/lovegov/db/local.db'
alias lgresyncdb='python $LG/lovegov/local_manage.py syncdb'
alias lgresetdb='$LG/local_reset.sh'
alias lgresetfixture='$LG/local_reset_testfixture.sh'
alias lgserver="$LG/local_server.sh"
alias lgsass="sass --watch $LG/lovegov/frontend/static/css/scss:$LG/lovegov/frontend/static/css/compiled"
alias lgshell="python $LG/lovegov/local_manage.py shell" 
alias lgindex="python $LG/lovegov/local_manage.py rebuild_index"
alias lgcharm="lgdir && charm ."
alias lgpython="bpython -i $LG/autopython.py"
alias remotedb="mysql --host=lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com --user=root --password=lglglg12 --database=lgdb -A"
alias remoteserver="$LG/remote_server.sh"
alias lgrun="source $LG/local_env.sh &&"
alias remoterun="source $LG/remote_env.sh &&"
alias remotepython="source $LG/remote_env.sh && bpython -i $LG/autopython.py"

# server
alias lg1max="ssh -i ~/lovegov/ec2/lg1.pem max@ec2-23-23-91-235.compute-1.amazonaws.com"
alias lg1jvkoh="ssh jvkoh@ec2-23-23-91-235.compute-1.amazonaws.com"
alias lg1jsftp="sftp jvkoh@ec2-23-23-91-235.compute-1.amazonaws.com"

# permission
alias projectpermission="sudo chmod -R 770 $LG"
alias jpermission="sudo chown jvkoh -R $LG && sudo chmod -R 770 $LG"
alias mpermission="sudo chown -R maxfowler $LG && sudo chmod -R 770 $LG"
alias jserver="jpermission && lgserver"
alias jsass="jpermission && lgsass"
alias lgcharm="lgdir && charm ."


# python environment
export PYTHONSTARTUP=$LG/autopython.py
export PYTHONPATH=${PYTHONPATH}:$LG/lovegov
export PYTHONPATH=${PYTHONPATH}:$LG
export DJANGO_SETTINGS_MODULE=lovegov.local_settings


