########################################################################################################################
########################################################################################################################
#
#           Comparison
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.defaults import *

# python
import math

#-----------------------------------------------------------------------------------------------------------------------
# Gets a list of buckets (by percent), based on an inputted resolution.
#-----------------------------------------------------------------------------------------------------------------------
def getBucketList(resolution=10):
    bucket_size = 100/resolution
    bucket_list = []
    for i in range(0, resolution):
        bucket_list.append(i*bucket_size)
    return bucket_list

#-----------------------------------------------------------------------------------------------------------------------
# Updates aggregate-response for all groups
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupViews(debug=False, fast=True):

    scheduled_logger.debug("UPDATE GROUP VIEWS")

    if fast:
        groups = UserGroup.objects.all()
        for g in groups:
            print g.title
            updateGroupView(g)
        networks = Network.objects.exclude(alias="congress")
        for g in networks:
            print g.title
            updateGroupView(g)
    else:
        groups = Group.objects.exclude(alias="congress")
        for g in groups:
            print g.title
            updateGroupView(g)

    """
    networks = Network.objects.exclude(name="congress")
    for g in networks:
        updateGroupView(g)
        if debug:
            print "updated: " + enc(g.title) + " aggregate-view"
    print "updated networks."

    groups = UserGroup.objects.all()
    for g in groups:
        updateGroupView(g)
        if debug:
            print "updated: " + enc(g.title) + " aggregate-view"
    print "updated usergroups." """



#-----------------------------------------------------------------------------------------------------------------------
# Updates aggregate-response for congress.
#-----------------------------------------------------------------------------------------------------------------------
def updateCongressView():
    congress = getCongressNetwork()
    updateGroupView(congress)

#-----------------------------------------------------------------------------------------------------------------------
# Updates content-response for all content.
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
#-----------------------------------------------------------------------------------------------------------------------
def updateAllContentLinks(debug=False):
    scheduled_logger.debug("UPDATE CONTENT LINKS")
    contents = Content.objects.filter(in_calc=True)
    for c in contents:
        if debug:
            print "updating: " + enc(c.title) + " content-links"
        updateContentLinks(c, debug=debug)

#-----------------------------------------------------------------------------------------------------------------------
# Updates comparisons between all users.
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
#-----------------------------------------------------------------------------------------------------------------------
def viewCompare(viewA, viewB):

    topics = getMainTopics()
    questions = Question.objects.filter(official=True)
    fast_comparison = fastCompare(questions=questions, viewA=viewA, viewB=viewB, topics=topics)

    comparison = findViewComparison(viewA, viewB)
    if not comparison:
        comparison = ViewComparison(viewA=viewA, viewB=viewB)

    total_bucket = fast_comparison.getTotalBucket()
    comparison.result = total_bucket.getSimilarityPercent()
    comparison.num_q = total_bucket.num_questions
    comparison.when = datetime.datetime.now()
    comparison.saveOptimized(fast_comparison)
    comparison.save()

    return comparison

#    for t in topics:
#        topic_bucket = fast_comparison.getTopicBucket(t)
#        by_topic = comparison.updateTopic(t, topic_bucket)


#-----------------------------------------------------------------------------------------------------------------------
# Returns a comparison between both views, either by retrieving or by calculating and then saving.
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
        explanation = "This was the answer was chosen by " + str(num_chose)
        explanation += " users, making it the most common responses on LoveGov for this question. This calculation is "\
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
#
#   comparisons
#
#
########################################################################################################################
########################################################################################################################

# each bucket stores num_questions, num_similar, weight_questions and weight_similar for some set of questions (the bucket)
class ComparisonBucket:

    # can be initialized with a dictionary of vals, or as all 0s
    def __init__(self, vals=None):
        if vals:
            self.num_questions = vals['num_questions']
            self.num_similar = vals['num_similar']
            self.weight_questions = vals['weight_questions']
            self.weight_similar = vals['weight_similar']
        else:
            self.num_questions = 0
            self.num_similar = 0
            self.weight_similar = 0
            self.weight_questions = 0

    def update(self, similar, weight):
        self.weight_questions += weight
        self.num_questions += 1
        if similar:
            self.weight_similar += weight
            self.num_similar += 1

    def getSimilarityPercent(self):
        if self.weight_questions:
            percent = int(self.weight_similar/float(self.weight_questions)*100)
        else:
            percent = 0
        return percent

    def toDict(self):
        return {'num_questions':self.num_questions,
                'num_similar':self.num_similar,
                'weight_questions':self.weight_questions,
                'weight_similar':self.weight_similar}

# stores a set of buckets that a comparison resulted in, including 'total' bucket
class FastComparison:

    # can be initialized with a json dump of all buckets or with a set of topics and tags to create buckets for
    def __init__(self, topics=None, tags=None, json_buckets=None):
        if json_buckets:
            buckets = json.loads(json_buckets)
            self.buckets={}
            for k,v in buckets.items():
                self.buckets[k] = ComparisonBucket(v)
        else:
            self.buckets = {}
            self.getTotalBucket()
            self.topics = topics
            if topics:
                for t in topics:
                    self.getTopicBucket(t)
            self.tags = tags
            if tags:
                for t in tags:
                    self.getTagBucket(t)

    def getTotalBucket(self):
        key = 'total'
        return self.getBucket(key)

    def getTopicBucket(self, topic):
        key = 'topic:'+topic.alias
        return self.getBucket(key)

    def getTagBucket(self, tag):
        key = 'tag:'+tag
        return self.getBucket(key)

    def getBucket(self, key):
        bucket = self.buckets.get(key)
        if not bucket:
            bucket = ComparisonBucket()
            self.buckets[key] = bucket
        return bucket

    def dumpBuckets(self):
        to_dump = {}
        for k,v in self.buckets.items():
            to_dump[k] = v.toDict()
        return json.dumps(to_dump)

# takes in a set of questions and two worldviews, and compares them overall
# and within buckets for inputted topics and tags
def fastCompare(questions, viewA, viewB, topics=None, tags=None):

    q_ids = questions.values_list("id", flat=True)
    responsesA = viewA.responses.filter(question__id__in=q_ids)
    responsesB = viewB.responses.filter(question__id__in=q_ids)

    comparison = FastComparison(topics, tags)

    for rA in responsesA:
        question = rA.question
        weight = rA.weight
        rB = responsesB.filter(question=question)
        if rB:
            rB = rB[0]
            question = rA.question
            similar = (rA.answer_val == rB.answer_val)
            # total bucket
            comparison.getTotalBucket().update(similar, weight)
            # topic buckets
            if topics:
                topic = question.getMainTopic()
                if topic in topics:
                    comparison.getTopicBucket(topic).update(similar, weight)
            # tag buckets
            if tags:
                tags = question.getTags()
                for tag in tags:
                    if tag in tags:
                        comparison.getTagBucket(tag).update(similar, weight)
    return comparison