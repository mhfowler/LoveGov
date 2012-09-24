#!/usr/bin/env python

if __name__ == "__main__":
    from scripts.alpha import sendGroupGeneralInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendGroupGeneralInviteEmail()
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


