########################################################################################################################
########################################################################################################################
#
#           Analytics
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.backend import *
from operator import itemgetter

#-----------------------------------------------------------------------------------------------------------------------
# email logging
#-----------------------------------------------------------------------------------------------------------------------
def logEmails(file_path, which):
    print "saving emails sent (" + file_path + ", " + which + ")"
    f = open(file_path, 'r')
    lines = f.readlines()
    for x in lines:
        try:
            email = x.replace("\n", "")
            EmailSent(email=email, which=which).save()
            print "saved " + email
        except:
            print "+WW+ failed " + x

#-----------------------------------------------------------------------------------------------------------------------
# Benchmarking
#-----------------------------------------------------------------------------------------------------------------------

def apacheBenchmark(domain, page, output_folder, num_requests=100, num_concurrent=1):

    url = domain + page

    output_file = page.replace("/", "_") + "." + str(num_concurrent)
    output_path = output_folder + "/" + output_file

    command = "ab -n " + str(num_requests) + " -c " + str(num_concurrent) + " " + url + " > " + output_path
    os.system(command)


def benchmarkPage(page, output_folder):

    domain = "http://lovegov.com"

    num_requests = 1000
    concurrencies = reversed([1, 10, 20, 50, 100, 200])

    url = domain + page
    print "*** RUNNING APACHE BENCHMARK FOR " + url + " ***"

    for num_concurrent in concurrencies:
        print "concurrency " + str(num_concurrent)
        apacheBenchmark(domain, page, output_folder, num_requests, num_concurrent)

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


################################################# LOAD TIMES ###########################################################

def dailyLoadTimes(days_ago=1, days_for=0):

    vals = {}

    now = datetime.datetime.now()
    time_start = now - datetime.timedelta(days=days_ago)
    if not days_for:
        time_end = now
    else:
        time_end = now + datetime.timedelta(days=days_for)
    vals['time_start'] = time_start
    vals['time_end'] = time_end

    ca = ClientAnalytics.objects.filter(when__gt=time_start, when__lt=time_end)

    pages = {}
    for x in ca:
        page = x.page
        already = pages.get(page)
        if not already:
            pages[page] = {'objects':[x], 'num':1, 'page':page}
        else:
            pages_page = pages[page]
            pages_page['objects'].append(x)
            pages_page['num'] += 1

    pages_list = []
    for k,v in pages.items():
        pages_list.append(v)

    pages_list.sort(key=itemgetter('num'), reverse=True)
    vals['load_times'] = pages_list

    for x in pages_list:
        x['mean'], x['max'], x['min'], x['count'] = getLoadTimeStats(x['objects'])

    context = Context(vals)
    template = loader.get_template('emails/daily_summary/load_times.html')
    html = template.render(context)

    return html

def getLoadTimeStats(ca):
    count = 0
    max_load = 0
    total = 0
    min_load = 100000
    for x in ca:
        count += 1
        load_time = x.load_time
        total += load_time
        max_load = max(max_load, load_time)
        min_load = min(min_load, load_time)
    mean = total / count
    return mean, max_load, min_load, count


################################################# USAGE EMAIL ##########################################################

class Session:
    """ for storing an individual users page accesses for a single session """
    def __init__(self):
        self.pa = []
    def getSessionStart(self):
        return self.pa[0].when
    def processPA(self):
        self.pa.sort(key=lambda item: item.when)
        previous = None
        for x in self.pa:
            if previous:
                duration = (x.when - previous.when).total_seconds()
                if duration < (60*60):
                    previous.duration = int(duration)
                else:
                    previous.duration = None
            previous = x

    def getNumPA(self):
        return len(self.pa)
    def getPA(self):
        return self.pa

def dailySummaryEmail(days_ago=1, days_for=0):
    vals = {}

    now = datetime.datetime.now()
    time_start = now - datetime.timedelta(days=days_ago)
    if not days_for:
        time_end = now
    else:
        time_end = now + datetime.timedelta(days=days_for)
    vals['time_start'] = time_start
    vals['time_end'] = time_end

    pa = PageAccess.objects.filter(when__gt=time_start, when__lt=time_end)

    accessed = {}
    anon_access = []
    for x in pa:
        try:
            user = x.user
            if not user.isAnon():
                alias = user.alias
                if not alias in accessed:
                    accessed[alias] = {'user':user, 'session':Session()}
                accessed[alias]['session'].pa.append(x)
            else:
                anon_access.append(x)
        except UserProfile.DoesNotExist:
            print "user does not exist for page access, " + str(x.id)

    accessed_list = []
    for k,v in accessed.items():
        accessed_list.append(v)

    accessed_list.sort(key=lambda item: item['session'].getNumPA())
    for x in accessed_list:
        x['session'].processPA()

    vals['accessed'] = accessed_list

    registered = UserProfile.objects.filter(created_when__gt=time_start).order_by("created_when")
    vals['registered'] = registered

    # load times
    vals['load_times_html'] = dailyLoadTimes(days_ago, days_for)

    # anon access
    anon = dailyAnonymousActivity(anon_access)
    vals['anon_activity'] = anon

    context = Context(vals)
    template = loader.get_template('emails/daily_summary/daily_summary.html')
    email = template.render(context)

    return email


def dailyAnonymousActivity(pa):

    anon_access = {}
    for x in pa:
        ipaddress = x.ipaddress
        if ipaddress not in anon_access:
            anon_access[ipaddress] = {'ipaddress':ipaddress, 'session':Session()}
        anon_access[ipaddress]['session'].pa.append(x)

    anon_list = anon_access.values()
    anon_list.sort(key=lambda item: item['session'].getNumPA())
    for x in anon_list:
        x['session'].processPA()

    return anon_list