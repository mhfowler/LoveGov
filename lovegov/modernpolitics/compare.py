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
# Updates aggregate-response for all groups
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupViews(debug=False):
    scheduled_logger.debug("UPDATE GROUP VIEWS")
    groups = Network.objects.exclude(name="congress")
    for g in groups:
        updateGroupView(g)
        if debug:
            print "updated: " + enc(g.title) + " aggregate-view"

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
    #-------------------------------------------------------------------------------------------------------------------
    def compareAll(self, method='W'):
        questions = Question.objects.all()
        return self.compareQuestions(questions, method=method)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns result of comparing all questions of inputted topic.
    #-------------------------------------------------------------------------------------------------------------------
    def compareTopic(self, topic, method='W'):
        questions = Question.objects.filter(topics__id__exact=topic.id)
        return self.compareQuestions(questions, method=method)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns result of comparing all inputted questions.
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
                    if dif < COMPARISON_CHUNKSIZE:
                        difference += 0
                    elif dif < 2* COMPARISON_CHUNKSIZE:
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