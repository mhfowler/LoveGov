#!/usr/bin/env python

__author__ = 'jvkoh'


if __name__ == "__main__":
    from initialize import initializeLegislation
    from pprint import pprint


    print "================= initializeLegislation() ==================="
    print '============================================================='
    errors = initializeLegislation()
    print "=================== Logged Errors ======================"
    print '========================================================'
    pprint(errors)


