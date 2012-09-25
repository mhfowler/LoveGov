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
def getFeedItems(viewer, alias, feed_ranking, feed_types, feed_start, num, like_minded=False):

    # special feed
    home_hot_feed = (feed_ranking == 'H' and alias == 'home')

    # get all content in the running
    if home_hot_feed:
        viewer.updateHotFeedIfOld(delta=HOT_FEED_GOES_REALLY_STALE_IN_THIS_MUCH_TIME)
        content = viewer.getHotFeedContent()
        if like_minded:
            like_content_ids = viewer.getLikeMindedGroup().getContent().values_list("id", flat=True)
            content = content.filter(id__in=like_content_ids)
    # if like minded, we do it special like dat
    elif like_minded:
        content = viewer.getLikeMindedGroup().getContent()
    # else we do it normal
    else:
        content = getContentFromAlias(alias, viewer)
        if not content:
            return []

    # filter
    if feed_types:
        feed_type = feed_types[0]
        content = content.filter(type=feed_type)
    else:
        feed_type = None

    # sort
    if not home_hot_feed:
        content = sortHelper(content, feed_ranking, feed_type)

    # paginate
    content = content[feed_start:feed_start+num]
    return content


def getContentFromAlias(alias, viewer):
    content = None
    if alias == 'home':
        content = Content.objects.filter(in_feed=True)
    elif alias == 'friends':
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(in_feed=True, creator_id__in=friends_ids)
    elif alias == 'like_minded':
        content = viewer.getLikeMindedGroup().getContent()
    elif alias == 'my_elections':
        elections = viewer.getElectionSubscriptions()
        elections_ids = elections.values_list("id", flat=True)
        content = Content.objects.filter(posted_to_id__in=elections_ids)
    elif alias ==  'my_groups':
        groups = viewer.getGroupSubscriptions()
        groups_ids = groups.values_list("id", flat=True)
        content = Content.objects.filter(posted_to_id__in=groups_ids)
    elif alias == 'representatives':
        representatives = viewer.getRepresentatives(location=viewer.temp_location)
        content = getLegislationFromCongressmen(representatives)
    elif alias == 'congress':
        content = Legislation.objects.all()
    elif alias == 'me':
        groups_ids = viewer.getGroups().values_list("id", flat=True)
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(Q(posted_to_id__in=groups_ids) | Q(creator_id__in=friends_ids))
    else:
        object = aliasToObject(alias)
        if object:
            content = object.getContent()

    return content


def getQuestionComparisons(viewer, to_compare, feed_ranking, question_ranking,
                           feed_topic, scorecard=None, feed_start=0, num=10):
    question_items = []
    them_responses = to_compare.view.responses.filter(privacy="PUB")
    you_responses = viewer.view.responses.all()

    if scorecard:
        scorecard_responses = scorecard.scorecard_view.responses.all()

        # filter
        if feed_topic:
            scorecard_responses = scorecard_responses.filter(main_topic=feed_topic)

        # append
        for scorecard_response in scorecard_responses:
            q = scorecard_response.question
            their_response = getResponseHelper(them_responses, q)
            if their_response:
                your_response = getResponseHelper(you_responses, q)
                q_item = getQuestionItem(question=q,
                    you=viewer, your_response=your_response,
                    them=to_compare, their_response=their_response,
                    scorecard=scorecard, scorecard_response=scorecard_response)
                question_items.append(q_item)

    elif viewer.id != to_compare.id:
        # filter
        if feed_topic:
            them_responses = them_responses.filter(main_topic=feed_topic)

        # append
        for r in them_responses:
            q = r.question
            your_response = getResponseHelper(you_responses, q)
            their_response = r
            q_item = getQuestionItem(question=q,
                you=viewer, your_response=your_response,
                them=to_compare, their_response=their_response)
            question_items.append(q_item)

    else:
        # filter
        if feed_topic:
            you_responses = you_responses.filter(main_topic=feed_topic)

        # append
        for r in you_responses:
            q = r.question
            your_response = getResponseHelper(you_responses, q)
            q_item = getQuestionItem(question=q,
                you=viewer, your_response=your_response,
                them=None, their_response=None)
            question_items.append(q_item)


    # sort
    if question_ranking:
        question_items = responsesSortHelper(question_items, question_ranking)
    elif feed_ranking:
        question_items = responsesSortHelper(question_items, feed_ranking)

    return question_items[feed_start:feed_start+num]


def getQuestionItems(viewer, feed_ranking, feed_topic=None, only_unanswered=False, poll=None, scorecard=None, feed_start=0, num=10):

    # questions & check for p_id (filter by poll)
    if not poll:
        questions = Question.objects.all()
    else:
        questions = poll.questions.all()
    question_items=[]

    # viewer responses
    if not scorecard:
        you_responses = viewer.view.responses.all()
    else:
        you_responses = scorecard.scorecard_view.responses.all()

    # filter
    if feed_topic:
        questions = questions.filter(main_topic=feed_topic)
    if only_unanswered:
        q_ids = you_responses.exclude(most_chosen_answer=None).values_list("question_id", flat=True)
        questions = questions.exclude(id__in=q_ids)

    # sort & append
    questions = questionsSortHelper(questions, feed_ranking)
    for q in questions:
        your_response = getResponseHelper(you_responses, q)
        q_item = getQuestionItem(question=q,
            you=viewer, your_response=your_response,
            them=None, their_response=None)
        question_items.append(q_item)

    # paginate
    if num:
        question_items = question_items[feed_start:feed_start+num]
    else:
        question_items = question_items[feed_start:]
    return question_items


def getResponseHelper(responses, question):
    r = responses.filter(question=question)
    if r:
        return r[0]
    else:
        return None

def sortHelper(content, feed_ranking, feed_type=None):
    if feed_ranking == 'N':
        content = content.order_by("-created_when")
    elif feed_ranking == 'H' and feed_type == "Q":
        content_ids = content.values_list("id", flat=True)
        content = Question.objects.filter(id__in=content_ids).order_by("-questions_hot_score")
    elif feed_ranking == 'H':
        content = content.order_by("-hot_score")
    elif feed_ranking == 'B' and feed_type == "Q":
        content_ids = content.values_list("id", flat=True)
        content = Question.objects.filter(id__in=content_ids).order_by("-num_responses")
    elif feed_ranking == 'B':
        content = content.order_by("-status")
    return content

def questionsSortHelper(questions, feed_ranking):
    if feed_ranking == 'N':
        questions = questions.order_by("-created_when")
    elif feed_ranking == 'H':
        questions = questions.order_by("-questions_hot_score")
    elif feed_ranking == 'B':
        questions = questions.order_by("-num_responses")
    return questions

def responsesSortHelper(question_items, ranking):
    if ranking == 'B':
        question_items.sort(key=lambda x:x['question'].status, reverse=True)
    elif ranking == 'H':
        question_items.sort(key=lambda x:x['question'].hot_score, reverse=True)
    elif ranking == 'N':
        question_items.sort(key=lambda x:x['question'].created_when, reverse=True)
    elif ranking == 'R':
        def recentComparison(item):
            them = item['them']
            if not them:
                to_return=datetime.datetime.min
            else:
                to_return=them.created_when
            return to_return
        question_items.sort(key=lambda x:recentComparison(x))
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

def getQuestionItem(question, you, your_response, them, their_response, scorecard=None, scorecard_response=None):
    responses = []
    if scorecard_response:
        responses.append({'response':scorecard_response,'responder':scorecard})
    if their_response:
        responses.append({'response':their_response,'responder':them})
    if your_response:
        responses.append({'response':your_response,'responder':you})
    q_item = {'question':question, 'you':your_response, 'them':their_response, 'scorecard':scorecard_response, 'compare_responses':responses}
    compareQuestionItem(q_item)
    return q_item

def compareQuestionItem(q_item):
    your_response = q_item['you']
    their_response = q_item['them']
    scorecard_response = q_item['scorecard']
    if your_response and their_response and scorecard_response:
        if their_response.most_chosen_answer_id and scorecard_response.most_chosen_answer_id:
            if their_response.most_chosen_answer_id == scorecard_response.most_chosen_answer_id:
                agree = 1
            else:
                agree = -1
        else:
            agree = 0
    elif your_response and their_response:
        if your_response.most_chosen_answer_id and their_response.most_chosen_answer_id:
            if your_response.most_chosen_answer_id == their_response.most_chosen_answer_id:
                agree = 1
            else:
                agree = -1
        else:
            agree = 0
    else:
        agree = 0
    q_item['agree'] = agree


### gets legislation based on filter parametrs ###
def getLegislationItems(session_set, type_set, subject_set, committee_set, introduced_set, sponsor_body_set, sponsor_name_set, sponsor_party, feed_start):

    # all legislation
    legislation_items = Legislation.objects.all()

    # filter
    if session_set:
        legislation_items = legislation_items.filter(
            congress_session__in=session_set)
    if type_set:
        legislation_items = legislation_items.filter(
            bill_type__in=type_set)
    if subject_set:
        legislation_items = legislation_items.filter(
            bill_subjects__in=subject_set)
    if committee_set:
        legislation_items = legislation_items.filter(
            committees__in=committee_set)
    if introduced_set:
        date_dict = json.loads(introduced_set)
        date = datetime.date(year=date_dict['year'], month=date_dict['month'], day=date_dict['day'])
        legislation_items = legislation_items.filter(
            bill_introduced__gte=date)
    if sponsor_body_set:
        legislation_items = legislation_items.filter(
            congress_body__in=sponsor_body_set)
    if sponsor_name_set:
        legislation_items = legislation_items.filter(
            sponsor__in=sponsor_name_set)
    if sponsor_party:
        users = UserProfile.objects.filter(parties=sponsor_party, politician=True)
        users_ids = users.values_list("id", flat=True)
        legislation_items = legislation_items.filter(sponsor_id__in=users_ids)

    # paginate
    legislation_items = legislation_items[feed_start:feed_start+10]

    return legislation_items

### gets legislation from representatives, all things they sponsored (or cosponsored?) ##
def getLegislationFromCongressmen(congressmen):

    #congressmen_ids = congressmen.values_list("id", flat=True)

    #legislation = Legislation.objects.filter()
    #cosponsored = LegislationCosponsor.objects.filter(cosponsor_id__in=congressmen_ids)

    congressmen_ids = [x.id for x in congressmen]
    sponsored = Legislation.objects.filter(sponsor_id__in=congressmen_ids)

    return sponsored


### update hot scores for all content ###
def updateHotScores(debug=False):
    for c in Content.objects.filter(in_feed=True):
        if debug: print c.get_name()
        c.calculateHotScore()
    for q in Question.objects.all():
        if debug: print q.get_name()
        q.recalculateQuestionHotScore()


### update hot feed of a particular user ###
def updateHotFeeds(debug=False):
    real_users = UserProfile.objects.filter(ghost=False)
    for u in real_users:
        if debug: print "+II+ updating " + u.get_name()
        u.updateHotFeed()

### update hot scores then update hot feeds ###
def updateHot(debug=False):
    updateHotScores(debug)
    updateHotFeeds(debug)