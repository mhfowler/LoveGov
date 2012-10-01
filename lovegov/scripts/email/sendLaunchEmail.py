#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendGroupGeneralInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendGroupGeneralInviteEmail('frontend/excel/AcademiaBundle_MA.xls', 1)
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


