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
    viewer = vals['viewer']
    group_subscriptions = viewer.getGroupSubscriptions()
    for g in group_subscriptions:
        g.num_new = g.getNumNewContent(viewer)
    vals['group_subscriptions'] = group_subscriptions
    election_subscriptions = viewer.getElectionSubscriptions()
    for e in election_subscriptions:
        e.num_new = e.getNumNewContent(viewer)
    vals['election_subscriptions'] = election_subscriptions

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
    if which=='mini':
        maximum = MINI_HISTOGRAM_MAXIMUM
    else:
        maximum = -1
    histogram_metadata = {'total':0,
                          'identical':0,
                          'identical_uids':[],
                          'resolution':resolution,
                          'g_id':g_id,
                          'which':which,
                          'increment':increment,
                          'topic_alias':'all',
                          'bucket_uids': bucket_uids,
                          'current_bucket': -1 ,
                          'maximum': maximum}
    vals['histogram_metadata'] = json.dumps(histogram_metadata)


#-----------------------------------------------------------------------------------------------------------------------
# helper for content-detail
#-----------------------------------------------------------------------------------------------------------------------
def contentDetail(request, content, vals):
    vals['content'] = content
    viewer = vals['viewer']
    creator_display = content.getCreatorDisplay(viewer)
    vals['creator'] = creator_display
    user_votes = Voted.objects.filter(user=vals['viewer'])
    my_vote = user_votes.filter(content=content)
    if my_vote:
        vals['my_vote'] = my_vote[0].value
    else:
        vals['my_vote'] = 0
    vals['iown'] = creator_display.you

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
# Recursively generates the html for a comment thread.
# Paramater usage:
#   request: the request object
#   object: the content object (News, Petition, etc. or a parent comment)
#   user: the viewer's UserProfile
#   depth: the level of nesting of the current comment
#   user_votes: list of all votes made by the user
#   user_commetns: list of all comments made by the user
#   start: the comment to start rendering at
#   limit: the max number of comments to render
#   rendered_so_far: number of comments rendered so far, wrapped in a list so it is mutable
# Returns:
#   a string containing the content thread html
#   the number of actual top-level comments (and their children) actually returned
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, user, depth=0, user_votes=None, user_comments=None, vals={}, start=0, limit=None, rendered_so_far=None):
    """Creates the html for a comment thread."""
    if not user_votes:
        user_votes = Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = Comment.objects.filter(creator=user)
    if not rendered_so_far:
        rendered_so_far = [0]
    # Get all comments that are children of the object
    comments = Comment.objects.filter(on_content=object,active=True).order_by('-status')[start:]
    viewer = vals['viewer']
    top_levels = 0
    if comments:
        # Start generating a string of html
        to_return = ''
        for c in comments:
            # Stop if limit is reached
            if rendered_so_far[0] >= limit and depth==0:
                break
            # If comment hasn't been deleted OR it has responses
            if c.active or c.num_comments:
                to_return += "<div class='threaddiv'>"     # open list
                to_return += renderComment(request, vals, c, depth, user_votes, user_comments)
                rendered_so_far[0] += 1
                if depth==0:
                    top_levels += 1
                to_return += makeThread(request,c,user,depth+1,user_votes,user_comments,vals=vals,limit=limit,rendered_so_far=rendered_so_far)[0]    # recur through children
                to_return += "</div>"   # close list
        return to_return, top_levels
    else:
        # No more comments found - return empty string
        return '', top_levels


def renderComment(request, vals, c, depth, user_votes=None, user_comments=None):
    viewer = user = vals['viewer']
    if not user_votes:
        user_votes = Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = Comment.objects.filter(creator=user)
    margin = 30*(depth+1)
    my_vote = user_votes.filter(content=c) # check if i like comment
    if my_vote:
        i_vote = my_vote[0].value
    else: i_vote = 0
    i_own = user_comments.filter(id=c.id) # check if i own comment
    # Prepare vals to render the comment template with appropriate context
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
    return template.render(context)  # render comment html

#-----------------------------------------------------------------------------------------------------------------------
# fills in vals with topic_stats for poll_progress_by_topic.html
#-----------------------------------------------------------------------------------------------------------------------
def getQuestionStats(vals):

    viewer = vals['viewer']
    responses = viewer.view.responses.all()
    topic_stats = []
    lgpoll = getLoveGovPoll()
    vals['lgpoll'] = lgpoll
    questions = lgpoll.questions.all()
    for t in getMainTopics():
        stat = {'topic':t}
        q_ids = questions.filter(main_topic=t).values_list('id', flat=True)
        total = q_ids.count()
        r = responses.filter(question_id__in=q_ids).exclude(most_chosen_answer=None)
        num = r.count()
        stat['total'] = total
        stat['num'] = num
        if total:
            percent = num/float(total)*100
        else:
            percent = 0
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

#-----------------------------------------------------------------------------------------------------------------------
# gets poll progress
#-----------------------------------------------------------------------------------------------------------------------
def getPollProgress(viewer, poll):
    q_ids = poll.questions.all().values_list('id', flat=True)
    responses = viewer.view.responses.filter(question_id__in=q_ids).exclude(most_chosen_answer_id=-1)
    poll_progress = {'completed':responses.count(), 'total':len(q_ids)}
    return poll_progress

#-----------------------------------------------------------------------------------------------------------------------
# fill dictionary for a particular group
#-----------------------------------------------------------------------------------------------------------------------
def valsGroup(viewer, group, vals):
    # Set group and group comparison
    vals['group'] = group
    comparison = group.getComparison(viewer)
    vals['group_comparison'] = comparison
    vals['comparison_breakdown'] = comparison.toBreakdown()

    # Figure out if this user is an admin
    vals['is_user_admin'] = False
    admins = list( group.admins.all() )
    for admin in admins:
        if admin.id == viewer.id:
            vals['is_user_admin'] = True
            break

    # Get list of all Admins
    vals['group_admins'] = group.admins.all()[:2]

    # Get the list of all members and truncate it to be the number of members showing
    group_members = group.getMembers()
    vals['group_members'] = group_members[:16]

    # Get the number of group Follow Requests
    vals['num_group_requests'] = group.getNumFollowRequests()

    # Get the total number of members
    vals['num_members'] = group.num_members

    # vals for group buttons
    valsGroupButtons(viewer, group, vals)

    # pinned
    pinned = group.pinned_content.all()
    vals['pinned'] = pinned

    # histogram
    loadHistogram(5, group.id, 'mini', vals=vals)

    return vals

def valsGroupButtons(viewer, group, vals):
    # Is the current viewer already (requesting to) following this group?
    vals['is_user_requested'] = False
    vals['is_user_confirmed'] = False
    vals['is_user_rejected'] = False
    group_joined = GroupJoined.lg.get_or_none(user=viewer,group=group)
    if group_joined:
        if group_joined.confirmed:
            vals['is_user_confirmed'] = True
        if group_joined.requested:
            vals['is_user_requested'] = True
        if group_joined.rejected:
            vals['is_user_rejected'] = True
    vals['is_user_following'] = group in viewer.group_subscriptions.all()
    return vals

#-----------------------------------------------------------------------------------------------------------------------
# fill dictionary for a particular election
#-----------------------------------------------------------------------------------------------------------------------
def valsElection(viewer, election, vals):
    running = election.running.all().order_by("-num_supporters")
    for r in running:
        r.comparison = r.getComparison(viewer)
    vals['running'] = running
    vals['election'] = election
    vals['i_am_running'] = viewer in running
    vals['is_user_following'] = election in viewer.election_subscriptions.all()
    return vals

#-----------------------------------------------------------------------------------------------------------------------
# fill dictionary for a petition
#-----------------------------------------------------------------------------------------------------------------------
def valsPetition(viewer, petition, vals):
    signers_limit = 1
    vals['petition'] = petition
    signers = petition.getSigners()
    vals['num_signers'] = len(signers)
    vals['signers'] = signers[:signers_limit]
    vals['i_signed'] = (viewer in signers)
    vals['i_created'] = (petition.creator == viewer)

#-----------------------------------------------------------------------------------------------------------------------
# fill dictionary for fb friends invite sidebar
#-----------------------------------------------------------------------------------------------------------------------
def valsFBFriends(request, vals):
    class FBFriend:
        pass
    viewer = vals['viewer']
    fb_friends = []
    if viewer.facebook_id:
        fb_return = fbGet(request,'me/friends/')
        if fb_return:
            friends_list = fb_return['data']
            vals['facebook_authorized'] = False
            if friends_list:
                vals['facebook_authorized'] = True
                for friend in random.sample(friends_list, 4):
                    fb_friend = FBFriend()
                    fb_friend.name = friend['name']
                    fb_friend.id = friend['id']
                    fb_friend.picture_url = "https://graph.facebook.com/" + str(fb_friend.id) + "/picture?type=large"
                    fb_friends.append(fb_friend)
                    vals['facebook_friends'] = fb_friends
    return fb_friends

#-----------------------------------------------------------------------------------------------------------------------
# put all state tuples in dictionary
#-----------------------------------------------------------------------------------------------------------------------
def getStateTuples(vals):
    vals['states'] = STATES


#-----------------------------------------------------------------------------------------------------------------------
# fills vals for reps header
#-----------------------------------------------------------------------------------------------------------------------
def valsRepsHeader(vals):
    viewer = vals['viewer']
    location = viewer.temp_location or viewer.location
    vals['location'] = location

    congressmen = []
    if location:
        vals['state'] = location.state
        vals['district'] = location.district
        vals['latitude'] = location.latitude
        vals['longitude'] = location.longitude
        if location.state:
            senators = getSensFromState(location.state)
            for s in senators:
                congressmen.append(s)
            if location.district:
                reps = getRepsFromLocation(location.state, location.district)
                for r in reps:
                    congressmen.append(r)
    if LOCAL and location:
        bush = getUser("George Bush")
        congressmen = [bush, bush, bush]
    vals['congressmen'] = congressmen
    for x in congressmen:
        x.comparison = x.getComparison(viewer)
    congressmen.sort(key=lambda x:x.comparison.result,reverse=True)
    if len(congressmen) < 3:
        vals['few_congressmen'] = True