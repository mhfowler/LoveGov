#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendProfessorInviteEmail, sendStudentGroupInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendStudentGroupInviteEmail('frontend/excel/StudentContacts.xls', 0)
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


