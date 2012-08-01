#!/usr/bin/env python

if __name__ == "__main__":
    from initialize import initializeVotingRecord
    from pprint import pprint

    print "================= initializeVotingRecord() ==================="
    print '=============================================================='
    errors = initializeVotingRecord()
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)
