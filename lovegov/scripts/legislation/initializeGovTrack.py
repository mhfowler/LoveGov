#!/usr/bin/env python

if __name__ == "__main__":
    ## Initialize Congress ##
    from lovegov.modernpolitics.initialize import initializeCongress
    from lovegov.modernpolitics.initialize import initializeCommittees

    print "================= initializeCongress() ==================="
    print '=========================================================='
    initializeCongress()
    print "================= initializeCommittees() ==================="
    print '=========================================================='
    initializeCommittees()

    ## Initialize Legislation ##
    from lovegov.modernpolitics.initialize import initializeLegislation
    from pprint import pprint

    print "================= initializeLegislation() ==================="
    print '============================================================='
    legislation_errors = initializeLegislation()
    print "=================== Logged Legislation Errors ======================"
    print '===================================================================='
    pprint(legislation_errors)

    ## Initialize Amendments ##
    from lovegov.modernpolitics.initialize import initializeLegislationAmendments
    from pprint import pprint

    print "================= initializeLegislationAmendments() ==================="
    print '======================================================================='
    amendment_errors = initializeLegislationAmendments()
    print "=================== Logged Amendment Errors ======================"
    print '=================================================================='
    pprint(amendment_errors)

    ## Initialize Voting Records ##
    from lovegov.modernpolitics.initialize import initializeVotingRecord
    from pprint import pprint

    print "================= initializeVotingRecord() ==================="
    print '=============================================================='
    voting_errors = initializeVotingRecord()
    print "=================== Logged Voting Errors ======================"
    print '==============================================================='
    pprint(voting_errors)

