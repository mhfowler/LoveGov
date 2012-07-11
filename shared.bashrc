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
alias scriptsdir="cd $PRE/scripts"
alias serverupdate="cd $PRE/scripts && git pull && cd -"

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
alias devmirror="sudo $PRE/scripts/dev/dev_mirror.sh"
alias devupdate="sudo $PRE/scripts/dev/dev_update.sh"
alias devsouth="sudo $PRE/scripts/dev/dev_south.sh"

# live
alias livedir="cd /srv/live"
alias livepython="sudo $PRE/scripts/live/live_run.sh python -i /srv/live/autopython.py"
alias livebetascript="sudo $PRE/scripts/live/live_run.sh python /srv/live/lovegov/beta/modernpolitics/scripts.py"
alias livealphascript="sudo $PRE/scripts/live/live_run.sh python /srv/live/lovegov/alpha/splash/splashscript.py"
alias liverun="sudo $PRE/scripts/live/live_run.sh"
alias livebackup="sudo $PRE/scripts/live/live_backup.sh"
alias liveupdate="sudo $PRE/scripts/live/live_update.sh"
alias livesouth="sudo $PRE/scripts/live/live_south.sh"
