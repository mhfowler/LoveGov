#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.initialize import initializeVotingRecord
    from pprint import pprint

    print "================= initializeVotingRecord() ==================="
    print '=============================================================='
    errors = initializeVotingRecord()
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)
