#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendSpecialEmails
    import datetime

    print str(datetime.datetime.now())
    print "================= sendSpecialEmails() ==================="
    print '============================================================='
    sendSpecialEmails()


