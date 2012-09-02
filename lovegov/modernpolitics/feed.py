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
    if not content:
        return []

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
    content = None
    if object:
        content = object.getContent()
    elif alias == 'home':
        content = Content.objects.filter(in_feed=True)
    elif alias == 'friends':
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(in_feed=True, creator_id__in=friends_ids)
    elif alias == 'like_minded':
        content = viewer.getLikeMindedGroup().getContent()
    elif alias == 'me':
        groups_ids = viewer.getGroups().values_list("id", flat=True)
        friends_ids = viewer.getIFollow().values_list("id", flat=True)
        content = Content.objects.filter(Q(posted_to_id__in=groups_ids) | Q(creator_id__in=friends_ids))
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

    else:
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

    # sort
    questions = sortHelper(questions, feed_ranking)
    for q in questions:
        your_response = getResponseHelper(you_responses, q)
        if your_response:
            responses = [your_response]
        else:
            responses= []
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

def sortHelper(content, feed_ranking):
    if feed_ranking == 'N':
        content = content.order_by("-created_when")
    elif feed_ranking == 'H':
        content = content.order_by("-hot_score")
    elif feed_ranking == 'B':
        content = content.order_by("-status")
    return content


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
def getLegislationItems(session_set, type_set, subject_set, committee_set, introduced_set, sponsor_body_set, sponsor_name_set, sponsor_party_set, sponsor_district_set, feed_start):

    # all legislation
    legislation_items = Legislation.objects.all()

    # filter
    if session_set:
        legislation_items = legislation_items.filter(
            congress_session__in=session_set)
    else: legislation_items = legislation_items
    if type_set:
        legislation_items = legislation_items.filter(
            bill_type__in=type_set)
    else: legislation_items = legislation_items
    if subject_set:
        legislation_items = legislation_items.filter(
            bill_subjects__in=subject_set)
    else: legislation_items = legislation_items
    if committee_set:
        legislation_items = legislation_items.filter(
            committees__in=committee_set)
    else: legislation_items = legislation_items
    if introduced_set:
        date_dict = json.loads(introduced_set)
        date = datetime.date(year=date_dict['year'], month=date_dict['month'], day=date_dict['day'])
        legislation_items = legislation_items.filter(
            bill_introduced__gte=date)
    else: legislation_items = legislation_items
    if sponsor_body_set:
        legislation_items = legislation_items.filter(
            congress_body__in=sponsor_body_set)
    else: legislation_items = legislation_items
    if sponsor_name_set:
        legislation_items = legislation_items.filter(
            sponsor__in=sponsor_name_set)
    else: legislation_items = legislation_items
    if sponsor_party_set:
        legislation_items = legislation_items.filter(
            sponsor__in=sponsor_party_set)
    else: legislation_items = legislation_items
    if sponsor_district_set:
        legislation_items = legislation_items.filter(
            sponsor__in=sponsor_district_set)
    else: legislation_items = legislation_items

    # paginate
    legislation_items = legislation_items[feed_start:feed_start+10]

    return legislation_items

### update hot scores for all content ###
def updateHotScores():
    for c in Content.objects.filter(in_feed=True):
        c.recalculateHotScore()

