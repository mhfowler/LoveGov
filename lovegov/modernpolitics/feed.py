########################################################################################################################
########################################################################################################################
#
#           Feed
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.initialize import *

# python
from operator import itemgetter

#-----------------------------------------------------------------------------------------------------------------------
# Returns a queryset of feed items, given inputted parameters
#-----------------------------------------------------------------------------------------------------------------------
def getFeedItems(viewer, alias, feed_ranking, feed_types, feed_start, num):

    # get all content in the running
    content = getContentFromAlias(alias, viewer)

    # filter
    if feed_types:
        content = content.filter(type__in=feed_types)

    # sort
    content = sortHelper(content, feed_ranking)

    # paginate
    content = content[feed_start:feed_start+num]
    return content


def getContentFromAlias(alias, viewer):
    object = aliasToObject(alias)
    content = []
    if object:
        content = object.getContent()
    elif alias == 'me':
        groups_ids = viewer.getGroups().values_list("id", flat=True)
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(Q(posted_to_id__in=groups_ids) | Q(creator_id__in=friends_ids))
    elif alias == 'groups':
        groups_ids = viewer.getGroups().values_list("id", flat=True)
        content = Content.objects.filter(in_feed=True, posted_to_id__in=groups_ids)
    elif alias == 'elections':
        content = Petition.objects.all()
    elif alias == 'politicians':
        content = Legislation.objects.all()
    elif alias == 'friends':
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(in_feed=True, creator_id__in=friends_ids)
    return content


def getQuestionComparisons(viewer, to_compare, feed_ranking, question_ranking,
                           feed_topic, feed_start=0, num=10):
    question_items = []
    them_responses = to_compare.view.responses.filter(privacy="PUB")
    you_responses = viewer.view.responses.all()

    # filter
    if feed_topic:
        them_responses = them_responses.filter(main_topic=feed_topic)

    # append
    for r in them_responses:
        q = r.question
        q_item = {'question':q, 'you':getResponseHelper(you_responses, q), 'them':r}
        compareQuestionItem(q_item)
        question_items.append(q_item)

    # sort
    if question_ranking:
        question_items = responsesSortHelper(question_items, question_ranking)
    elif feed_ranking:
        question_items = responsesSortHelper(question_items, feed_ranking)

    return question_items[feed_start:feed_start+num]


def getQuestionItems(viewer, feed_ranking, feed_topic, only_unanswered, feed_start=0, num=10):

    question_items=[]
    questions = Question.objects.all()

    you_responses = viewer.view.responses.all()

    if feed_topic:
        questions = questions.filter(main_topic=feed_topic)
    if only_unanswered:
        q_ids = you_responses.values_list("question_id", flat=True)
        questions = questions.exclude(id__in=q_ids)

    questions = sortHelper(questions, feed_ranking)

    for q in questions:
        q_item = {'question':q, 'you':getResponseHelper(you_responses, q), 'them':None}
        q_item['agree'] = 0
        question_items.append(q_item)

    return question_items[feed_start:feed_start+num]

def getResponseHelper(responses, question):
    r = responses.filter(question=question)
    if r:
        return r[0]
    else:
        return None

def sortHelper(content, feed_ranking):
    if feed_ranking == 'N':
        content = content.order_by("-created_when")
    elif feed_ranking == 'H':
        content = content.order_by("-status")
    elif feed_ranking == 'B':
        content = content.order_by("-status")
    return content

def responsesSortHelper(question_items, ranking):
    if ranking == 'B':
        question_items.sort(key=lambda x:x['question'].status, reverse=True)
    elif ranking == 'H':
        question_items.sort(key=lambda x:x['question'].status, reverse=True)
    elif ranking == 'N':
        question_items.sort(key=lambda x:x['question'].created_when, reverse=True)
    elif ranking == 'R':
        def recentComparison(item):
            you = item['you']
            if not you:
                to_return=datetime.datetime.min
            else:
                to_return=you.created_when
            return to_return
        question_items.sort(key=lambda x:recentComparison(x), reverse=True)
    elif ranking == 'I':
        def importanceComparison(item):
            you = item['you']
            if not you:
                to_return=-1
            else:
                to_return=you.weight
            return to_return
        question_items.sort(key=lambda x:importanceComparison(x), reverse=True)
    elif ranking == 'A':
        question_items = filter(lambda x:x['agree']==1, question_items)
    elif ranking == 'D':
        question_items = filter(lambda x:x['agree']==-1, question_items)
    return question_items

def compareQuestionItem(item):
    you = item['you']
    them = item['them']
    to_return = 0
    if you and them:
        if you.most_chosen_answer_id == them.most_chosen_answer_id:
            to_return = 1
        else:
            to_return = -1
    item['agree'] = to_return
    item['disagree'] = (to_return==-1)
    return to_return

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a filter object, which has all feeds of SimpleFilter, except m2m as id lists
#-----------------------------------------------------------------------------------------------------------------------
def getFeed(filter, start=0, stop=10, saved=False):
    topics = filter['topics']
    types = filter['types']
    levels = filter['levels']
    g_ids = filter['groups']
    groups = Group.objects.filter(id__in=g_ids)
    ranking = filter['ranking']
    submissions_only = filter['submissions_only']
    content = Content.objects.filter(in_feed=True)
    if topics:
        content = content.filter(main_topic__in=topics)
    if types:
        content = content.filter(type__in=types)
    if levels:
        content = content.filter(scale__in=levels)
    if groups:
        u_ids = []
        for g in groups:
            u_ids.extend(g.members.all().values_list("id", flat=True))
        users = UserProfile.objects.filter(id__in=u_ids)
    else:
        users = UserProfile.objects.filter(ghost=False)
    if submissions_only:
        if groups:
            u_ids = users.values_list("id", flat=True)
            content = content.filter(creator_id__in=u_ids)
        return getFeedHelper(content, ranking, start, stop)
    else:
        print "complex feed!"
        return None

def getFeedHelper(content, ranking, start, stop):
    if ranking == 'N':
        return content.order_by("-created_when")[start:stop]
    elif ranking == 'B':
        return content.order_by("-status")[start:stop]
    elif ranking == 'H':
        c_ids = content.values_list("id", flat=True)
        items = getHotFeed().items.filter(content_id__in=c_ids).order_by("-rank")[start:stop]
        to_return = []
        for x in items:
            to_return.append(x.content)
        return to_return

#-----------------------------------------------------------------------------------------------------------------------
# Updates stati of all content... for viewing how ranking algo works
#-----------------------------------------------------------------------------------------------------------------------
def updateRank(debug=True):
    scheduled_logger.debug("UPDATE RANK")
    content = Content.objects.all()
    filter = getDefaultFilter()
    users = UserProfile.objects.filter(ghost=False)
    for c in content:
        print (c.title + ": " + str(calcRank(content=c, filter_setting=filter, users=users, debug=debug)))

#-----------------------------------------------------------------------------------------------------------------------
# Updates the score/status of all content (1 pt per vote)
#-----------------------------------------------------------------------------------------------------------------------
def updateStatus():
    content = Content.objects.all()
    for x in content:
        votes = Voted.objects.filter(content=x)
        score = calcScore(votes)
        x.status = score
        x.save()

#-----------------------------------------------------------------------------------------------------------------------
# Updates feeds for all users
#-----------------------------------------------------------------------------------------------------------------------
def updateUserFeeds(debug=False):
    scheduled_logger.debug("UPDATE USER FEEDS")
    users = UserProfile.objects.all()
    for u in users:
        updateUserFeed(u)
        if debug:
            print "*  updated: " + enc(u.get_name()) + " feed  *"

#-----------------------------------------------------------------------------------------------------------------------
# Updates feeds for all groups
#-----------------------------------------------------------------------------------------------------------------------
def updateAllGroupFeeds(debug=False):
    scheduled_logger.debug("UPDATE GROUP FEEDS")
    groups = Group.objects.all()
    for g in groups:
        updateGroupFeed(g, 'N', debug=debug)
        updateGroupFeed(g, 'H', debug=debug)
        updateGroupFeed(g, 'B', debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Updates feed for lovegov group.
# args:
#-----------------------------------------------------------------------------------------------------------------------
def updateLoveGovFeeds(debug=True):
    scheduled_logger.debug("UPDATE LOVEGOV FEEDS")
    g = getLoveGovGroup()
    updateGroupFeed(g, 'N', debug=debug)
    updateGroupFeed(g, 'H', debug=debug)
    updateGroupFeed(g, 'B', debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Updates sitewide feeds [optimization].
#-----------------------------------------------------------------------------------------------------------------------
def updateSiteFeeds(debug=False):
    content = Content.objects.filter(in_feed=True)

    # hot_feed
    hot_feed = getHotFeed()
    filter = getHotFilter()
    updateFeedHelper(a_feed=hot_feed, filter_setting=filter, content=content)

    # new_feed
    # new_feed = getNewFeed()
    # filter = getNewFilter()
    # updateFeedHelper(a_feed=new_feed, filter_setting=filter, content=content)

    # best_feed
    # best_feed = getBestFeed()
    # filter = getBestFilter()
    # updateFeedHelper(a_feed=best_feed, filter_setting=filter, content=content)

def oldGetFeedItems(start, stop, feed_type=None, topics=None):
    if feed_type == 'N':
        feed = getNewFeed()
    elif feed_type == 'H':
        feed = getHotFeed()
    elif feed_type == 'B':
        feed = getBestFeed()
    items = feed.items.order_by('-rank')
    # if filter by topics
    if topics:
        filtered = []
        for x in items:
            if x.content.main_topic in topics:
                filtered.append(x)
    else:
        filtered = items
    stop = min(stop, len(filtered))
    return filtered[start:stop]

def updateFeedHelper(a_feed, filter_setting, content):
    a_feed.smartClear()
    items = feed(x=FEED_MAX, filter_setting=filter_setting, content=content)
    for i in items:
        new_item = FeedItem(content=i[0], rank=i[1])
        new_item.save()
        a_feed.items.add(new_item)

#-----------------------------------------------------------------------------------------------------------------------
# Updates feeds for a particular group
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupFeed(group, feed_type, debug=False):
    members = group.members.all()
    group.smartClearGroupFeed(feed_type)
    # update new feed #
    if feed_type == 'N':
        if debug:
            print "updating: " + enc(group.title) + " new feed"
        items = feed(users=members, worldview=group.group_view, filter_setting=getNewFilter(), debug=debug)
        for i in items:
            new_item = FeedItem(content=i[0], rank=i[1])
            new_item.save()
            group.group_newfeed.add(new_item)
    # update best feed #
    elif feed_type == 'B':
        if debug:
            print "updating: " + enc(group.title) + " best feed"
        items = feed(users=members, worldview=group.group_view, filter_setting=getBestFilter(), debug=debug)
        for i in items:
            new_item = FeedItem(content=i[0], rank=i[1])
            new_item.save()
            group.group_bestfeed.add(new_item)
    # update hot feed #
    elif feed_type == 'H':
        if debug:
            print "updating: " + enc(group.title) + " hot feed"
        items = feed(users=members, worldview=group.group_view, filter_setting=getHotFilter(), debug=debug)
        for i in items:
            new_item = FeedItem(content=i[0], rank=i[1])
            new_item.save()
            group.group_hotfeed.add(new_item)

#-----------------------------------------------------------------------------------------------------------------------
# Update groups with inputted name.
# args:
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupByName(name, debug=True):
    scheduled_logger.debug("UPDATE " + name + " FEEDS")
    print "***" + enc(name) + "***"
    groups = Group.objects.filter(title__icontains=name)
    for g in groups:
        updateGroupFeed(g, 'N', debug=debug)
        updateGroupFeed(g, 'H', debug=debug)
        updateGroupFeed(g, 'B', debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a user, and updates their feed appropriately (does not remove items currently in feed).
# args: user (user to be updated)
# tags: USABLE
# frequency: everyday/whenever-called-by-user
#-----------------------------------------------------------------------------------------------------------------------
def updateUserFeed(user):
    user.smartClearMyFeed()
    # use custom filter setting to get feed
    filter = user.filter_setting
    if filter:
        items = feed(worldview=user.getView(), filter_setting=filter)
        for i in items:
            new_item = FeedItem(content=i[0], rank=i[1])
            new_item.save()
            user.my_feed.add(new_item)

#-----------------------------------------------------------------------------------------------------------------------
# switcher for different feed types
#-----------------------------------------------------------------------------------------------------------------------
def feedSwitcher(feed_type = 'C', x=FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None):
    if feed_type == 'C':
        return feed(x=FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None)
    else:
        return feed(x=FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a number of items to get, as well as a list of users, perspective and filter_setting, and returns the top
# x items ranked based on the inputted parameters.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def feed(x=FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None):
    #### initialize default values if not inputted ####
    if users==-1:
        users = UserProfile.objects.filter(ghost=False)
    if not worldview:
        worldview = getLoveGovUser().getView()
    if not filter_setting:
        filter_setting = getDefaultFilter()
    if not content:
        content = Content.objects.filter(in_feed=True)
    x = min(x, len(content))
    #### get sorted list of all content based on filter_setting ####
    found = []
    for c in content:
        rank = calcRank(content=c, users=users, worldview=worldview, filter_setting=filter_setting, debug=debug)
        found.append((c, rank))
    sorted_list = sorted(found, key=itemgetter(1), reverse=True)     # sort by second elt of tuple
    items = sorted_list[:x]
    return items


########################################################################################################################
########################################################################################################################
#    Ranking, Feeds & Filtering
#
########################################################################################################################
########################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a piece of content, a list of users, a worldview (who we are filtering for), and a filter_setting, and returns
# rank of inputted content.
# prefiltered_votes is an optional argument, to optimize in the case where acceptable votes are processed earlier
# args: content, users
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def calcRank(content, users, filter_setting, worldview=None, prefiltered=False, prefiltered_votes=None, debug=False):
    # if content is recent enough to be included
    days = filter_setting.days
    if (days==-1) or checkDays(content, days):
        # right now only using one algo to determine rank, but this system makes it easy to experiment with others
        algo = filter_setting.algo
        if algo == 'D':
            rank = bayesianRank(content=content, users=users, filter_setting=filter_setting,
                prefiltered=prefiltered, prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
        elif algo =='H':
            rank = bayesianRank(content=content, users=users, filter_setting=filter_setting,
                prefiltered=prefiltered, prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
        elif algo =='B':
            rank = bayesianRank(content=content, users=users, filter_setting=filter_setting,
                prefiltered=prefiltered, prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
        elif algo =='R':
            rank = redditRank(content=content, users=users, filter_setting=filter_setting,
                prefiltered=prefiltered, prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
        else:
            rank = bayesianRank(content=content, users=users, filter_setting=filter_setting,
                prefiltered=prefiltered, prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
        if debug:
            print(enc(content.title) + " rank: " + unicode(rank))
            # process by topic and type weighting
        rank = weighting(content=content, rank=rank, filter_setting=filter_setting)
        # return rank
        return rank
    # else, return min rank value
    else:
        return MIN_RANK

#-----------------------------------------------------------------------------------------------------------------------
# bayesian ranking algorithm, uses default lovegov bayesian constant unless another one is inputted
# args: content, users
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def bayesianRank(content, users, filter_setting, prefiltered=False, prefiltered_votes=None, worldview=None, debug=False):
    # get average content votes and score
    average_rating = 0.5
    # get this content votes and score
    votes = filterVotes(content=content, users=users, prefiltered=prefiltered,
        filter_setting=filter_setting,  prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
    score = calcScore(votes)
    this_votes = votes.count()
    bayesian_constant = this_votes # need to save and retrieve average num votes TODO: CHANGE THIS!
    if this_votes:
        this_rating = score / this_votes
        rank = ((bayesian_constant * average_rating) + (this_votes * this_rating)) / (bayesian_constant + this_votes)
    else: # divide by zero case
        rank = average_rating
    return rank*100

#-----------------------------------------------------------------------------------------------------------------------
# reddit ranking algorithm, for new_filter... highly values new content, and content degrades over time.
# args: content, users
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def redditRank(content, users, filter_setting, prefiltered=False, prefiltered_votes=None, worldview=None, debug=False):
    days = content.howOld().days
    time_multiplier = NEWFILTER_DAYS - days
    votes = filterVotes(content=content, users=users, prefiltered=prefiltered,
        filter_setting=filter_setting,  prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
    score = calcScore(votes)
    rank = score + TIME_BONUS*time_multiplier
    return rank

#-----------------------------------------------------------------------------------------------------------------------
# Factors rank by type and topic weights.
# args: content, users
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def weighting(content, rank, filter_setting):
    # if weighted by topic
    if filter_setting.by_topic:
        weight = 0
        topics = content.topics.all()
        if topics:
            for t in content.topics.all():
                weight += filter_setting.getTopicWeight(t)
        # what to do for non-topic content?
        else:
            weight=0
            # multiply rank by weight
        rank *= (weight/100)
        # if weighted by type
    if filter_setting.by_type:
        weight = 0
        topics = content.topics.all()
        if topics:
            for t in content.topics.all():
                weight += filter_setting.getTopicWeight(t)
        # what to do for non-topic content?
        else:
            weight=0
            # multiply rank by weight
        rank *= (weight/100)
    return rank

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a queryset of users, a piece of content, and a filter setting, and returns the votes to be counted for that content
# prefiltered is an optional argument, in the case that votes were batch filtered before knowing which content
# args: content, users
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def filterVotes(content, users, filter_setting, prefiltered=False, prefiltered_votes=None, worldview=None, debug=False):
    # filter votes by inputted list of users
    if prefiltered:
        votes = prefiltered_votes.filter(content=content)
    else:
        ids = users.values_list("id", flat=True)
        votes = Voted.objects.filter(content=content, user__id__in=ids)
        # quick check for no votes
    if not votes:
        return votes
        # if not prefiltered, we must first filter votes
    if not prefiltered:
        # filter by similarity and hot window
        to_include_ids= [] # list of ids to exclude
        for v in votes:
            # check if voter is similar enough to inputted worldview
            similarity = filter_setting.similarity
            if (similarity == -1) or checkSimilar(vote=v, similarity=similarity, worldview=worldview):
                # if hot algo, check if vote is recent enough
                if filter_setting.algo == 'H':
                    hot_window = filter_setting.hot_window
                    if (hot_window == -1) or checkWindow(vote=v, hot_window=hot_window):
                        to_include_ids.append(v.id)
                else:
                    to_include_ids.append(v.id)
        votes = votes.filter(id__in=to_include_ids)
    return votes

#-----------------------------------------------------------------------------------------------------------------------
# Helper method which returns a score for a set of votes.
#-----------------------------------------------------------------------------------------------------------------------
def calcScore(votes, ranking='D'):
    score = 0
    for v in votes:
        score += v.getValue(ranking=ranking)
    return score

#-----------------------------------------------------------------------------------------------------------------------
# Helper method which checks if worldview of inputted voter is similar enough to inputted worldview
#-----------------------------------------------------------------------------------------------------------------------
def checkSimilar(vote, similarity, worldview=None):
    voter_view = vote.user.getView()
    # get comparison between voterview and inputted worldview
    comparison = findViewComparison(worldview, voter_view)
    if not comparison:
        comparison = viewCompare(worldview, voter_view)
        # check similarity
    if comparison.result > similarity:
        return True
    else:
        return False

#-----------------------------------------------------------------------------------------------------------------------
# # helper which checks if the vote is older than the number of days in inputted hot_window
#-----------------------------------------------------------------------------------------------------------------------
def checkWindow(vote, hot_window):
    now = datetime.datetime.now()
    then = vote.when
    delta = now - then
    if delta.days > hot_window:
        return False
    else: return True

#-----------------------------------------------------------------------------------------------------------------------
# helper which checks if piece of content is older than inputted number of days
#-----------------------------------------------------------------------------------------------------------------------
def checkDays(content, days):
    delta = content.howOld()
    if delta.days > days:
        return False
    else: return True