#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.initialize import initializeLegislation
    from pprint import pprint

    print "================= initializeLegislation() ==================="
    print '============================================================='
    errors = initializeLegislation()
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)


