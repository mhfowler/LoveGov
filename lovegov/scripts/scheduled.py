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
    tags = ['groupviews', 'lovegovresponses','congress','hot_scores', 'like_minded_groups']
    if tag == 'all':
        for t in tags:
            scriptUpdate(t)
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
        print "*** UPDATING GROUP HOT SCORES ***"
        updateGroupHotScores()
    elif tag == 'hot_scores':
        print "*** UPDATING HOT SCORES ***"
        updateHotScores()
    elif tag == 'like_minded_groups':
        print "*** UPDATING LIKE MINDED GROUPS ***"
        updateLikeMindedGroups()
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
    print "why!"

#-----------------------------------------------------------------------------------------------------------------------
# Initialize script.
#-----------------------------------------------------------------------------------------------------------------------
def scriptInitialize(tag, args=[]):
    initializeDB()

#-----------------------------------------------------------------------------------------------------------------------
# Script for adding stuff to db.
#-----------------------------------------------------------------------------------------------------------------------
def scriptAdd(tag, args=[]):
    print "add!"

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
