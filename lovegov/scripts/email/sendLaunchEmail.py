#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendProfessorInviteEmail, sendStudentGroupInviteEmail, sendGroupGeneralInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendGroupGeneralInviteEmail('frontend/excel/StudentContacts.xls', 1)
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


