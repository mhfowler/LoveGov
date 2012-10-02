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
import xlwt
import xlutils

#-----------------------------------------------------------------------------------------------------------------------
# METRICS
#-----------------------------------------------------------------------------------------------------------------------

### output metrics to excel doc ###
def metricsToExcel(filepath):

    from xlutils import copy

    metrics_template_filepath = os.path.join(PROJECT_PATH, 'logging/metrics/metrics_template.xls')

    rb = open_workbook(metrics_template_filepath,formatting_info=True)
    wb = xlutils.copy.copy(rb) #a writable copy (I can't read values out of this, only write to it)

    start_epoch = datetime.datetime(month=8, year=2012, day=28, hour=4)
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    spread = 20                    # num columns between average and total

    which_metrics = [
            {'metric_label':'page views', 'which':'page_views'},
            {'metric_label':'time on site', 'which':'session_length'},
            {'metric_label':'answers', 'which':'new_answers'},
            {'metric_label':'posts', 'which':'num_posts', },
            {'metric_label':'comments', 'which':'num_posts', 'type':'C'},
            {'metric_label':'signatures', 'which':'activity', 'type':'signatures'},
            {'metric_label':'upvotes', 'which':'activity', 'type':'upvotes'},
            {'metric_label':'downvotes', 'which':'activity', 'type':'downvotes'},
            {'metric_label':'groups joined', 'which':'activity', 'type':'groups_joined'},
            {'metric_label':'groups followed', 'which':'activity', 'type':'groups_followed'},
            {'metric_label':'users followed', 'which':'activity', 'type':'users_followed'},
            {'metric_label':'politicians supported', 'which':'activity', 'type':'politicians_supported'},
            {'metric_label':'news', 'which':'num_posts', 'type':'N'},
            {'metric_label':'questions', 'which':'num_posts', 'type':'Q'},
            {'metric_label':'discussions', 'which':'num_posts', 'type':'D'},
            {'metric_label':'petitions', 'which':'num_posts', 'type':'P'},
            {'metric_label':'polls', 'which':'num_posts', 'type':'B'},
            #{'metric_label':'% anon answers', 'which':'anon_percent', 'type':'answers'},
            #{'metric_label':'% anon posts', 'which':'anon_percent', 'type':'posts'},
            #{'metric_label':'% anon comments', 'which':'anon_percent', 'type':'comments'},
    ]

    demographics = ['logged_on', 'new_users', 'returning_users']
    for i, demograph in enumerate(demographics):

        print "DEMOGRAPH: " + demograph

        w_sheet = wb.get_sheet(i)
        c_date = start_epoch
        row = 1
        total_to_date = 0
        while c_date < now:
            time_start = c_date
            time_end = time_start + delta
            user_group = getUserGroupsFromDemographics(time_start, time_end, [demograph])[0]

            dt = time_start.strftime('%m/%d/%y')
            w_sheet.write(row,2,dt)

            w_sheet.write(row,3,total_to_date)

            users = user_group['users']
            num_users_today = len(users)
            w_sheet.write(row,4,num_users_today)
            print "NUM USERS: " + str(num_users_today)

            column = 7
            for args_dict in which_metrics:
                total, normalized = metricsResult(args_dict, time_start, time_end, users)
                w_sheet.write(row, column, normalized)
                w_sheet.write(row, column+spread, total)
                print args_dict['metric_label'] + " " + str(total)
                column += 1

            total_to_date += num_users_today
            row += 1
            c_date = time_end

            print c_date

    wb.save(filepath)




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

#    metric_pages = ['/home/', '/questions/', '/groups/', '/elections/', '/legislation/', '/about/', '/blog/']
#    for page in metric_pages:
#        args_dict = {'metric_label':page, 'which':'page_views', 'page':page}
#        which_metrics.append(args_dict)

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

    anon = getAnonUser()

    count = 0

    if 'all_users' in demographics:
        all_users = UserProfile.objects.filter(ghost=False).exclude(id=anon.id)
        all_users_dict = {'time_start':time_start,
                          'time_end':time_end,
                          'users':  all_users,
                          'description': 'all real users',
                          'which_color': USER_GROUP_COLORS[count]}
        user_groups.append(all_users_dict)
        count += 1

    if 'logged_on' in demographics:
        logged_on_users = getLoggedOnUsers(time_start, time_end).exclude(id=anon.id)
        logged_on_dict = {'time_start':time_start,
                          'time_end':time_end,
                          'users':  logged_on_users,
                          'description': 'logged on',
                          'which_color': USER_GROUP_COLORS[count]}
        user_groups.append(logged_on_dict)
        count += 1

    if 'returning_users' in demographics:
        logged_on_users = getLoggedOnUsers(time_start, time_end).exclude(id=anon.id)
        returning_users = filterByCreatedWhen(logged_on_users, None, time_end=time_start)
        returning_users_dict = {'time_start':time_start,
                                'time_end':time_end,
                                'users': returning_users,
                                'description': 'returning users',
                                'which_color': USER_GROUP_COLORS[count]}
        user_groups.append(returning_users_dict)
        count += 1

    if 'new_users' in demographics:
        new_users = UserProfile.objects.filter(ghost=False).exclude(id=anon.id)
        new_users = filterByCreatedWhen(new_users, time_start, time_end)
        new_users_dict = {'time_start':time_start,
                          'time_end':time_end,
                          'users': new_users,
                          'description': 'new users',
                          'which_color': USER_GROUP_COLORS[count]}
        user_groups.append(new_users_dict)
        count += 1

    return user_groups

def getLoggedOnUsers(time_start, time_end):
    pa = PageAccess.objects.all()
    pa = filterByWhen(pa, time_start, time_end)
    user_ids = pa.values_list('user_id', flat=True)
    logged_on_users = UserProfile.objects.filter(id__in=user_ids)
    return logged_on_users

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
        num_users = len(users)

    if which == 'num_posts':
        posts = metricsGetPostsHelper(time_start, time_end, users)
        c_type = args_dict.get("type")
        if c_type:
            posts = posts.filter(type=c_type)
        result = posts.count()
        if num_users:
            normalized = result / float(num_users)

    elif which == 'num_answers':
        responses = metricsGetResponsesHelper(time_start, time_end, users)
        result = responses.count()
        if num_users:
            normalized = result / float(num_users)

    elif which == 'new_answers':
        responses = metricsGetResponsesHelper(time_start, time_end, users, created=True)
        result = responses.count()
        if num_users:
            normalized = result / float(num_users)

    elif which == 'activity':
        type = args_dict.get('type')
        if type == 'upvotes':
            activity =  VotedAction.objects.filter(value=1).exclude(content__type="R")
        elif type == 'downvotes':
            activity =  VotedAction.objects.filter(value=-1).exclude(content__type="R")
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
        activity = filterByWhen(activity, time_start, time_end)
        if users:
            activity = activity.filter(creator__in=users)
        result = activity.count()
        if num_users:
            normalized = result / float(num_users)

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
            result = num_anon / float(num_stuff) * 100
        else:
            result = 0
        result = str(result)[:2] + "%"
        normalized = result

    elif which == 'page_views':

        anon = getAnonUser()
        pa = PageAccess.objects.exclude(user=anon)
        pa = filterByWhen(pa, time_start, time_end)
        if users:
            pa = pa.filter(user__in=users)

        page = args_dict.get('page')
        if page:
            pa = pa.filter(page=page)

        result = pa.count()
        if num_users:
            normalized = result / float(num_users)

    elif which == 'session_length':
        anon_id = getAnonUser().id
        if not users:
            users = UserProfile.objects.filter(ghost=False).exclude(id=anon_id)
        total_time = datetime.timedelta(seconds=0)
        total_logged_on = 0
        for u in users:
            time_on_site, logged_on = u.getTimeOnSite(time_start, time_end)
            if logged_on:
                total_time += time_on_site
                total_logged_on += 1
        result = int(total_time.total_seconds()) / 60.0
        if total_logged_on:
            normalized = result / float(total_logged_on)

    normalized = str(normalized)
    normalized = normalized[:5]

    return result, normalized

def metricsGetResponsesHelper(time_start, time_end, users, created=False):
    lg = getLoveGovUser()
    responses = Response.objects.exclude(creator=lg)
    if created:
        responses = filterByCreatedWhen(responses, time_start, time_end)
    else:
        responses = filterByEditedWhen(responses, time_start, time_end)
    if users:
        responses = responses.filter(creator__in=users)
    return responses

def metricsGetPostsHelper(time_start, time_end, users):
    posts = Content.objects.filter(type__in=IN_FEED)
    posts = filterByCreatedWhen(posts, time_start, time_end)
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


################################################# LOAD TIMES ###########################################################

def loadTimes(time_start, time_end):

    vals = {}

    ca = ClientAnalytics.objects.all()
    ca = filterByWhen(ca, time_start, time_end)

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
    now = datetime.datetime.now()
    time_start = now - datetime.timedelta(days=days_ago)
    if not days_for:
        time_end = now
    else:
        time_end = now + datetime.timedelta(days=days_for)
    return summaryEmail(time_start, time_end)

def summaryEmail(time_start, time_end):

    vals = {'time_start':time_start,
            'time_end':time_end}

    pa = PageAccess.objects.all()
    pa = filterByWhen(pa, time_start, time_end)

    accessed = {}
    anon_access = []
    for x in pa:
        try:
            user = x.user
            x.post_parameters_dict = x.getPostParametersDict()
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
        user = x['user']
        time_on_site, logged_on = user.getTimeOnSite(time_start, time_end)
        x['session_length'] = time_on_site.total_seconds() / 60.0

    vals['accessed'] = accessed_list

    registered = UserProfile.objects.all()
    registered = filterByCreatedWhen(registered, time_start, time_end)
    registered.order_by("created_when")
    vals['registered'] = registered

    # load times
    vals['load_times_html'] = loadTimes(time_start, time_end)

    # anon access
    anon = anonymousActivity(anon_access)
    vals['anon_activity'] = anon

    # metrics
    demographics = ['logged_on', 'new_users']
    vals['metrics_html'] = getMetricsHTMLFromTimeAndDemographics(time_start, time_end, demographics)

    vals['IGNORED_POST_PARAMETERS'] = ['csrfmiddlewaretoken', 'path', 'action', 'url']

    context = Context(vals)
    template = loader.get_template('emails/daily_summary/daily_summary.html')
    email = template.render(context)

    return email


def anonymousActivity(pa):

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


def sendSummaryEmail(time_start, time_end, email_recipients):
    sendHTMLEmail(subject="LoveGov Summary [summary]", email_html=summaryEmail(time_start, time_end),
        email_sender="info@lovegov.com", email_recipients=email_recipients)


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



def ajaxAnalyticsToExcel():
    """
    Uses list of analytics settings
    """
    import datetime
    dt = datetime.datetime.now().strftime('%y%m%d%H%M%s')
    filename = '/log/profiles/ajax'+settings.CURRENT_TEST_RUN+'.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Profiles '+dt)

    col = 0
    for page, action in settings.BENCHMARK_AJAX:
        label = '('+page+', '+action+')'
        ws.write(0,col,label=label)
        times = ClientAnalytics.objects.filter(page=page, action=action, test_run=settings.CURRENT_TEST_RUN).order_by('load_time').values_list('load_time',flat=True)
        if len(times) > 0:
            from numpy import median, mean
            median, mean, minimum = median(times), mean(times), min(times)
            ws.write(1,col,label=median)
            ws.write(2,col,label=mean)
            ws.write(3,col,label=minimum)
            print label+" mean: "+mean+"ms, median: "+median+"ms"
            for i, time in enumerate(times):
                row = i + 5
                ws.write(row,col,label=time)

        col += 1
    wb.save(filename)
    print filename



