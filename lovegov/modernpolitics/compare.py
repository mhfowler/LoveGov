########################################################################################################################
########################################################################################################################
#
#           Comparison
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.initialize import *

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
# Updates comparisons between all users.
#-----------------------------------------------------------------------------------------------------------------------
def updateUserComparisons(debug=False):
    scheduled_logger.debug("UPDATE USER COMPARISONS")
    users = UserProfile.objects.filter(ghost=False)
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
    fast_comparison = fastCompare(viewA=viewA, viewB=viewB, topics=topics)

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
        aggregateView(users, worldview)
    else:
        wv = WorldView()
        wv.save()
        group.group_view = wv
        group.save()
        updateGroupView(group)

def aggregateView(users, view):
    for r in view.responses.all():
        q = r.question
        aggregateHelper(question=q, users=users, aggregate=r)
    old_ids = view.responses.all().values_list("question", flat=True)
    new_questions = Question.objects.filter(official=True).exclude(id__in=old_ids)
    for q in new_questions:
        agg = aggregateHelper(question=q, users=users)
        view.responses.add(agg)


#-----------------------------------------------------------------------------------------------------------------------
# Takes in a piece of content, and updates or creates its associated content response by aggregating users whol liked.
#-----------------------------------------------------------------------------------------------------------------------
def updateContentView(content):
    user_ids = Voted.objects.filter(content=content, value=1).values_list("user", flat=True)
    users = UserProfile.objects.filter(id__in=user_ids)
    if content.calculated_view_id != -1:
        worldview = content.getCalculatedView()
        aggregateView(users, worldview)
    else:
        worldview = WorldView()
        worldview.save()
        content.calculated_view_id = worldview.id
        content.save()
        updateContentView(content)

#-----------------------------------------------------------------------------------------------------------------------
# Takes in a question and a set of users, and an AggregateResponse and calculates
# tuples, answer_avg and answer_val for that agg, then saves and returns agg.
#-----------------------------------------------------------------------------------------------------------------------
def aggregateHelper(question, users, aggregate=None):
    if not aggregate:
        aggregate = Response(question=question)
        aggregate.autoSave()
    total_num = 0
    answers = {}
    # create or get answer tally objects
    for choice in question.answers.all():
        already = aggregate.answer_tallies.filter(answer=choice)
        if not already:
            tuple = AnswerTally(answer=choice, tally=0)
            tuple.save()
            aggregate.answer_tallies.add(tuple)
        else:
            tuple = already[0]
            tuple.tally = 0
        answers[choice.id] = tuple
    most_chosen_num = 0
    most_chosen_answer_id = -1
    for p in users:
        response = p.view.responses.filter(question=question)
        if response:
            index = response[0].most_chosen_answer_id
            if index in answers:
                total_num += 1
                tuple = answers[index]
                tuple.tally += 1
                if tuple.tally >= most_chosen_num:
                    most_chosen_num = tuple.tally
                    most_chosen_answer_id = index
    # save tuples
    for a_id,answer_tally in answers.items():
        answer_tally.save()
    # set aggregate response values
    aggregate.most_chosen_answer_id = most_chosen_answer_id
    aggregate.most_chosen_num = most_chosen_num
    aggregate.total_num = total_num
    aggregate.question = question
    aggregate.save()

    return aggregate

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

    def getNumQuestions(self):
        return self.num_questions

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


#=======================================================================================================================
# Compares two world views
# ----------------------------
# takes in a set of questions and two worldviews, and compares them overall
# and within buckets for inputted topics and tags
#=======================================================================================================================
def fastCompare(viewA,viewB,topics=None):
    # Get both sets of responses
    responsesA = viewA.responses.order_by('question')
    responsesB = viewB.responses.order_by('question')
    # Make a comparison object
    comparison = FastComparison(topics)

    # Set response list positions
    a_index = 0
    b_index = 0

    # While the response list positions are valid
    while a_index < len(responsesA) and b_index < len(responsesB):
        # Get the current responses in list
        rA = responsesA[a_index]
        rB = responsesB[b_index]
        # If the question IDs match, compare their answers and save it!
        if rA.question_id == rB.question_id:
            if rA.most_chosen_answer_id and rB.most_chosen_answer_id:
                similar = (rA.most_chosen_answer_id == rB.most_chosen_answer_id)
                weight = rA.weight
                comparison.getTotalBucket().update(similar, weight)
                # And also do something with topic buckets...
                if topics:
                    topic = rA.question.getMainTopic()
                    if topic in topics:
                        comparison.getTopicBucket(topic).update(similar, weight)
            # Then increment both counters
            a_index += 1
            b_index += 1

        # Otherwise, if response A has the smaller question ID
        elif responsesA[a_index].question_id < responsesB[b_index].question_id:
            a_index += 1 # Increment position for response list A
        else: # Otherwise response B has the smaller question ID
            b_index += 1 # Increment position for response list B

    return comparison