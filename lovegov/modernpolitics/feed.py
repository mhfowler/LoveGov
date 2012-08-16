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
        q_item = getQuestionItem(q, getResponseHelper(you_responses, q), r)
        q_item['show_answer'] = q_item['you'] and q_item['them']
        question_items.append(q_item)

    # sort
    if question_ranking:
        question_items = responsesSortHelper(question_items, question_ranking)
    elif feed_ranking:
        question_items = responsesSortHelper(question_items, feed_ranking)

    return question_items[feed_start:feed_start+num]


def getQuestionItems(viewer, feed_ranking, feed_topic=None, only_unanswered=False, questions=None, feed_start=0, num=10):

    # questions
    question_items=[]
    if not questions:
        questions = Question.objects.all()

    # viewer responses
    you_responses = viewer.view.responses.all()

    # filter
    if feed_topic:
        questions = questions.filter(main_topic=feed_topic)
    if only_unanswered:
        q_ids = you_responses.values_list("question_id", flat=True)
        questions = questions.exclude(id__in=q_ids)

    # sort
    questions = sortHelper(questions, feed_ranking)

    for q in questions:
        q_item = getQuestionItem(q, getResponseHelper(you_responses, q), None)
        q_item['show_answer'] = False
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


def getQuestionItem(question, you_response, them_response):
    q_item = {'question':question, 'you':you_response, 'them':them_response}
    compareQuestionItem(q_item)
    return q_item


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
