#!/usr/bin/env python

if __name__ == "__main__":
    from initialize import initializeLegislationAmendments
    from pprint import pprint

    print "================= initializeLegislationAmendments() ==================="
    print '======================================================================='
    errors = initializeLegislationAmendments()
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)

