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
# convenience method to see user activity summary
#-----------------------------------------------------------------------------------------------------------------------
def userSum(name):
    user = getUser(name)
    if user:
        userActivity(user)
    else:
        print "no user with inputted name."

#-----------------------------------------------------------------------------------------------------------------------
# new user
#-----------------------------------------------------------------------------------------------------------------------
def userActivity(user, file=None,  min=None, max=None):

    pa = PageAccess.objects.filter(user=user).exclude(page="/answer/").order_by("when")
    if min:
        pa.filter(when__gt=min)
    if max:
        pa.filter(when__lt=max)

    when = datetime.datetime.min
    to_return = "\n\nUser Summary for " + user.get_name() + ": \n"

    for x in pa:

        delta = x.when - when
        when = x.when

        if delta.total_seconds() > (60*60):
            to_return += "\n---------------------------------  " + str(when) + "\n"  # if new session page break
        else:
            to_return += " (" + str(delta.total_seconds()) + ")\n"               # else print time delta from last page

        to_return += x.page
        if x.action:
            to_return += ":" + x.action


    if file:
        with open(file, 'a') as f:
            try:
                f.write(to_return)
            except UnicodeEncodeError:
                print "unicode encode error for " + user.get_name()

    print to_return
    return to_return

def allUserActivity(file, min=None, max=None):
    u = UserProfile.objects.filter(ghost=False)
    for x in u:
        userActivity(x, file, min, max)

#-----------------------------------------------------------------------------------------------------------------------
# Creates a printout summarizing all user activity for the day.
#-----------------------------------------------------------------------------------------------------------------------
def dailyActivity(request, days=1):
    users = UserProfile.objects.filter(ghost=False)
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