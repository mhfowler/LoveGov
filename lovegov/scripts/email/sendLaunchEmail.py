#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendStudentGroupInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendStudentGroupInviteEmail()
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


