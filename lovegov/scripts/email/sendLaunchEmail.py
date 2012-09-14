#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendLaunchEmailBatch

    print "================= sendLaunchEmails() ==================="
    print '============================================================='
    total_sent = sendLaunchEmailBatch()
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


