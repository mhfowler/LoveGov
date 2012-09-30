#!/usr/bin/env python

if __name__ == "__main__":
    from scripts.alpha import scriptCreateResponses
    from pprint import pprint

    print "================= scriptCreateResponses() ==================="
    print '======================================================================='
    file = 'necandidates/HouseCandidateAnswers_MA.xls'
    print file
    errors = scriptCreateResponses(file)
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)

