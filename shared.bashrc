# FILE FOR SHARED BASH SETTINGS AND ALIASES

PRE="/srv/server"
DEV="/srv/dev"
LIVE="/srv/live"

# misc
alias cmdcreate="sudo vi $PRE/shared.bashrc"
alias cmdhelp="cat $PRE/cmdhelp"
alias autopermission="sudo $PRE/scripts/permission.sh"
alias allpermission="sudo chmod 770 -R"
alias setaccess="sudo chgrp -R access"
alias serverdir="cd $PRE"


# apache
alias apacheconfig="cd $PRE/apache"
alias apacherestart="sudo /etc/init.d/apache2 restart"
alias apachereload="sudo /etc/init.d/apache2 reload"
alias apachelog="sudo vi /var/log/apache2/error.log"
alias motd="sudo vi /etc/motd.tail"

# memcached
alias memcachedstart="sudo /etc/init.d/memcached start"
alias memcachedstop="sudo /etc/init.d/memcached stop"

# dev
alias devdir="cd /srv/dev"
alias devpython="sudo $PRE/scripts/dev/dev_run.sh python -i /srv/dev/autopython.py"
alias devbetascript="sudo $PRE/scripts/dev/dev_run.sh python /srv/dev/lovegov/beta/modernpolitics/scripts.py"
alias devalphascript="sudo $PRE/scripts/dev/dev_run.sh python /srv/dev/lovegov/alpha/splash/splashscript.py"
alias devrun="sudo $PRE/scripts/dev/dev_run.sh"
alias devbackup="sudo $PRE/scripts/dev/dev_backup.sh"
alias devreset="sudo $PRE/scripts/dev/dev_reset.sh"

# live
alias livedir="cd /srv/live"
alias livepython="sudo $PRE/scripts/live/live_run.sh python -i /srv/live/autopython.py"
alias livebetascript="sudo $PRE/scripts/live/live_run.sh python /srv/live/lovegov/beta/modernpolitics/scripts.py"
alias livealphascript="sudo $PRE/scripts/live/live_run.sh python /srv/live/lovegov/alpha/splash/splashscript.py"
alias liverun="sudo $PRE/scripts/live/live_run.sh"
alias livebackup="sudo $PRE/scripts/live/live_backup.sh"

# git
alias devupdate="cd $DEV && git pull origin dev && cd -"
alias liveupdate="cd $LIVE && git pull && cd -"
alias serverupdate="cd $PRE && git pull origin server && cd -"

