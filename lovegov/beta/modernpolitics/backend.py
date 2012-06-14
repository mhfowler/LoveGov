########################################################################################################################
########################################################################################################################
#
#           Backend
#               methods that get called sometimes, by us, not by request
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

# Our Imports
from lovegov.beta.modernpolitics.models import *
from lovegov.beta.modernpolitics.constants import *

# Django Imports
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django import db

### External Imports ###
from BeautifulSoup import BeautifulStoneSoup
import traceback
import math
from operator import itemgetter

scheduled_logger = logging.getLogger('scheduledlogger')
logger = logging.getLogger('filelogger')

########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Updates all things that require updating.
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def update(debug=True):
    updateRank(debug=debug)
    updateGroupViews(debug=debug)
    updateCalcViews(debug=debug)
    updateAllGroupFeeds(debug=debug)
    updateUserFeeds(debug=debug)
    updateUserComparisons(debug=debug)
    updateAllContentLinks(debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Updates stati of all content... for viewing how ranking algo works
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def updateRank(debug=True):
    scheduled_logger.debug("UPDATE RANK")
    content = Content.objects.all()
    filter = getDefaultFilter()
    users = UserProfile.objects.filter(user_type='U')
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
# Updates aggregate-response for all groups
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupViews(debug=False):
    scheduled_logger.debug("UPDATE GROUP VIEWS")
    groups = Network.objects.exclude(name="congress")
    for g in groups:
        updateGroupView(g)
        if debug:
            print "updated: " + enc(g.title) + " aggregate-view"

def updateCongressView():
    congress = getCongressNetwork()
    updateGroupView(congress)

#-----------------------------------------------------------------------------------------------------------------------
# Updates content-response for all content.
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def updateCalcViews(debug=False):
    scheduled_logger.debug("UPDATE CALC VIEWS")
    contents = Content.objects.filter(in_calc=True)
    for c in contents:
        updateContentView(c)
        if debug:
            print "updated: " + enc(c.title) + " calculated-view"

#-----------------------------------------------------------------------------------------------------------------------
# Updates content-content links for all content.
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def updateAllContentLinks(debug=False):
    scheduled_logger.debug("UPDATE CONTENT LINKS")
    contents = Content.objects.filter(in_calc=True)
    for c in contents:
        if debug:
            print "updating: " + enc(c.title) + " content-links"
        updateContentLinks(c, debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Updates feeds for all users
# args:
# tags: USABLE
# frequency: call once a day?
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
# args:
# tags: USABLE
# frequency: call once a day?
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
    content = Content.objects.filter(Q(type='P') | Q(type='N'))
    # new_feed
    new_feed = getNewFeed()
    filter = getNewFilter()
    updateFeedHelper(a_feed=new_feed, filter_setting=filter, content=content)
    # hot_feed
    hot_feed = getHotFeed()
    filter = getHotFilter()
    updateFeedHelper(a_feed=hot_feed, filter_setting=filter, content=content)
    # best_feed
    best_feed = getBestFeed()
    filter = getBestFilter()
    updateFeedHelper(a_feed=best_feed, filter_setting=filter, content=content)

def getFeedItems(start, stop, feed_type=None, topics=None):
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
    items = feed(x=constants.FEED_MAX, filter_setting=filter_setting, content=content)
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
def feedSwitcher(feed_type = 'C', x=constants.FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None):
    if feed_type == 'C':
        return feed(x=constants.FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None)
    else:
        return feed(x=constants.FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a number of items to get, as well as a list of users, perspective and filter_setting, and returns the top
# x items ranked based on the inputted parameters.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def feed(x=constants.FEED_SIZE, users=-1, worldview=None, filter_setting=None, debug=False, content=None):
    #### initialize default values if not inputted ####
    if users==-1:
        users = UserProfile.objects.filter(user_type='U')
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


#-----------------------------------------------------------------------------------------------------------------------
# Updates comparisons between all users.
# args:
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def updateUserComparisons(debug=False):
    scheduled_logger.debug("UPDATE USER COMPARISONS")
    users = UserProfile.objects.filter(user_type='U')
    i=0
    for a in users:
        for b in users[i:]:
            getUserUserComparison(a, b, force=True)
            if debug:
                print "compared: " + enc(a.get_name()) + " and " + enc(b.get_name())
        i += 1      # keeps from replicating comparisons

#-----------------------------------------------------------------------------------------------------------------------
# This should probably never be called...
#-----------------------------------------------------------------------------------------------------------------------
def updateViewComparisons(debug=False):
    scheduled_logger.debug("UPDATE VIEW COMPARISONS")
    views = WorldView.objects.all()
    i=0
    for a in views:
        for b in views[i:]:
            viewCompare(a, b)
            if debug:
                print "compared: view[" + str(a.id) + "] and view[" + str(b.id) + "]"
        i += 1      # keeps from replicating comparisons

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for findUserComparison which does comparison if one doesn't already exist.
#-----------------------------------------------------------------------------------------------------------------------
def getUserUserComparison(userA, userB, force=False):
    viewA = userA.getView()
    viewB = userB.getView()
    return getViewComparison(viewA, viewB, force=force, dateA=userA.last_answered, dateB=userB.last_answered)

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for getViewComparison, takes in user and content
#-----------------------------------------------------------------------------------------------------------------------
def getUserContentComparison(user, content, force=False):
    viewA = user.getView()
    viewB = content.getCalculatedView()
    return getViewComparison(viewA, viewB, force)

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for getViewComparison, which takes in user and group
#-----------------------------------------------------------------------------------------------------------------------
def getUserGroupComparison(user, group, force=False):
    userView = user.getView()
    groupView = group.getGroupView()
    return getViewComparison(userView, groupView, force)

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for findUserComparison which does comparison if one doesn't already exist.
#-----------------------------------------------------------------------------------------------------------------------
def getViewComparison(viewA, viewB, force=False, dateA=None, dateB=None):
    if force:
        comparison = viewCompare(viewA, viewB)
    else:
        comparison = findViewComparison(viewA, viewB)
        if not comparison:
            comparison = viewCompare(viewA, viewB)
        else:
            if comparison.checkStale(dateA, dateB):
                comparison=viewCompare(viewA, viewB)
    return comparison

#-----------------------------------------------------------------------------------------------------------------------
# Creates or updates comparison between two views.
# args: viewA, viewB
# tags: USABLE
# frequency: call once a day?
#-----------------------------------------------------------------------------------------------------------------------
def viewCompare(viewA, viewB):
    comparator = Comparison(viewA.responses.all(), viewB.responses.all())
    (result, num_q) = comparator.compareAll()
    comparison = findViewComparison(viewA, viewB)
    # if not found, create new comparison in db
    if not comparison:
        new_comparison = ViewComparison(viewA=viewA, viewB=viewB, result=result, num_q= num_q)
        new_comparison.save()
        # do topics
        all_topics = Topic.objects.all()
        for topic in all_topics:
            (result, num_q)  = comparator.compareTopic(topic)
            topic_comparison = TopicComparison(topic=topic, result=result, num_q=num_q)
            topic_comparison.save()
            new_comparison.bytopic.add(topic_comparison)
        return new_comparison
    # else just update
    else:
        when = datetime.datetime.now()
        comparison.update(result=result, num_q=num_q, when=when)
        # update topics
        for t in comparison.bytopic.all():
            (result, num_q) = comparator.compareTopic(t.topic)
            t.update(result=result, num_q=num_q)
        return comparison

#-----------------------------------------------------------------------------------------------------------------------
# Returns a comparison between both views, either by retrieving or by calculating and then saving.
# args: viewA, viewB
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def findViewComparison(viewA, viewB, bidirectional=False):
    first_filter = ViewComparison.objects.filter(viewA=viewA, viewB=viewB)
    if first_filter:
        return first_filter[0]
    elif bidirectional:
        second_filter = UserComparison.objects.filter(viewA=viewB, viewB=viewA)
        if second_filter:
            return second_filter[0]
        else:
            return None
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# Wrapper for findViewComparison which takes in two users
#-----------------------------------------------------------------------------------------------------------------------
def findUserComparison(userA, userB):
    viewA = userA.getView()
    viewB = userB.getView()
    return findViewComparison(viewA, viewB)

#-----------------------------------------------------------------------------------------------------------------------
# Updates inputted comparison.
#-----------------------------------------------------------------------------------------------------------------------
def updateComparison(comparison):
    return viewCompare(viewA=comparison.viewA, viewB=comparison.viewB)


#-----------------------------------------------------------------------------------------------------------------------
# Takes in a group and saves/updates AggregateResponse appropriately.
# args: group (group to save view for)
# tags: USABLE
# frequency: call on all groups every day?
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupView(group):
    users = group.members.all()
    worldview = group.group_view
    if worldview:
        # update old questions
        for r in worldview.responses.all():
            agg = r.aggregateresponse   # downcast
            q = agg.question
            aggregateHelper(question=q, users=users, object=agg, update=True)
        # new questions
        old_ids = worldview.responses.all().values_list("question", flat=True)
        #print ("test: " + old_ids)
        new_questions = Question.objects.filter(official=True).exclude(id__in=old_ids)
        for q in new_questions:
            agg = AggregateResponse(title=group.title + ' ' + q.title + " Aggregate", question=q)
            agg = aggregateHelper(question=q, users=users, object=agg)
            worldview.responses.add(agg)
    # create world view, recall
    else:
        wv = WorldView()
        wv.save()
        group.group_view = wv
        group.save()
        updateGroupView(group)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a piece of content, and updates or creates its associated content response by aggregating users whol liked.
# args: content (content to be updated)
# frequency: everyday?
#-----------------------------------------------------------------------------------------------------------------------
def updateContentView(content):
    questions = Question.objects.filter(official=True)
    user_ids = Voted.objects.filter(content=content, value=1).values_list("user", flat=True)
    users = UserProfile.objects.filter(id__in=user_ids)
    # update
    if content.calculated_view_id != -1:
        worldview = content.getCalculatedView()
        for w in worldview.responses.all():
            agg = w.downcast()
            q = agg.question
            aggregateHelper(question=q, users=users, object=agg, update=True)
        # new questions
        old_ids = worldview.responses.all().values_list("question", flat=True)
        new_questions = Question.objects.exclude(id__in=old_ids)
        for q in new_questions:
            agg = AggregateResponse(title=content.title + ' ' + q.title + " Aggregate", question=q)
            agg = aggregateHelper(question=q, users=users, object=agg)
            worldview.responses.add(agg)
    # create
    else:
        worldview = WorldView()
        worldview.save()
        content.calculated_view_id = worldview.id
        content.save()
        for q in questions:
            agg = AggregateResponse(title=content.title + ' ' + q.title + " Aggregate", question=q)
            agg = aggregateHelper(question=q, users=users, object=agg)
            worldview.responses.add(agg)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a piece of content, and updates or creates content links between it and the most highly associated content.
# frequency: everyday?
#-----------------------------------------------------------------------------------------------------------------------
def updateContentLinks(content, debug=False):
    filter = getDefaultFilter()
    links = content.getLinks()
    supporters = content.getSupporters()                # people who agree with or upvote this content
    for l in links: # update association for already formed links
        l.association_strength=calcRank(content=l.to_content, users=supporters, filter_setting=filter)
        l.autoSave()
    # re highest associated content
    associated = feed(users=supporters, filter_setting=filter)     # content most highly regarded by supporters of this content
    for x in associated:
        c = x[0]
        rank = x[1]
        if c!=content:
            if debug:
                print (" ** rank[" + enc(c.title) + "]: " + str(rank))
            update = links.filter(to_content=c)
            if update:
                link = update[0]
                link.association_strength=rank
                link.autoSave()
            else:
                link = Linked(from_content=content, to_content=c, association_strength=rank)
                link.autoSave()

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a question and a set of users, and an AggregateResponse and calculates
# tuples, answer_avg and answer_val for that agg, then saves and returns agg.
# args: question (question to calculate over), users (to get responses from), object (agg to save to),
# create (boolean which is true if this is create instead of update)
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def aggregateHelper(question, users, object, update=False):
    sum = 0
    total = 0
    answers = {}
    # create aggregate tuples
    for choice in question.answers.all().order_by("value"):
        tuple = AggregateTuple(answer_val=choice.value, tally=0)
        answers[choice.value] = tuple
    for p in users:
        response = UserResponse.objects.filter(question=question, responder=p)
        if response:
            # keep track of tally
            index = response[0].answer_val
            if index in answers:
                answers[index].tally += 1
            # calculate average
            sum += index
            total += 1
    # calculate mean
    if total:
        mean = float(sum)/float(total)
    else:
        mean = 5
    # calculate most chosen
    most = 0
    which = -1
    for value, tup in answers.items():
        if tup.tally >= most:
            most = tup.tally
            which = value
    # set values
    object.answer_avg = str(mean)
    object.answer_val = which
    object.total = total
    # if update
    if update:
        object.save()
        object.smartClearResponses()
        object.users.clear()
    # else new
    else:
        object.autoSave()
    # add users
    for u in users:
        object.users.add(u)
    # add agg tuples
    for tuple in answers.itervalues():
        tuple.save()
        object.responses.add(tuple)
    return object

#-----------------------------------------------------------------------------------------------------------------------
# Updates aggregate responses for lovegov group, and sets lovegov user responses to most highly chosen answer of all
# answers.
#-----------------------------------------------------------------------------------------------------------------------
def updateLoveGovResponses():
    updateGroupView(getLoveGovGroup())
    aggs = getLoveGovGroup().group_view.responses
    user = getLoveGovUser()
    for x in aggs.all():
        question = x.question
        my_response = user.getView().responses.filter(question=question)
        num_chose = x.aggregateresponse.responses.filter(answer_val=x.answer_val)[0].tally
        explanation = "This was the answer was chosen by " + str(num_chose) + " users," \
        "making it the most common responses on LoveGov for this question. This calculation is " \
        "updated every hour on the hour, so you're voice will be accounted for soon if it hasn't been already."
        # save new response
        if not my_response:
            response = UserResponse(responder=user,
                question=question,
                answer_val= x.answer_val,
                explanation=explanation)
            response.autoSave(creator=user, privacy='PUB')
        # else update old response
        else:
            response = my_response[0]
            user_response = response.userresponse
            user_response.answer_val= x.answer_val
            user_response.explanation = explanation
            user_response.save()
    user.last_answered = datetime.datetime.now()
    user.save()

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
        return constants.MIN_RANK

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
    time_multiplier = constants.NEWFILTER_DAYS - days
    votes = filterVotes(content=content, users=users, prefiltered=prefiltered,
        filter_setting=filter_setting,  prefiltered_votes=prefiltered_votes, worldview=worldview, debug=debug)
    score = calcScore(votes)
    rank = score + constants.TIME_BONUS*time_multiplier
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





########################################################################################################################
########################################################################################################################
#    Create stuff
#
########################################################################################################################
########################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------
# Creates a user for the alpha based on name and email (with autogenerated password)
# args: name, email
#-----------------------------------------------------------------------------------------------------------------------
def createAlphaUser(name, email):
    password = passwordAutogen()
    createUser(name, email, password)
    sendAlphaTesterEmail(name, email, password)

def createFBUser(name, email):
    password = generateRandomPassword(10)
    control = createUser(name, email, password)
    sendFBRegisterEmail(name, email, password)
    return control

def passwordAutogen(length=10):
    possible = "23456qwertasdfgzxcvbQWERTASDFGZXCVB789yuiophjknmYUIPHJKLNM"
    r = random.Random()
    password = ""
    for i in range(length):
        char = r.choice(possible)
        password += char
    print "password: " + password
    return password

#-----------------------------------------------------------------------------------------------------------------------
# Generates a random password with digits and characters of given length
#-----------------------------------------------------------------------------------------------------------------------
import string
def generateRandomPassword(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))

#-------------------------------------------------------------------------------------------------------------------
# creates a new userprofile from name, email and password, along with controlling user to manage this profile.
# - name, email, password
#-------------------------------------------------------------------------------------------------------------------
def createUser(name, email, password, type='userProfile',active=True):
    if not ControllingUser.objects.filter(username=email):
        control = ControllingUser.objects.create_user(username=email, email=email, password=password)
        control.is_active = active
        control.save()
        logger.debug("created control: " + control.email)
        user_profile = createUserHelper(control=control, name=name, type=type, active=active)
        logger.debug("created userpof: " + user_profile.get_name())
        control.user_profile = user_profile
        control.save()
        return control
    logger.debug("user already exists!")

def getUserProfile(request=None, control_id=None):
    if control_id:
        control = ControllingUser.lg.get_or_none(id=control_id)
    else:
        control = ControllingUser.lg.get_or_none(id=request.user.id)
    if control:
        return control.user_profile
    else:
        return None

def getPrivacy(request):
    """"Returns value of privacy cookie, or in the case of no cookie returns 'public'."""
    try:
        to_return = request.COOKIES['privacy']
    except KeyError:
        logger.error("no privacy cookie")
        to_return = 'PUB'
    return to_return


#-------------------------------------------------------------------------------------------------------------------
# creates a new userprofile from name, email and password, along with controlling user to manage this profile.
# - name, email, password
#-------------------------------------------------------------------------------------------------------------------
def createUserHelper(control,name,type='userProfile',active=True):
    # new user profile
    if type=="politician":
        userProfile = Politician(user_type='P')
    elif type=="senator":
        userProfile = Senator(user_type='S')
    elif type=="representative":
        userProfile = Representative(user_type='R')
    else:
        userProfile = UserProfile(user_type='U')
        toregister = getToRegisterNumber()
        toregister.number -= 1
        toregister.save()
    # split name into first and last
    names = name.split(" ")
    if len(names) == 2:
        userProfile.first_name = names[0]
        userProfile.last_name = names[1]
    elif len(names) == 3:
        userProfile.first_name = names[0] + " " + names[1]
        userProfile.last_name = names[2]
    # save email and username from control
    userProfile.email = control.email
    userProfile.username = control.username
    # active
    userProfile.is_active = active
    userProfile.confirmation_link = str(random.randint(1,9999999999999999999))   #TODO: crypto-safe
    # worldview
    world_view = WorldView()
    world_view.save()
    userProfile.view_id = world_view.id
    userProfile.save()
    userid = userProfile.id
    # basic info
    userBasicInfo = BasicInfo(id=userid)
    userBasicInfo.save()
    userProfile.basicinfo = userBasicInfo
    # profilePage
    userProfilePage = ProfilePage(person=userProfile)
    userProfilePage.save()
    # alias
    userProfile.makeAlias()
    # filter settings
    filter_setting = getDefaultFilter()
    userProfile.filter_setting = filter_setting
    # notification settings
    userProfile.initNotificationSettings()
    # connections group and lovegov group and join or create network group
    userProfile.createIFollowGroup()
    userProfile.createFollowMeGroup()
    userProfile.joinLoveGovGroup()
    userProfile.joinNetwork()
    # associate with control
    userProfile.user = control
    userProfile.save()
    if type=="userProfile":
        from lovegov.beta.modernpolitics.send_email import sendYayRegisterEmail
        sendYayRegisterEmail(userProfile)
    # return control
    return userProfile

#-------------------------------------------------------------------------------------------------------------------
# Alpha
#-------------------------------------------------------------------------------------------------------------------
def removeUser(email):
    """
    Removes an Alpha user.

    @param email: email address of user to remove
    @type email: string
    """
    control = ControllingUser.objects.get(username=email)
    control.delete()
    return True

########################################################################################################################
########################################################################################################################
# Class stores in a dictionary all responses of one person with all responses of a second
# construct: A (person 1), B (person 2)
#
# compareAll returns a tuple (%similar, num_questions), where num_questions is the number of question-responses
# this comparison was based off of
# compareTopic is the same as compareAll except by topic
########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# Class stores in a dictionary all responses of one person with all responses of a second TODO
# construct: viewA (worldview A), viewB (worldview B)
#
# compareAll returns a tuple (%similar, num_questions), where num_questions is the number of question-responses
# this comparison was based off of
# compareTopic is the same as compareAll except by topic
# userA and userB, its always from the perspective of userA
#=======================================================================================================================
class Comparison:
    def __init__(self, responsesA, responsesB):
        self.responsesA = responsesA
        self.responsesB = responsesB

    #-------------------------------------------------------------------------------------------------------------------
    # Returns result of comparing all topics.
    # arg - topic
    #-------------------------------------------------------------------------------------------------------------------
    def compareAll(self, method='W'):
        questions = Question.objects.all()
        return self.compareQuestions(questions, method=method)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns result of comparing all questions of inputted topic.
    # arg - topic
    #-------------------------------------------------------------------------------------------------------------------
    def compareTopic(self, topic, method='W'):
        questions = Question.objects.filter(topics__id__exact=topic.id)
        return self.compareQuestions(questions, method=method)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns result of comparing all inputted questions.
    # arg - topic
    #-------------------------------------------------------------------------------------------------------------------
    def compareQuestions(self, questions, method='W', aggregate=False):
        difference = 0.0
        total = 0
        total_weight = 0.0
        for q in questions:
            responseA = self.responsesA.filter(question=q)
            responseB = self.responsesB.filter(question=q)
            if responseA and responseB:
                responseA = responseA[0]
                responseB = responseB[0]        # special case for aggregates
                if responseA.type == 'Z': responseA = responseA.aggregateresponse
                if responseB.type == 'Z': responseB = responseB.aggregateresponse
                # default comparison method
                if method == 'D':
                    difference += self.getDifference(responseA, responseB)
                    total += 1
                # chunked comparison method
                elif method == 'C':
                    dif = self.getDifference(responseA, responseB)
                    if dif < constants.COMPARISON_CHUNKSIZE:
                        difference += 0
                    elif dif < 2*constants.COMPARISON_CHUNKSIZE:
                        difference += 1
                    else:
                        difference += 2
                    total += 1
                # comparison based on weighted questions
                elif method == 'W':
                    weight = responseA.weight
                    difference += self.getDifference(responseA, responseB) * weight/10.0
                    total += 1
                    total_weight += weight
        return self.getSimilarityTuple(difference, total, method=method, total_weight=total_weight)


    def getDifference(self, responseA, responseB):
        return math.fabs(responseA.getValue() - responseB.getValue())

    #-------------------------------------------------------------------------------------------------------------------
    # Returns tuple where first first element represent similarity percentage (subjective algo),
    # and second is how many questions.
    # arg - difference (un-processed sim percentage), num_questions (how many questions this was based off of)
    #-------------------------------------------------------------------------------------------------------------------
    def getSimilarityTuple(self, difference, num_questions, method='W', total_weight=0):
        if num_questions :
            if method=='D':
                similarityPercentage = (100 - int(difference / num_questions*10)*100)
            elif method=='C':
                similarityPercentage = (100 - int(difference / num_questions*2)*100)
            elif method=='W':
                similarityPercentage = (100 - int(difference / total_weight*100))
            else:
                similarityPercentage = 0
        else:
            similarityPercentage = 0
        return similarityPercentage, num_questions

########################################################################################################################
########################################################################################################################
#    Initialization methods which are not for testing. They are meant to create and modify db in ways that
#   we will actually want on the site.
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Initialize lovegov settings and other necessary defaults.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGov():
    initializeDefaultImage()
    initializeLoveGovGroup()
    initializeLoveGovUser()
    # initialize topics
    initializeTopicForums()
    initializeTopicImages()
    #initializeTopicMiniImages()
    #initializeTopicColors()
    # filters
    initializeBestFilter()
    initializeNewFilter()
    initializeHotFilter()
    # feeds
    initializeFeeds()
    # init pass codes
    initializePassCodes()

#-----------------------------------------------------------------------------------------------------------------------
# Initializes the user lovegov..... this user represents the site as a whole. Any content created by "us" will be attributed
# to user lovegov.
# lovegov's views will be an aggregate of the views of all memebers of the site.
# we control lovegov.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGovUser():
    if UserProfile.objects.filter(alias="lovegov"):
        print("...lovegov user already initialized.")
    else:
        lovegov = ControllingUser.objects.create_user('lovegov', 'lovegov', 'free')
        lovegov.first_name = 'Love'
        lovegov.last_name = 'Gov'
        user_profile = superUserHelper(lovegov)
        print "initialized: lovegov user"
        return user_profile


#-----------------------------------------------------------------------------------------------------------------------
# Currently, just makes lovegov worldview equal to aggregate of all users on site. But could also do more later.
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGovGroup():
    if Group.objects.filter(alias="LoveGov_Group"):
        print("...lovegov group already initialized.")
    else:
        group = Group(title="LoveGov Group", group_type='O', full_text="We are lovegov.", system=True, alias="LoveGov_Group")
        group.autoSave()
        group.saveDefaultCreated()
        # add all users
        for u in UserProfile.objects.filter(user_type='U'):
            group.members.add(u)
        print("initialized: lovegov group")
        return group

#-----------------------------------------------------------------------------------------------------------------------
# Initializes a user which represents all anonymous users on the site.
#-----------------------------------------------------------------------------------------------------------------------
def initializeAnonymous():
    if UserProfile.objects.filter("anonymouswho"):
        print("...anon user already initialized.")
    else:
        anon = ControllingUser.objects.create_user(username='anon',email='anon@lovegov.com',password='theANON')
        anon.first_name = "Anonymous"
        anon.last_name = "Who"
        userprof = superUserHelper(anon)
        print("initialized: anon user")
        return userprof


#-----------------------------------------------------------------------------------------------------------------------
# Initializes a user which represents all anonymous users on the site.
#-----------------------------------------------------------------------------------------------------------------------
def initializeDefaultImage():
    if UserImage.objects.filter(alias="Default_Image"):
        print("...default image already initialized.")
    else:
        default = UserImage(title="Default Image", summary="default.", alias="Default_Image")
        file = open(constants.DEFAULT_IMAGE)
        default.createImage(file, type=".png")
        default.autoSave()
        print("initialized: default image")
        return default

#-----------------------------------------------------------------------------------------------------------------------
# Initializes best filter... for now same as default filter. Bayesian.
#-----------------------------------------------------------------------------------------------------------------------
def initializeBestFilter():
    if FilterSetting.objects.filter(alias="Best_Filter"):
        print("...best filter already initialized.")
    else:
        filter = FilterSetting(alias="Best_Filter")
        filter.save()
        print("initialized: best filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes new filter... only looks at content made in the last 2 weeks, and values recency.
#-----------------------------------------------------------------------------------------------------------------------
def initializeNewFilter():
    if FilterSetting.objects.filter(alias="New_Filter"):
        print("...new filter already initialized.")
    else:
        days = constants.NEWFILTER_DAYS
        algo = 'R'  # reddit
        filter = FilterSetting(days=days, algo=algo, alias="New_Filter")
        filter.save()
        print("initialized: new filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes hot filter... only looks at votes within time period of hot window (most recent week)
#-----------------------------------------------------------------------------------------------------------------------
def initializeHotFilter():
    if FilterSetting.objects.filter(alias="Hot_Filter"):
        print("...hot filter already initialized.")
    else:
        hot_window = constants.HOT_WINDOW
        algo = 'H'  # hot
        filter = FilterSetting(hot_window=hot_window, algo=algo, alias="Hot_Filter")
        filter.save()
        print("initialized: hot filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes 3 default site-wide feeds.
#-----------------------------------------------------------------------------------------------------------------------
def initializeFeeds():
    initializeFeed("New_Feed")
    initializeFeed("Hot_Feed")
    initializeFeed("Best_Feed")

def initializeFeed(alias):
    if Feed.objects.filter(alias=alias):
        print("..." + alias + " already initialized.")
    else:
        feed = Feed(alias=alias)
        feed.save()
        print("initialized: " + alias + " feed")
        return feed

#-----------------------------------------------------------------------------------------------------------------------
# Initializes forums for every topic.
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicForums():
    for x in Topic.objects.all():
        initializeTopicForum(x)

def initializeTopicForum(x):
    alias = "topicforum:" + x.alias
    if Forum.objects.filter(alias=alias):
        print ("..." + alias + " already initialized")
    else:
        title = x.topic_text + " Forum"
        summary = "A forum for discussing anything related to the topic " + x.topic_text + "."
        forum = Forum(title=title, summary=summary, alias=alias)
        forum.autoSave()
        forum.topics.add(x)
        x.forum_id = forum.id
        x.save()
        print("initialized: " + alias)
        return x

#-----------------------------------------------------------------------------------------------------------------------
# Initialize images for every topic.
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicImages():
    for x in Topic.objects.all():
        if x.topic_text in MAIN_TOPICS:
            initializeTopicImage(x)

def initializeTopicImage(x):
    if x.topic_text in MAIN_TOPICS:
        alias = "topicimage:" + x.alias
        title = x.topic_text + " Image"
        if UserImage.objects.filter(alias=alias):
            print ("..." + alias + " already initialized")
        else:
            summary = "An image representing " + x.topic_text + "."
            im = UserImage(title=title, summary=summary, alias=alias)
            ref = os.path.join(settings.PROJECT_PATH, 'alpha'+x.getImageRef())
            file = open(ref)
            im.createImage(file, type=".png")
            im.autoSave()
            forum = x.getForum()
            forum.main_image_id = im.id
            forum.save()
            # initialize image
            x.image.save(photoKey(".png"), File(file))
            # initialize hover
            hover_ref = 'alpha/static/images/questionIcons/' + x.alias + '/' + x.getPre() + '_hover.png'
            hover_ref = os.path.join(settings.PROJECT_PATH, hover_ref)
            file = open(hover_ref)
            x.hover.save(photoKey(".png"), File(file))
            # initialize selected
            selected_ref = 'alpha/static/images/questionIcons/' + x.alias + '/' + x.getPre() + '_selected.png'
            selected_ref = os.path.join(settings.PROJECT_PATH, selected_ref)
            file = open(selected_ref)
            x.selected.save(photoKey(".png"), File(file))
            # save
            x.save()
            print("initialized: " + title)
            return x
    else:
        return None

#-----------------------------------------------------------------------------------------------------------------------
# Initialize mini images for every topic.
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicMiniImages():
    for topic in Topic.objects.all():
        if topic.topic_text in MAIN_TOPICS:
            title = topic.topic_text + "Mini Image"
            alias = "topicminiimage:" + topic.alias
            summary = "A mini image representing " + topic.topic_text + "."
            img = UserImage(title=title, summary=summary, alias=alias)
            ref = os.path.join(settings.PROJECT_PATH, 'alpha' + topic.getMiniImageRef())
            file = open(ref)
            img.createImage(file, type=".png")
            img.autoSave()
            # save mini image
            topic.image_mini.save(photoKey(".png"), File(file))
            # save
            topic.save()
            print("initialized: " + title)

#-----------------------------------------------------------------------------------------------------------------------
# Initialize colors for every topic
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicColors():
    for topic in Topic.objects.all():
        title = topic.topic_text + " Colors"
        if topic.topic_text is "Economy":
            topic.color = '#92B76C'
            topic.color_light = '#CBE0AF'
        elif topic.topic_text is "Education":
            topic.color = '#9DC5C9'
            topic.color_light = '#C3E7ED'
        elif topic.topic_text is "Energy":
            topic.color = '#F9D180'
            topic.color_light = '#FFF0C5'
        elif topic.topic_text is "Environment":
            topic.color = '#9797C6'
            topic.color_light = '#CACAD8'
        elif topic.topic_text is "Health Care":
            topic.color = '#EA7D95'
            topic.color_light = '#E8B8C6'
        elif topic.topic_text is "National Security":
            topic.color = '#EA947D'
            topic.color_light = '#F9BFB4'
        elif topic.topic_text is "Social Issues":
            topic.color = '#639E9B'
            topic.color_light = '#A3C6C4'
        elif topic.topic_text is "Social Issues":
            topic.color = '#639E9B'
            topic.color_light = '#A3C6C4'
        topic.save()
        print("initialized: " + title)

#-----------------------------------------------------------------------------------------------------------------------
# Initialize network for people with non .edu email extension.
#-----------------------------------------------------------------------------------------------------------------------
def initializeOtherNetwork():
    if Network.objects.filter(name="other"):
        print ("...other network already initialized")
    else:
        network = Network(name="other")
        network.title = "Other Network"
        network.summary = "Network of all people with non recognized emails."
        network.autoSave()
        print ("initialized: Other Network")
        return network

#-----------------------------------------------------------------------------------------------------------------------
# Initialize network for congress
#-----------------------------------------------------------------------------------------------------------------------
def initializeCongressNetwork():
    if Network.objects.filter(name="congress"):
        print ("...congress network already initialized")
    else:
        network = Network(name="congress")
        network.title = "Congress Network"
        network.summary = "Network of all members of Congress."
        network.autoSave()
        # join all members
        congress = UserProfile.objects.filter(Q(user_type='S') | Q(user_type='R'))
        for u in congress:
            network.members.add(u)
            u.network_id = network.id
            u.save()
        print ("initialized: Congress Network")
        return network

#-----------------------------------------------------------------------------------------------------------------------
# Initialize passcodes.
#-----------------------------------------------------------------------------------------------------------------------
def initializePassCodes():
    code = RegisterCode(code_text="politics")
    code.save()
    code = RegisterCode(code_text="brownrisd")
    code.save()

########################################################################################################################
########################################################################################################################
#
#   Scripts for adding objects to database.
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Adds email to valid email list.
#-----------------------------------------------------------------------------------------------------------------------
def addValidEmail(email):
    new_email = ValidEmail(email=email)
    new_email.save()
    print("added: " + str(new_email.email))

########################################################################################################################
########################################################################################################################
#
#   Methods for sending emails
#
########################################################################################################################
########################################################################################################################

#-----------------------------------------------------------------------------------------------------------------------
# Sends email to invite user to lovegov
#-----------------------------------------------------------------------------------------------------------------------
def sendInviteEmail(email):
    recipient_list = [email]
    message = "<h3>" + "Welcome to LoveGov. </h3>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)

#-----------------------------------------------------------------------------------------------------------------------
# Sends confirmation email to user.
#-----------------------------------------------------------------------------------------------------------------------
def sendConfirmationEmail(userProfile):
    recipient_list = [userProfile.email]
    # send email
    send_mail(subject='Welcome to LoveGov.', message="TODO: how to actually send nice emails.",
        from_email='info@lovegov.com', recipient_list=recipient_list)

#-----------------------------------------------------------------------------------------------------------------------
# Sends email to registered alpha user.
#-----------------------------------------------------------------------------------------------------------------------
def sendAlphaTesterEmail(name, email, password):
    recipient_list = [email]
    message = "<h3>" + "Hello " + name + ", </h3>"
    message += "<p>" + "username: " + email + "</p>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)

def sendFBRegisterEmail(name, email, password):
    recipient_list = [email]
    message = "<h3>" + "Hello " + name + ", </h3>"
    message += "<p> welcome to LoveGov! You registered via facebook, and you can connect in the future via facebook or using\
    the username and password below. You can also change your password once you are logged on through the account settings page."
    message += "<p>" + "username: " + email + "</p>"
    message += "<p>" + "password: " + password + "</p>"
    send_mail(subject='Welcome to LoveGov.', message=message,
        from_email='info@lovegov.com', recipient_list=recipient_list)

#-----------------------------------------------------------------------------------------------------------------------
# Sends email of password change
#-----------------------------------------------------------------------------------------------------------------------
def sendPasswordChangeEmail(django_user, password):
    import send_email
    EMAIL_SENDER = 'info@lovegov.com'
    dict = {'password':password,"firstname":django_user.first_name}
    send_email.sendTemplateEmail("Password Change Notification","passwordChange.html",dict,EMAIL_SENDER,django_user.email)

########################################################################################################################
########################################################################################################################
# Initialize db with crap
#       - for ease of testing
#
########################################################################################################################
########################################################################################################################
def initializeDB():
    from lovegov.alpha.splash.splashscript import scriptCreatePresidentialCandidates
    from lovegov.alpha.splash.splashscript import scriptCreateCongressAnswers
    # post-processing of migration
    setTopicAlias()
    # initialize default stuff
    initializeLoveGov()
    ## ## ## ## ## ## ## ##
    initializeAdmin()
    initializeUsers()
    initializeNormalBob()
    initializeContent()
    # valid emails
    initializeValidEmails()
    initializeValidRegisterCodes()
    # initialize congress
    if not LOCAL:
        initializeCongress()
        scriptCreatePresidentialCandidates()
        initializeCommittees()
        initializeLegislation()
        initializeLegislationAmendments()
        initializeVotingRecord()
        scriptCreateCongressAnswers()


def setTopicAlias():
    for t in Topic.objects.all():
        t.makeAlias()


def initializeTestFeedData():
    r = random.Random()
    lovegov = getLoveGovUser()
    for i in range(10):
        title = "News " + str(i)
        p = News(title=title, summary="here's some news for ya", link="www.nytimes.com")
        p.autoSave(creator=lovegov, privacy='PUB')
        # add random amount of votes
        ups = r.choice(range(200))
        for l in range(ups):
            p.like(lovegov, 'PUB')
        downs = r.choice(range(200))
        for d in range(downs):
            p.dislike(lovegov, 'PUB')
    for i in range(100):
        title = "Petition " + str(i)
        p = Petition(title=title, full_text="a test petition aww yea")
        p.autoSave(creator=lovegov, privacy='PUB')
        # add random amount of votes
        ups = r.choice(range(200))
        for l in range(ups):
            p.like(lovegov, 'PUB')
        downs = r.choice(range(200))
        for d in range(downs):
            p.dislike(lovegov, 'PUB')


def initializeNormalBob():
    normal = createUser(name="Normal Bob", email="normal@gmail.com", password="normal")
    normal.user_profile.confirmed = True
    normal.user_profile.save()
    print "initialized: Normal Bob"

def initializeTopics(using="default"):
    t1 = Topic(topic_text="Economy")
    t1.save(using=using)
    t2 = Topic(topic_text="Taxes", parent_topic=t1)
    t2.save(using=using)
    t3 = Topic(topic_text="Education")
    t3.save(using=using)
    t4 = Topic(topic_text="College", parent_topic=t3)
    t4.save(using=using)
    t5 = Topic(topic_text="School Funding", parent_topic=t3)
    t5.save(using=using)
    t6 = Topic(topic_text="Reform")
    t6.save(using=using)
    t7 = Topic(topic_text="Justice Reform", parent_topic=t6)
    t7.save(using=using)
    t8 = Topic(topic_text="Social Issues")
    t8.save(using=using)
    t9 = Topic(topic_text="Foreign Policy")
    t9.save(using=using)
    t10 = Topic(topic_text="Environment")
    t10.save(using=using)
    t11 = Topic(topic_text="Health Care")
    t11.save(using=using)
    t12 = Topic(topic_text="Energy")
    t12.save(using=using)
    t13 = Topic(topic_text="National Security")
    t13.save(using=using)

def initializeAdmin():
    yoshi = ControllingUser.objects.create_superuser(username="yoshi", email="joshcka_tryba@brown.edu", password="hackthis12")
    greg = ControllingUser.objects.create_superuser(username="greg", email="greg@brown.edu", password="greggers")
    yoshi.first_name = "Joshcka"
    yoshi.last_name = "Tryba"
    greg.first_name = "Greg"
    greg.last_name = "Greg"
    superUserHelper(yoshi)
    superUserHelper(greg)

def superUserHelper(control):
    from lovegov.beta.modernpolitics import forms
    name = control.first_name + " " + control.last_name
    user_profile = createUserHelper(control=control, name=name)
    user_profile.confirmed = True
    user_profile.developer = True
    user_profile.save()
    control.user_profile = user_profile
    control.save()
    return user_profile

def initializeUsers():
    # RANDY
    randy = ControllingUser.objects.create_user('randy', 'randy', 'salt')
    randy.first_name = 'Randy'
    randy.last_name = 'Johnson'
    superUserHelper(randy)
    # KATY
    katy = ControllingUser.objects.create_user('katy', 'katy', 'salt')
    katy.first_name = 'Katy'
    katy.last_name = 'Perry'
    superUserHelper(katy)
    # STALIN
    stalin = ControllingUser.objects.create_user('stalin', 'stalin', 'salt')
    stalin.first_name = 'Joseph'
    stalin.last_name = 'Stalin'
    superUserHelper(stalin)
    # CLAY
    clay = ControllingUser.objects.create_user('clayton_dunwell@brown.edu', 'clayton_dunwell@brown.edu', 'texers')
    clay.first_name = 'Clayton'
    clay.last_name = 'Dunwell'
    superUserHelper(clay)

def initializeQ():
    title = 'LoveGov Question'
    question_text = 'Do you love LoveGov?'
    question_type = 'MC'
    a1 = Answer(answer_text="yes",value=5)
    a2 = Answer(answer_text="Lo<3Gov4eva",value=10)
    a1.save()
    a2.save()
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="College")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)
    # # 2
    title = 'Other Question'
    question_text = 'Whatsup?'
    question_type = 'MC'
    a1 = Answer(answer_text="not much",value=5)
    a2 = Answer(answer_text="coding",value=3)
    a1.save()
    a2.save()
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="Education")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)


def initializeQuestions():
    # QUESTION 1
    a1 = Answer(answer_text="macaroni",value=1)
    a2 = Answer(answer_text="chicken",value=2)
    a3 = Answer(answer_text="chocolate milk",value=3)
    a4 = Answer(answer_text="jello",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'Food Question'
    question_text = 'Which food would you eat for the rest of your life?'
    question_type = 'MC'
    type = 'Q'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic = Topic.objects.get(topic_text="Economy")
    q1.topics.add(topic)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)
    # QUESTION 2
    a1 = Answer(answer_text="obama",value=1)
    a2 = Answer(answer_text="michael jordan",value=2)
    a3 = Answer(answer_text="kim jung",value=3)
    a4 = Answer(answer_text="lil wayne",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'President Question'
    question_text = 'Who would you vote for president?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="College")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)
    # QUESTION 3
    a1 = Answer(answer_text="Yes",value=1)
    a2 = Answer(answer_text="No",value=2)
    a3 = Answer(answer_text="Abortion is permissible in rare cases",value=3)
    a1.save()
    a2.save()
    a3.save()
    title = 'Abortion Question'
    question_text = 'Do you considered yourself pro-life?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Social Issues")
    q1.topics.add(topic1)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    # QUESTION 4
    a1 = Answer(answer_text="Yes, significantly",value=1)
    a2 = Answer(answer_text="Yes",value=2)
    a3 = Answer(answer_text="No",value=3)
    a4 = Answer(answer_text="No, and increase spending",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'Military Spending Question'
    question_text = 'Would you like to see the government reduce military spending?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Reform")
    q1.topics.add(topic1)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)


def initializeContent():
    topic = Topic.objects.get(topic_text="Health Care")
    topic2 = Topic.objects.get(topic_text="National Security")
    p1 = Petition(type="P", title="IMPEACH BUSH", summary="impeach bush summary", full_text="We should get rid of President Bush because blah blah blah")
    p2 = Petition(type="P", title="STOP PROP 9", summary="prop 9 summary", full_text="BLAH BLAH BLAH BLAH BLAH BLAH")
    p3 = Petition(type="P", title="BAN GAY MARRIAGE", summary="gay marriage summary", full_text="BAN GAY MARRIAGE FULL TEXT")
    p4 = Petition(type="P", title="REPEAL H.R. 123", summary="REPEAL H.R. 123 summary", full_text="REPEAL H.R. 123 FULL TEXT")
    p1.save()
    p2.save()
    p3.save()
    p4.save()
    p1.topics.add(topic)
    p2.topics.add(topic2)
    p3.topics.add(topic2)
    randy = UserProfile.objects.get(username='randy')
    p1.autoSave(creator=randy,privacy='PUB')
    p2.autoSave(creator=randy,privacy='PUB')
    p3.autoSave(creator=randy,privacy='PUB')
    p4.autoSave(creator=randy,privacy='PUB')
    n1 = News(type="N", title="Legislation to affect....", summary="Legislation to affect....summary", link="www.cnn.com")
    n2 = News(type="N", title="LoveGov launches", summary="changed politics forever", link="www.lovegov.com")
    n1.save()
    n2.save()
    n1.topics.add(topic)
    n2.topics.add(topic2)

    testGroup = Group(type="G", title="SUPER GROUP", summary="group summary", group_type="O", full_text="great group")

    testGroup.autoSave()
    testGroup.topics.add(topic)

def testAddNewContent():
    p1 = Petition(type="P", title="NEW PETITION", summary="new petition summary", full_text="this is the new petition full text")
    p1.save()

def initializeDebate():
    moderator = UserProfile.objects.get(username='stalin')
    now = datetime.datetime.now()
    newDebate = Debate(type="D", title="Health Care Debate", summary="Watch as Maximus Fowler and Clayton Dunwell duke it out", active=True, debate_when=now, moderator=moderator)
    newDebate.save()
    topic = Topic.objects.get(topic_text="Health Care")
    newDebate.topics.add(topic)
    modrelationship = Debaters(side="M", user=moderator, content=newDebate, relationship_type="I", privacy='PUB')
    modrelationship.save()
    debater1 = UserProfile.objects.get(username='stalin')
    debater2 = UserProfile.objects.get(username='katy')
    rel1 = Debaters(side="L", user=debater1, content=newDebate, relationship_type="I", privacy='PUB')
    rel2 = Debaters(side="R", user=debater2, content=newDebate, relationship_type="I", privacy='PUB')
    rel1.save()
    rel2.save()


def initializePersistentDebate():
    debate = Persistent(title="Star Wars Debate", summary="Who shot first?")
    topic = Topic.objects.get(topic_text="Health Care")
    debate.moderator = UserProfile.objects.get(username='stalin')
    debate.affirmative = UserProfile.objects.get(username='randy')
    debate.negative = UserProfile.objects.get(username='katy')
    debate.affirmative_confirmed = True
    debate.type = 'Y'
    debate.debate_type = 'C'
    debate.resolution = "Greedo shot first."
    debate.turns_total = 4
    debate.save()
    debate.topics.add(topic)


def filecount(path):
    count = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)): count += 1
    return count

def initializeCongress():
    for num in range(109,113):
        pathXML = '/data/govtrack/' + str(num) + "/people.xml"
        fileXML = open(pathXML)
        parsedXML = BeautifulStoneSoup(fileXML, selfClosingTags=['role'])
        newSession = CongressSessions(session=int(parsedXML.people['session']))
        newSession.save()
        for personXML in parsedXML.findAll('person'):
            if not ElectedOfficial.objects.filter(govtrack_id=int(personXML['id'])).exists():
                role_type = personXML.role['type']
                if role_type == "rep": role_type = "representative"
                else: role_type = "senator"
                name = personXML['firstname']+ " " + personXML['lastname']
                email = personXML['lastname'] + "_" + personXML['id']
                print "initializing " + email.encode('utf-8','ignore')
                password = "congress"
                congressControl = createUser(name,email,password,type=role_type)
                congressControl.user_profile.autoSave(personXML)
                electedofficial = ElectedOfficial.objects.get(govtrack_id=int(personXML['id']))
                image_path = '/data/govtrack/images/' + str(electedofficial.govtrack_id) + ".jpeg"
                try:
                    electedofficial.setProfileImage(file(image_path))
                except:
                    print "no image here: " + image_path
                newSession.people.add(congressControl.user_profile)
            else:
                newSession.people.add(ElectedOfficial.objects.get(govtrack_id=int(personXML['id'])))


def initializeCommittees():
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + '/committees.xml'
        fileXML = open(filePath)
        BeautifulStoneSoup.NESTABLE_TAGS["member"] = []
        parsedXML = BeautifulStoneSoup(fileXML, selfClosingTags=['member'])
        for committeeXML in parsedXML.findAll(re.compile("^committee$")):
            if not Committee.objects.filter(name=committeeXML['displayname'].encode("utf-8",'ignore')).exists():
                db.reset_queries()
                print "parsing committee"
                committee = Committee()
                committee.saveXML(committeeXML,num)

def initializeLegislation():
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills/"
        fileListing = os.listdir(filePath)
        fileCount = filecount(filePath)
        count = 1
        for infile in fileListing:
            db.reset_queries()
            #print "parsing " + infile + " " + str(count) + '/' + str(fileCount)
            fileXML = open(filePath + infile)
            parsedXML = BeautifulStoneSoup(fileXML)
            newLegislation = Legislation()
            try:
                newLegislation.setSaveAttributes(parsedXML)
            except:
                print "ERROR parsing " + infile + " " + str(count) + '/' + str(fileCount)
                traceback.print_exc()
            count+=1

def initializeLegislationAmendments():
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills.amdt/"
        fileListing = os.listdir(filePath)
        fileCount = filecount(filePath)
        count = 1
        for infile in fileListing:
            db.reset_queries()
            #print "parsing " + infile + " " + str(count) + '/' + str(fileCount)
            if ".xml" in infile:
                fileXML = open(filePath + infile)
                parsedXML = BeautifulStoneSoup(fileXML)
                newLegislation = LegislationAmendment()
                try:
                    newLegislation.saveXML(parsedXML)
                except:
                    print "ERROR parsing " + infile + " " + str(count) + '/' + str(fileCount)
                    traceback.print_exc()
                count+=1

# Initialize Voting Records
def initializeVotingRecord():
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/rolls/"
        fileListing = os.listdir(filePath)
        fileCount = filecount(filePath)
        for infile in fileListing:
            db.reset_queries()
            fileXML = open(filePath + infile)
            parsedXML = BeautifulStoneSoup(fileXML)
            congressRoll = CongressRoll()
            try:
                congressRoll.setSaveAttributes(parsedXML)
            except:
                print "ERROR parsing " + infile + " " + str(count) + '/' + str(fileCount)
                traceback.print_exc()


#-----------------------------------------------------------------------------------------------------------------------
# initializes valid emails
#-----------------------------------------------------------------------------------------------------------------------
def initializeValidEmails():
    brownExtension = ValidEmailExtension(extension='brown.edu')
    brownExtension.save()
    clayEmail = ValidEmail(email='rioisk@gmail.com', description="clay's gmail")
    clayEmail.save()
    maxEmail = ValidEmail(email="max_fowler@brown.edu", description="max's email")
    maxEmail.save()

# initializes valid emails
#-----------------------------------------------------------------------------------------------------------------------
def initializeValidRegisterCodes():
    code = RegisterCode(code_text='brownrisd')
    code.save()

#-----------------------------------------------------------------------------------------------------------------------
# Checks if an email is valid
#-----------------------------------------------------------------------------------------------------------------------
def checkEmail(email):
    splitted = email.split("@")
    if len(splitted)==2:
        extension = splitted[1]
        valid = ValidEmailExtension.objects.filter(extension=extension)
        if valid: return True
        valid = ValidEmail.objects.filter(email=email)
        if valid: return True
        else: return False
    else:
        return False

def checkUnique(email):
    already = ControllingUser.objects.filter(username=email)
    if already: return False
    else: return True

def checkRegisterCode(register_code):
    if RegisterCode.objects.filter(code_text=register_code).exists():
        return True
    else:
        return False

########################################################################################################################
########################################################################################################################
#    methods for getting default lovegov values
#
########################################################################################################################
########################################################################################################################

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def getDefaultImage():
    to_return = UserImage.lg.get_or_none(alias="Default_Image")
    if to_return:
        return to_return
    else:
        return initializeDefaultImage()

def getHotFilter():
    to_return = FilterSetting.lg.get_or_none(alias="Hot_Filter")
    if to_return:
        return to_return
    else:
        return initializeHotFilter()

def getNewFilter():
    to_return = FilterSetting.lg.get_or_none(alias="New_Filter")
    if to_return:
        return to_return
    else:
        return initializeNewFilter()

def getBestFilter():
    to_return = FilterSetting.lg.get_or_none(alias="Best_Filter")
    if to_return:
        return to_return
    else:
        return initializeBestFilter()

def getDefaultFilter():
    return getHotFilter()

def getLoveGovGroup():
    to_return = Group.lg.get_or_none(alias="LoveGov_Group")
    if to_return:
        return to_return
    else:
        return initializeLoveGovGroup()

def getLoveGovGroupView():
    return getLoveGovGroup().group_view.responses.all()

def getLoveGovUser():
    to_return = UserProfile.lg.get_or_none(alias="lovegov")
    if to_return:
        return to_return
    else:
        return initializeLoveGovUser()

def getAnonUser():
    to_return = UserProfile.lg.get_or_none(alias="anonymouswho")
    if to_return:
        return to_return
    else:
        return initializeAnonymous()

def getNewFeed():
    to_return =  Feed.lg.get_or_none(alias='New_Feed')
    if to_return:
        return to_return
    else:
        return initializeFeed('New_Feed')

def getHotFeed():
    to_return = Feed.lg.get_or_none(alias='Hot_Feed')
    if to_return:
        return to_return
    else:
        return initializeFeed('Hot_Feed')

def getBestFeed():
    to_return = Feed.lg.get_or_none(alias='Best_Feed')
    if to_return:
        return to_return
    else:
        return initializeFeed('Best_Feed')

def getTopicImage(topic):
    alias = "topicimage:" + topic.alias
    to_return = UserImage.lg.get_or_none(alias=alias)
    if to_return:
        return to_return
    else:
        return initializeTopicImage(topic)

def getTopicFeed(topic):
    alias = "topicfeed:" + topic.alias
    to_return = UserImage.lg.get_or_none(alias=alias)
    if to_return:
        return to_return
    else:
        return initializeTopicFeed(topic)

# TODO add root topic
def getGeneralTopic():
    to_return = Topic.lg.get_or_none(alias='general')
    if to_return:
        return to_return
    else:
        return initializeGeneralTopic()

def getOtherNetwork():
    to_return = Network.lg.get_or_none(name="other")
    if to_return:
        return to_return
    else:
        return initializeOtherNetwork()

def getCongressNetwork():
    to_return = Network.lg.get_or_none(name="congress")
    if to_return:
        return to_return
    else:
        return initializeCongressNetwork()


def getToRegisterNumber():
    num = LGNumber.lg.get_or_none(alias="to_register")
    if not num:
        num = LGNumber(alias="to_register", number=100)
        num.save()
    return num


def enc(s):
    return s.encode('ascii', 'ignore')


########################################################################################################################
########################################################################################################################
#    methods because I fucked up
#
########################################################################################################################
########################################################################################################################
def restoreUser(user):
    password = generateRandomPassword(10)
    control = ControllingUser.objects.create_user(username=user.username, email=user.username, password=password)
    control.user_profile = user
    control.save()
    user.user = control
    user.save()
    print (user.username + ": " + password)


def resetPassword(user):
    password = generateRandomPassword(10)
    print ("password: " + password)
    user.set_password(password)
    user.save()
    sendPasswordChangeEmail(user, password)






























# old

########################################################################################################################
########################################################################################################################
# These classes are used to generate the feed.  Accesses.py uses these classes.
#
# Class ScoreType
#   - stores total score for each topic
#   - stores subscores based on content type
#
# Class OldFeed
#   - calculates from UserContentRelationship the probability weights for each topic based on the user's actions
#   - (example: Topic 1 Weight = Topic 1 Score / Total Score of all topics)
#   - calculates the content type in a similar fashion as above
#   - generates a (topic, type) tuple
#   - retrieves latest 10 UserContentRelationships matching the generated (topic, type) tuple
#   - calculates probability weights from value of these 10 matches
#   - selects with weighted probabilities the Content to deliver to the feed
########################################################################################################################
########################################################################################################################

CONTENT_TYPE = ('E', 'P', 'N', 'L', 'Q', 'R', 'G', 'C', 'I', 'A', 'Z', 'D')

TOPICS = list(Topic.objects.all().values_list('topic_text', flat=True))

########################################################################################################################


# cache questions
class QUESTIONS:
    objects = Question.objects.all()

# cache topics
class TOPICS:
    objects = Topic.objects.all()


FEED_CONTENT = ['E', 'P', 'N']

RELATIONSHIP_CHOICES = (
    ('L','likes'),
    ('D','dislikes'),
    ('?', 'complicated'),
    ('C','created'),
    ('S', 'shared'),
    ('F','following'),
    ("I", 'involved')
    )

def getRelationshipValue(relationship):
    if relationship == 'L':
        return 1.0
    elif relationship == 'D':
        return -1.0
    elif relationship == 'C':
        return 10.0
    elif relationship == 'S':
        return 5.0
    elif relationship == 'F':
        return 5.0
    else:
        return 1.0


class ScoreType:
    def __init__(self):
        self.totalScore = 0.0
        self.typeScores = {}
        for type in CONTENT_TYPE:
            self.typeScores[type] = 0.0

    ###### PRIVATE METHODS ######

    # adds the value to the appropriate type
    def addScore(self, type, value):
        self.typeScores[type] += value
        self.totalScore += value

    # normalizes the total score to [0,1]
    def normalizeTotalScore(self, scoreSum):
        if self.totalScore > 0.0:
            self.totalScore = self.totalScore / scoreSum

    # normalizes the type scores to [0,1]
    def normalizeTypeScores(self):
        if self.totalScore > 0.0:
            for score in self.typeScores.iterkeys():
                self.typeScores[score] = self.typeScores[score] / self.totalScore

    # gets the total score
    def getTotalScore(self):
        return self.totalScore

    # gets the type score
    def getTypeScore(self,type):
        return self.typeScores[type]

    # returns random type with weighted probabilities
    def getRandomType(self):
        r = random.random()
        for type in self.typeScores.iterkeys():
            score = self.typeScores[type]
            if score > r:
                return type
            else:
                r = r - score

class OldFeed:
    def __init__(self, user):
        self.scoreSum = 0.0
        self.relations = Relationship.objects.filter(user=user)
        self.topicDict = {}
        for topic in TOPICS:
            self.topicDict[topic] = ScoreType()

    ###### PUBLIC METHODS ######

    def calculateScores(self):
        for uc in self.relations:
            topics = list(uc.content.topics.all().values_list('topic_text', flat=True))
            # get topics for comments
            if uc.content.type == 'C':
                topics = list(uc.content.downcast().topics.all().values_list('topic_text', flat=True))
                # get topics of question content if response
            if uc.content.type == 'R':
                topics = list(uc.content.downcast().question.topics.all().values_list('topic_text', flat=True))
            type = uc.content.type
            relationship = uc.relationship_type
            for t in topics:
                value = getRelationshipValue(relationship)
                self.topicDict[t].addScore(type,value)
                self.scoreSum += value
        for score in self.topicDict.itervalues():
            score.normalizeTypeScores()
            score.normalizeTotalScore(self.scoreSum)

    def getTopicTypeMatches(self):
        criteria = self.__getRandomTopicAndType()
        queryset = Relationship.objects.filter(content__type__contains=criteria[1], content__topics__topic_text__contains=criteria[0])
        values = list(queryset.order_by('when')[:10].values_list('content', flat=True))
        # Turn list of values into one big Q objects
        queryset = reduce(lambda q,value: q|Q(id=value), values, Q())
        # Gets recent relevant content
        content = Content.objects.filter(queryset)
        # Choose content to return from weighted status probabilities
        return self.__getReturnContent(content)

    ###### PRIVATE METHODS ######

    def __getReturnContent(self, content):
        total = 0.0
        for c in content:
            total += c.status
        for c in content:
            c.status = float(c.status) / total
        r = random.random()
        for c in content:
            score = c.status
            if score > r:
                return c
            else:
                r = r - score

    def __getRandomTopicAndType(self):
        randomTopic = self.__getRandomTopic()
        randomType = self.topicDict[randomTopic].getRandomType()
        # returns (topic, type) tuple
        return randomTopic, randomType

    def __getRandomTopic(self):
        r = random.random()
        for topic in self.topicDict.iterkeys():
            score = self.topicDict[topic].getTotalScore()
            if score > r:
                return topic
            else:
                r = r - score



def updateTopicFeeds():
    main_topics = Topic.objects.filter(topic_text__in=constants.MAIN_TOPICS)
    for t in main_topics:
        topic_feed = getTopicFeed(t)
        if topic_feed:
            filter = getHotFilter()
            content = t.getContent()
            updateFeedHelper(a_feed=topic_feed, filter_setting=filter, content=content)

def initializeTopicFeed(topic):
    alias = "topicfeed:" + topic.alias
    topic_feed = Feed(alias=alias)
    topic_feed.save()
    print ("initialized: " + alias)
    return topic_feed


def initializeGeneralTopic():
    topic = Topic(topic_text="General", alias="general")
    topic.save()
    initializeTopicForum(topic)
    initializeTopicImage(topic)
    return topic

#-----------------------------------------------------------------------------------------------------------------------
# Updates QuestionDiscussed models (an optimization for storing which questions are most discussed).
#-----------------------------------------------------------------------------------------------------------------------
def updateQuestionDiscussed():
    question_discussed = QuestionDiscussed.objects.all()
    for q in Question.objects.all():
        f = question_discussed.filter(question=q)
        if f:
            qd = f[0]
            qd.num_comments = q.getNumComments()
        else:
            qd = QuestionDiscussed(question=q, num_comments=q.getNumComments())
        qd.save()


#-----------------------------------------------------------------------------------------------------------------------
# Takes in a user, and adds all items in his feed to history, then updates feed (so feed has all new stuff)
# args: user (user to be updated)
# tags: USABLE
# frequency: everyday/whenever-called-by-user
#-----------------------------------------------------------------------------------------------------------------------
def refreshFeed_simple(user):
    for x in user.my_feed.all():
        user.my_history.add(x.content)