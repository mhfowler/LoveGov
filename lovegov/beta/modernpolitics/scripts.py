########################################################################################################################
########################################################################################################################
########################################################################################################################
#
#           Scripts to be run from terminal which modify db.
#     must "export DJANGO_SETTINGS_MODULE=lovegov.settings" before running!
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

import sys
import getpass
import datetime
from lovegov.beta.modernpolitics import backend
from lovegov.beta.modernpolitics.models import Script
from lovegov.beta.modernpolitics.models import EmailList

import logging
scheduled_logger = logging.getLogger('scheduledlogger')

########################################################################################################################
########################################################################################################################
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
            'lovegovfeeds', 'groupbyname', 'debug', 'lovegovresponses',
            'questiondiscussed', 'alpha', 'sitefeeds', 'topicfeeds', 'betafeeds', 'congress']
    if tag == 'all':
        for t in tags:
            scriptUpdate(t)
    elif tag == 'rank':
        print "*** UPDATING CONTENT RANK ***"
        backend.updateRank()
    elif tag == 'allcomparisons':
        print "*** UPDATING VIEW COMPARISONS ***"
        backend.updateViewComparisons()
    elif tag == 'usercomparisons':
        print "*** UPDATING VIEW COMPARISONS ***"
        backend.updateUserComparisons()
    elif tag == 'groupviews':
        print "*** UPDATING AGGREGATE GROUP VIEWS ***"
        backend.updateGroupViews()
    elif tag == 'calcviews':
        print "*** UPDATING CALCULATED CONTENT VIEWS ***"
        backend.updateCalcViews()
    elif tag == 'contentlinks':
        print "*** UPDATING CONTENT LINKS ***"
        backend.updateAllContentLinks(debug=True)
    elif tag == 'userfeeds':
        print "*** UPDATING USER FEEDS ***"
        backend.updateUserFeeds()
    elif tag == 'groupfeeds':
        print "*** UPDATING GROUP FEEDS ***"
        backend.updateAllGroupFeeds()
    elif tag == 'lovegovfeeds':
        print "*** UPDATING LOVEGOV FEEDS ***"
        backend.updateLoveGovFeeds()
    elif tag == 'questiondiscussed':
        print "*** UPDATING QUESTION DISCUSSED RANKINGS  ***"
        scheduled_logger.debug("** updating questiondiscussed **")
        backend.updateQuestionDiscussed()
    elif tag == 'alpha':
        print "*** ALPHA UPDATE ***"
        scheduled_logger.debug("** alpha update **")
        backend.updateLoveGovResponses()
        backend.updateQuestionDiscussed()
    elif tag == 'topicfeeds':
        print "*** UPDATING TOPIC FEEDS ***"
        scheduled_logger.debug("** updating site feeds **")
        backend.updateTopicFeeds()
    elif tag == 'betafeeds':
        scriptUpdate(tag="sitefeeds")
        scriptUpdate(tag="topicfeeds")
    elif tag == 'groupbyname':
        print "*** UPDATING GROUPBYNAME FEED ***"
        name = ""
        length = len(args)
        for index, x in enumerate(args):
            if index < (length-1):
                name += x + " "
            else: name += x
        backend.updateGroupByName(name=name)
    ###################### ACTUALLY USED ON SCHEDULE ON LIVE SITE ######################
    elif tag == 'sitefeeds':
        print "*** UPDATING SITE FEEDS ***"
        scheduled_logger.debug("** updating site feeds **")
        backend.updateSiteFeeds()
    elif tag == 'lovegovresponses':
        print "*** UPDATING LOVEGOV GROUP AND USER RESPONSES ***"
        scheduled_logger.debug("** updating lovegovrespones **")
        backend.updateLoveGovResponses()
    elif tag == 'congress':
        print "*** UPDATING CONGRESS GROUP VIEW ***"
        backend.updateCongressView()
    ####################################################################################
    elif tag == 'debug':
        print "*** UPDATE ALL DEBUG ***"
        backend.update()
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
        backend.initializeLoveGovUser()          # user of the site who represents the whole site
    elif tag == 'testdata':
        print "*** INITIALIZING TEST DATA ***"
        backend.initializeDB()
    elif tag == 'topics':
        print "*** INITIALIZING TOPICS IN QAWEB ***"
        backend.initializeTopics(using="qaweb")
    elif tag == 'localinit':
        print "*** INITIALIZING TESTDATA LOCALLY ***"
        backend.initializeTopics()
        backend.initializeDB()
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
            backend.addValidEmail(args[0])
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
time = datetime.datetime.now()

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
