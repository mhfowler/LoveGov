#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendWeeklyDigestEmails
    import datetime

    print str(datetime.datetime.now())
    print "================= sendWeeklyDigestEmails() ==================="
    print '============================================================='
    sendWeeklyDigestEmails()


