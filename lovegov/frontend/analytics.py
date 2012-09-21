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
# METRICS
#-----------------------------------------------------------------------------------------------------------------------

# takes in a time start, time end, a list of strings of hardcoded demographics. Returns html showing metrics for input.
def getMetricsHTMLFromTimeAndDemographics(time_start, time_end, demographics=[]):

    user_groups = getUserGroupsFromDemographics(time_start, time_end, demographics)

    which_metrics = [
        {'metric_label':'page views', 'which':'page_views'},
        {'metric_label':'time on site', 'which':'session_length'},
        {'metric_label':'answers', 'which':'num_answers'},
        {'metric_label':'upvotes', 'which':'activity', 'type':'upvotes'},
        {'metric_label':'downvotes', 'which':'activity', 'type':'downvotes'},
        {'metric_label':'comments', 'which':'num_posts', 'type':'C'},
        {'metric_label':'posts', 'which':'num_posts', },
        {'metric_label':'news', 'which':'num_posts', 'type':'N'},
        {'metric_label':'questions', 'which':'num_posts', 'type':'Q'},
        {'metric_label':'discussions', 'which':'num_posts', 'type':'D'},
        {'metric_label':'polls', 'which':'num_posts', 'type':'B'},
        {'metric_label':'petitions', 'which':'num_posts', 'type':'P'},
        {'metric_label':'users followed', 'which':'activity', 'type':'users_followed'},
        {'metric_label':'politicians supported', 'which':'activity', 'type':'politicians_supported'},
        {'metric_label':'groups joined', 'which':'activity', 'type':'groups_joined'},
        {'metric_label':'groups followed', 'which':'activity', 'type':'groups_followed'},
        {'metric_label':'signatures', 'which':'activity', 'type':'signatures'},
        {'metric_label':'% anon answers', 'which':'anon_percent', 'type':'answers'},
        {'metric_label':'% anon posts', 'which':'anon_percent', 'type':'posts'},
        {'metric_label':'% anon comments', 'which':'anon_percent', 'type':'comments'},
    ]

    metric_pages = ['/home/', '/questions/', '/groups/', '/elections/', '/legislation/', '/about/', '/blog/']
    for page in metric_pages:
        args_dict = {'metric_label':page, 'which':'page_views', 'page':page}
        which_metrics.append(args_dict)

    html = getMultipleMetricsHTML(which_metrics, user_groups)
    return html

# returns a list of user group dictionaries, based on inputted times, and hardcoded demographic option strings
# user_groups is a list where each element is a dictionary of form
# 'users': queryset of users
# 'time_start': time_start
# 'time_end': time_end
# 'description': string description of what this is
def getUserGroupsFromDemographics(time_start, time_end, demographics):
    user_groups = []

    count = 0

    all_users = UserProfile.objects.filter(ghost=False)
    all_users_dict = {'time_start':time_start,
                      'time_end':time_end,
                      'users':  all_users,
                      'description': 'all real users',
                      'which_color': USER_GROUP_COLORS[count]}
    user_groups.append(all_users_dict)

    if 'new_users' in demographics:
        count += 1
        new_users = UserProfile.objects.filter(ghost=False, created_when__gt=time_start)
        new_users_dict = {'time_start':time_start,
                          'time_end':time_end,
                          'users': new_users,
                          'description': 'new users',
                          'which_color': USER_GROUP_COLORS[count]}
        user_groups.append(new_users_dict)

    return user_groups

# returns html for a list of chosen metrics for a list of user groups
def getMultipleMetricsHTML(which_metrics, user_groups):
    vals = {'user_groups':user_groups}
    vals['USER_GROUP_COLORS'] = USER_GROUP_COLORS
    html = renderHelper("analytics/metrics/metrics_header.html", vals)
    for args_dict in which_metrics:
        vals['results'] = metricsResults(args_dict, user_groups)
        vals['metric_label'] = args_dict['metric_label']
        html += renderHelper("analytics/metrics/metric_simple.html", vals)
    return html

## returns a list of results, in the order of the inputted user_groups
def metricsResults(args_dict, user_groups):
    results = []
    count = 0
    for x in user_groups:
        time_start = x.get('time_start')
        time_end = x.get('time_end')
        users = x.get('users')
        result, normalized = metricsResult(args_dict, time_start, time_end, users)
        results.append({'result':result, 'normalized':normalized, 'which_color':USER_GROUP_COLORS[count]})
        count += 1
    return results

# returns a particular result for a particular metric (indicated by args_dict), for a group of users during some time
def metricsResult(args_dict, time_start=None, time_end=None, users=None):

    which = args_dict['which']
    result = "X"
    normalized = ""

    if not users:
        num_users = float(UserProfile.objects.all().count())
    else:
        num_users = float(users.count())

    if which == 'num_posts':
        posts = metricsGetPostsHelper(time_start, time_end, users)
        c_type = args_dict.get("type")
        if c_type:
            posts = posts.filter(type=c_type)
        result = posts.count()
        if num_users:
            normalized = result / num_users

    elif which == 'num_answers':
        responses = metricsGetResponsesHelper(time_start, time_end, users)
        result = responses.count()
        if num_users:
            normalized = result / num_users

    elif which == 'activity':
        type = args_dict.get('type')
        if type == 'upvotes':
            activity =  VotedAction.objects.filter(value=1)
        elif type == 'downvotes':
            activity =  VotedAction.objects.filter(value=-1)
        elif type == 'users_followed':
            activity =  UserFollowAction.objects.all()
        elif type == 'politicians_supported':
            activity =  SupportedAction.objects.all()
        elif type == 'groups_joined':
            activity =  GroupJoinedAction.objects.all()
        elif type == 'groups_followed':
            activity = GroupFollowAction.objects.all()
        elif type == 'signatures':
            activity = SignedAction.objects.all()
        if time_start:
            activity = activity.filter(when__gt=time_start)
        if time_end:
            activity = activity.filter(when__lt=time_end)
        if users:
            activity = activity.filter(creator__in=users)
        result = activity.count()
        if num_users:
            normalized = result / num_users

    elif which == 'anon_percent':
        type = args_dict.get('type')
        if type == 'answers':
            stuff = metricsGetResponsesHelper(time_start, time_end, users)
        elif type == 'posts':
            stuff = metricsGetPostsHelper(time_start, time_end, users)
        elif type == 'comments':
            stuff = metricsGetPostsHelper(time_start, time_end, users).filter(type="C")
        num_stuff = stuff.count()
        num_anon = stuff.filter(privacy="PRI").count()
        if num_anon:
            result = num_stuff / float(num_anon) * 100
        else:
            result = 0
        result = str(result) + "%"
        normalized = result

    elif which == 'page_views':

        pa = PageAccess.objects.all()
        if time_start:
            pa = pa.filter(when__gt=time_start)
        if time_end:
            pa = pa.filter(when__lt=time_end)
        if users:
            pa = pa.filter(user=users)

        page = args_dict.get('page')
        if page:
            pa = pa.filter(page=page)

        result = pa.count()
        if num_users:
            normalized = result / num_users

    elif which == 'session_length':
        if not users:
            users = UserProfile.objects.filter(ghost=False)
        total_time = datetime.timedelta(seconds=0)
        total_logged_on = 0
        for u in users:
            time_on_site, logged_on = u.getTimeOnSite(time_start, time_end)
            if logged_on:
                total_time += time_on_site
                total_logged_on += 1
        result = int(total_time.total_seconds())
        normalized = total_time.total_seconds() / float(total_logged_on)

    normalized = str(normalized)
    normalized = normalized[:5]

    return result, normalized


def metricsGetResponsesHelper(time_start, time_end, users):
    lg = getLoveGovUser()
    responses = Response.objects.exclude(creator=lg)
    if time_start:
        responses = responses.filter(edited_when__gt=time_start)
    if time_end:
        responses = responses.filter(edited_when__lt=time_end)
    if users:
        responses = responses.filter(creator__in=users)
    return responses

def metricsGetPostsHelper(time_start, time_end, users):
    posts = Content.objects.filter(type__in=IN_FEED)
    if time_start:
        posts = posts.filter(created_when__gt=time_start)
    if time_end:
        posts = posts.filter(created_when__lt=time_end)
    if users:
        posts = posts.filter(creator__in=users)
    return posts

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

    # metrics
    demographics = ['new_users']
    vals['metrics_html'] = getMetricsHTMLFromTimeAndDemographics(time_start, time_end, demographics)

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