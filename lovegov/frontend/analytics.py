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
def userSummary(user, request, days=None):
    if days:
        today = datetime.datetime.now() - datetime.timedelta(days=int(days))
        pa = PageAccess.objects.filter(user=user, when__gt=today).order_by("when")
    else:
        pa = PageAccess.objects.filter(user=user)
    if pa:
        access = {}
        for x in pa:
            page = x.page
            if page in access:
                access[page] += 1
            else:
                access[page] = 1
        vals = {'access':access, 'pa':pa, 'u':user}
        return ajaxRender('analytics/user_summary.html', vals, request)
    else:
        return ""


#-----------------------------------------------------------------------------------------------------------------------
# new user
#-----------------------------------------------------------------------------------------------------------------------
def userActivity(user):

    pa = PageAccess.objects.filter(user=user).order_by("when")

    when = datetime.MINYEAR
    to_return = "User Summary for " + user.get_name() + ": \n"

    for x in pa:
        delta = x.when - when
        if delta.hours > 0:
            to_return += "---------------------------------  " + when + "\n"
            to_return +=

    return "ok"

#-----------------------------------------------------------------------------------------------------------------------
# Creates a printout summarizing all user activity for the day.
#-----------------------------------------------------------------------------------------------------------------------
def dailyActivity(request, days=1):
    users = UserProfile.objects.filter(user_type="U")
    activity = ""
    for u in users:
        activity += userSummary(u, request, days=days)
    vals = {'activity':activity, 'days':days}
    return renderToResponseCSRF('analytics/daily_activity.html', vals, request)

def totalActivity(request, alias=None):
    if alias:
        user = UserProfile.objects.get(alias=alias)
        vals = {'activity':activity}
        return renderToResponseCSRF('analytics/total_activity.html', vals, request)
    else:
        return dailyActivity(request, days=None)