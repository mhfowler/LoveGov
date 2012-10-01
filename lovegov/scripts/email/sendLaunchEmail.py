#!/usr/bin/env python

if __name__ == "__main__":
    from lovegov.modernpolitics.send_email import sendProfessorInviteEmail

    print "================= sendStudentGroupInviteEmail() ==================="
    print '============================================================='
    total_sent = sendProfessorInviteEmail('frontend/excel/AcademiaBundle_MA.xls', 2)
    print "=================== Total Sent ======================"
    print("#: " + str(total_sent))


