########################################################################################################################
########################################################################################################################
#
#           Analytics
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.backend import *

ANALYTICS_EMAILS = ['max_fowler@brown.edu']

#-----------------------------------------------------------------------------------------------------------------------
# Creates a summary of a users daily use.
#-----------------------------------------------------------------------------------------------------------------------
def userSummary(user, request):
    today = datetime.datetime.now() - datetime.timedelta(days=1)
    pa = PageAccess.objects.filter(user=user, when__gt=today).order_by("when")
    if pa:
        access = {}
        for x in pa:
            page = x.page
            if page in access:
                access[page] += 1
            else:
                access[page] = 0
        vals = {'access':access, 'pa':pa, 'u':user}
        return ajaxRender('analytics/user_summary.html', vals, request)
    else:
        return ""

#-----------------------------------------------------------------------------------------------------------------------
# Creates a printout summarizing all user activity for the day.
#-----------------------------------------------------------------------------------------------------------------------
def dailyActivity(request):
    users = UserProfile.objects.filter(user_type="U")
    activity = ""
    for u in users:
        activity += userSummary(u, request)
    vals = {'activity':activity}
    return renderToResponseCSRF('analytics/daily_activity.html', vals, request)