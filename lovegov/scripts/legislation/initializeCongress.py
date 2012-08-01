#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.initialize import initializeCongress
    from lovegov.modernpolitics.initialize import initializeCommittees

    print "================= initializeCongress() ==================="
    print '=========================================================='
    initializeCongress()
    print "================= initializeCommittees() ==================="
    print '=========================================================='
    initializeCommittees()


