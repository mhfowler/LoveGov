from django.http import HttpResponse, HttpRequest

# lovegov
from lovegov.modernpolitics.backend import *
from lovegov.base_settings import UPDATE

#-----------------------------------------------------------------------------------------------------------------------
# gets frame values and puts in dictionary.
#-----------------------------------------------------------------------------------------------------------------------
def frame(request, vals):
    userProfile = vals['viewer']
    vals['new_notification_count'] = userProfile.getNumNewNotifications()
    vals['firstLogin'] = userProfile.checkFirstLogin()

#-----------------------------------------------------------------------------------------------------------------------
# gets values for right side bar and puts in dictionary
#-----------------------------------------------------------------------------------------------------------------------
def rightSideBar(request, vals):
    userProfile = vals['viewer']
    vals['questions_dict'] = getQuestionsDictionary(questions=getOfficialQuestions(vals), vals=vals)
    getMainTopics(vals)

#-----------------------------------------------------------------------------------------------------------------------
# left sidedbar for home page (navbar)
#-----------------------------------------------------------------------------------------------------------------------
def homeSidebar(request, vals):
    vals['sidebar'] = 'sidebar'
    vals['groups'] = UserGroup.objects.all()

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses to questions
#-----------------------------------------------------------------------------------------------------------------------
def getUserResponses(request,vals={}):
    userProfile = vals['viewer']
    vals['qr'] = userProfile.getUserResponses()

#-----------------------------------------------------------------------------------------------------------------------
# gets the users responses proper format for web
#-----------------------------------------------------------------------------------------------------------------------
def getUserWebResponsesJSON(request,vals={},webCompare=False):

    questionsArray = {}
    topics = getMainTopics(vals)
    for t in topics:
        questionsArray[t.topic_text] = []

    for (question,response) in vals['viewer'].getUserResponses():
        answerArray = []
        for answer in question.answers.all():
            if response and (not webCompare or response.privacy == "PUB"):
                checked = (answer.id == response.most_chosen_answer.id)
                weight = response.weight
            else:
                checked = False
                weight = 5
            answer_json = {'answer_text':answer.answer_text,'answer_id':answer.id,'user_answer':checked,'weight':weight}
            answerArray.append(answer_json)
        toAddquestion = {'id':question.id,'text':question.question_text,'answers':answerArray,'user_explanation':"",'childrenData':[]}
        if response: toAddquestion['user_explanation'] = response.downcast().explanation
        if not webCompare and response: toAddquestion['security'] = response.privacy
        else: toAddquestion['security'] = ""
        questionsArray[question.getMainTopic().topic_text].append(toAddquestion)
    vals['questionsArray'] = json.dumps(questionsArray)

#-----------------------------------------------------------------------------------------------------------------------
# loads histogram metadata into vals
#-----------------------------------------------------------------------------------------------------------------------
def loadHistogram(resolution, g_id, which, increment=1, vals={}):
    bucket_list = getBucketList(resolution)
    vals['buckets'] = bucket_list
    bucket_uids = {}
    for x in bucket_list:
        bucket_uids[x] = []
    histogram_metadata = {'total':0,
                          'identical':0,
                          'identical_uids':[],
                          'resolution':resolution,
                          'g_id':g_id,
                          'which':which,
                          'increment':increment,
                          'topic_alias':'all',
                          'bucket_uids': bucket_uids,
                          'current_bucket': -1 }
    vals['histogram_metadata'] = json.dumps(histogram_metadata)


#-----------------------------------------------------------------------------------------------------------------------
# helper for content-detail
#-----------------------------------------------------------------------------------------------------------------------
def contentDetail(request, content, vals):
    rightSideBar(request, vals)
    shareButton(request, vals)
    vals['thread_html'] = makeThread(request, content, vals['viewer'], vals=vals)
    vals['topic'] = content.getMainTopic()
    vals['content'] = content
    viewer = vals['viewer']
    creator_display = content.getCreatorDisplay(viewer)
    vals['creator'] = creator_display
    vals['recent_actions'] = Action.objects.filter(privacy="PUB").order_by('-when')[:5]
    user_votes = Voted.objects.filter(user=vals['viewer'])
    my_vote = user_votes.filter(content=content)
    if my_vote:
        vals['my_vote'] = my_vote[0].value
    else:
        vals['my_vote'] = 0
    vals['iown'] = (creator_display.you)

#-----------------------------------------------------------------------------------------------------------------------
# get share button values
#-----------------------------------------------------------------------------------------------------------------------
def shareButton(request, vals={}):
    viewer = vals['viewer']
    vals['my_followers'] = viewer.getFollowMe()
    getMyGroups(request, vals)

#-----------------------------------------------------------------------------------------------------------------------
# fills in vals for a question
#-----------------------------------------------------------------------------------------------------------------------
def valsQuestion(request, q_id, vals={}):
    user = vals['viewer']
    question = Question.objects.filter(id=q_id)[0]
    contentDetail(request=request, content=question, vals=vals)
    vals['question'] = question
    my_response = user.getView().responses.filter(question=question)
    if my_response:
        vals['response']=my_response[0]
    answers = []
    agg = getLoveGovGroupView().filter(question=question)
    # get aggregate percentages for answers
    if agg:
        agg = agg[0]
    for a in question.answers.all():
        if agg:
            tallies = agg.answer_tallies.filter(answer_id=a.id)
            if tallies and agg.total_num:
                tally = tallies[0]
                percent = int(100*float(tally.tally)/float(agg.total_num))
            else:
                percent = 0
        else:
            percent = 0
        answers.append(AnswerClass(a.answer_text, a.id, percent))
    vals['answers'] = answers
    topic_text = question.getMainTopic().topic_text
    vals['topic_img_ref'] = MAIN_TOPICS_IMG[topic_text]
    vals['topic_color'] = MAIN_TOPICS_COLORS[topic_text]['light']

class AnswerClass:
    def __init__(self, text, id, percent):
        self.text = text
        self.id = id
        self.percent = percent

#-----------------------------------------------------------------------------------------------------------------------
# Creates the html for a comment thread.
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, user, depth=0, user_votes=None, user_comments=None, vals={}):
    """Creates the html for a comment thread."""
    if not user_votes:
        user_votes = Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = Comment.objects.filter(creator=user)
    comments = Comment.objects.filter(on_content=object).order_by('-status')
    viewer = vals['viewer']
    if comments:
        to_return = ''
        for c in comments:
            if c.active or c.num_comments:
                margin = 30*(depth+1)
                to_return += "<span class='collapse'>[-]</span><div class='threaddiv'>"     # open list
                my_vote = user_votes.filter(content=c) # check if i like comment
                if my_vote:
                    i_vote = my_vote[0].value
                else: i_vote = 0
                i_own = user_comments.filter(id=c.id) # check if i own comment
                vals.update({'comment': c,
                             'my_vote': i_vote,
                             'owner': i_own,
                             'votes': c.upvotes - c.downvotes,
                             'display_name': c.getThreadDisplayName(viewer, getSourcePath(request)),
                             'creator': c.getCreatorDisplay(viewer),
                             'public': c.getPublic(),
                             'margin': margin,
                             'width': 690-(30*depth+1)-30,
                             'defaultImage':getDefaultImage().image,
                             'depth':depth})

                context = RequestContext(request,vals)
                template = loader.get_template('site/pieces/comment.html')
                comment_string = template.render(context)  # render comment html
                to_return += comment_string
                to_return += makeThread(request,c,user,depth+1,user_votes,user_comments,vals=vals)    # recur through children
                to_return += "</div>"   # close list
        return to_return
    else:
        return ''

#-----------------------------------------------------------------------------------------------------------------------
# fills in vals with topic_stats for poll_stats.html
#-----------------------------------------------------------------------------------------------------------------------
def getQuestionStats(vals):

    viewer = vals['viewer']
    responses = viewer.view.responses.all()
    topic_stats = []
    for t in getMainTopics():
        stat = {'topic':t}
        q_ids = Question.objects.filter(main_topic=t, official=True).values_list('id', flat=True)
        total = q_ids.count()
        r = responses.filter(question_id__in=q_ids).exclude(most_chosen_answer=None)
        num = r.count()
        stat['total'] = total
        stat['num'] = num
        percent = num/float(total)*100
        stat['percent'] = percent
        stat['empty'] = 100-percent
        topic_stats.append(stat)
    vals['topic_stats'] = topic_stats

#-----------------------------------------------------------------------------------------------------------------------
# returns a list of group tuples for rendering the agrees_box
#-----------------------------------------------------------------------------------------------------------------------
def getGroupTuples(viewer, question, response):
    my_groups = viewer.getGroups().order_by("-num_members")[:10]
    group_tuples = []
    for g in my_groups:
        g_response = g.group_view.responses.filter(question=question)
        if g_response and response:
            g_response = g_response[0]
            percent = g_response.getPercent(response.most_chosen_answer_id)
        else:
            percent = 0
        g_tuple = {'percent':percent, 'group':g}
        group_tuples.append(g_tuple)
    return group_tuples

