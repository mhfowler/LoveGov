#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.initialize import manuallyUpdate
    print "manually updating..."
    xls_path = 'scripts/migration/ct.xls'
    manuallyUpdate("CT", xls_path)