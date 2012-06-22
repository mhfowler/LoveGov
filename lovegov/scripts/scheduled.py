########################################################################################################################
########################################################################################################################
#
#           Scheduled scripts
#
#
########################################################################################################################
########################################################################################################################

# python
import sys
import getpass
import datetime

# lovegov
from lovegov.modernpolitics.backend import *

#-----------------------------------------------------------------------------------------------------------------------
# Switch method which calls correct script.
#-----------------------------------------------------------------------------------------------------------------------
def runScript(operation, tag, args=[]):
    tags = ['update', 'print', 'initialize']
    if operation == 'update':
        scriptUpdate(tag, args)
    elif operation == 'print':
        scriptPrint(tag, args)
    elif operation == 'initialize':
        scriptInitialize(tag, args)
    # prints valid scripts
    elif operation == 'help':
        to_print = 'acceptable operations: help, '
        for t in tags:
            to_print += t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted operation."

#-----------------------------------------------------------------------------------------------------------------------
# Update script.
#-----------------------------------------------------------------------------------------------------------------------
def scriptUpdate(tag, args=[]):
    tags = ['rank', 'allcomparisons', 'usercomparisons', 'groupviews',
            'calcviews', 'contentlinks', 'userfeeds', 'groupfeeds',
            'lovegovfeeds', 'groupbyname', 'lovegovresponses',
            'alpha', 'sitefeeds', 'topicfeeds', 'betafeeds', 'congress']
    if tag == 'all':
        for t in tags:
            scriptUpdate(t)
    if tag == 'sitefeeds':
        print "*** UPDATING SITE FEEDS ***"
        scheduled_logger.debug("** updating site feeds **")
        updateSiteFeeds()
    elif tag == 'lovegovresponses':
        print "*** UPDATING LOVEGOV GROUP AND USER RESPONSES ***"
        scheduled_logger.debug("** updating lovegovrespones **")
        updateLoveGovResponses()
    elif tag == 'congress':
        print "*** UPDATING CONGRESS GROUP VIEW ***"
        updateCongressView()
    elif tag == 'groupviews':
        print "*** UPDATING AGGREGATE GROUP VIEWS ***"
        updateGroupViews()
    elif tag == 'calcviews':
        print "*** UPDATING CALCULATED CONTENT VIEWS ***"
        updateCalcViews()
    elif tag == 'groupfeeds':
        print "*** UPDATING GROUP FEEDS ***"
        updateAllGroupFeeds()
    elif tag == 'groupbyname':
        print "*** UPDATING GROUPBYNAME FEED ***"
        name = ""
        length = len(args)
        for index, x in enumerate(args):
            if index < (length-1):
                name += x + " "
            else: name += x
        updateGroupByName(name=name)
    # prints valid tags
    elif tag == 'help':
        print "***** UPDATE HELP *****"
        to_print = 'acceptable tags: help, all, '
        for t in tags:
            to_print = to_print + t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag."

#-----------------------------------------------------------------------------------------------------------------------
# Print script.
#-----------------------------------------------------------------------------------------------------------------------
def scriptPrint(tag, args=[]):
    tags = ['scripts', 'emails']
    if tag == 'all':
        for t in tags:
            scriptPrint(t)
    elif tag == 'scripts':
        print "***** PRINTING SCRIPTS *****"
        for x in Script.objects.all():
            to_print = '"' + x.command + '"' + ' by ' + x.user + ' at ' + str(x.when)
            print to_print
    elif tag == 'emails':
        print "***** PRINTING EMAILS *****"
        for x in EmailList.objects.all():
            print x.email + " at " + str(x.when)
    # prints valid tags
    elif tag == 'help':
        print "***** PRINT HELP *****"
        to_print = 'acceptable tags: help, all, '
        for t in tags:
            to_print = to_print + t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag."

#-----------------------------------------------------------------------------------------------------------------------
# Initialize script.
#-----------------------------------------------------------------------------------------------------------------------
def scriptInitialize(tag, args=[]):
    tags = ['lovegov', 'testdata', 'topics']
    if tag == 'all':
        for t in tags:
            scriptInitialize(t)
    elif tag == 'lovegov':
        print "*** INITIALIZING USER LOVEGOV ***"
        initializeLoveGovUser()             # user of the site who represents the whole site
    elif tag == 'testdata':
        print "*** INITIALIZING TEST DATA ***"
        initializeDB()
    elif tag == 'topics':
        print "*** INITIALIZING TOPICS IN QAWEB ***"
        initializeTopics(using="qaweb")
    elif tag == 'localinit':
        print "*** INITIALIZING TESTDATA LOCALLY ***"
        initializeTopics()
        initializeDB()
    # prints valid tags
    elif tag == 'help':
        print "***** INITIALIZE HELP *****"
        to_print = 'acceptable tags: help, all, '
        for t in tags:
            to_print = to_print + t + ', '
        print to_print
    # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag."

#-----------------------------------------------------------------------------------------------------------------------
# Script for adding stuff to db.
#-----------------------------------------------------------------------------------------------------------------------
def scriptAdd(tag, args=[]):
    tags = ['email']
    if tag == 'email':
        print "*** ADDING EMAIL ***"
        if arg:
            addValidEmail(args[0])
        else: print("no email supplied")
    elif tag == 'help':
        print "***** ADD HELP *****"
        to_print = 'acceptable tags: help, '
        for t in tags:
            to_print = to_print + t + ', '
        print to_print
        # else invalid tag
    else:
        print "invalid command: '" + tag + "' is not an accepted tag."


########################################################################################################################
#   Start of actual script.
#
########################################################################################################################
# save the fact that script was run
command = ''
for x in sys.argv:
    command += x + ' '
to_save = Script(command=command, user=getpass.getuser())
to_save.save()
time = datetime.now()

# check at least one tag
if len(sys.argv) < 3:
    print "invalid command: need at least one script and one tag."
else:
    print '\n"' + command + '" ' + " at " + str(time)
    operation = sys.argv[1]
    tag = sys.argv[2]
    if len(sys.argv) > 3:
        args = sys.argv[3:]
    else:
        args=[]
    # runscript
    runScript(operation, tag, args)
