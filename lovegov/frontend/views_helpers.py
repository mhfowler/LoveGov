from django.http import HttpResponse, HttpRequest

# lovegov
from lovegov.modernpolitics.backend import *
from lovegov.base_settings import UPDATE
from operator import attrgetter


#-----------------------------------------------------------------------------------------------------------------------
# get questions for weekly digest
#-----------------------------------------------------------------------------------------------------------------------
def getWeeklyDigestQuestions(time_start, time_end, viewer):

    responses = viewer.getView().responses.all()
    answered_ids = responses.values_list("question_id", flat=True)
    questions = Question.objects.exclude(id__in=answered_ids)

    questions = viewer.filterContentOnlyMyContent(questions)

    digested_ids = viewer.digested_content.values_list("id", flat=True)
    questions = questions.exclude(id__in=digested_ids)

    all_users = UserProfile.objects.filter(ghost=False)
    all_user_responses = Response.objects.filter(creator__in=all_users)

    questions_list = []
    for x in questions:
        recent_responses = filterByEditedWhen(all_user_responses, time_start, time_end)
        x.num_recent_responses = recent_responses.count()
        questions_list.append(x)

    questions_list.sort(key=attrgetter('num_recent_responses'), reverse=True)

    return questions_list


def getWeeklyDigestNews(time_start, time_end, viewer):

    digested_ids = viewer.digested_content.values_list("id", flat=True)
    news = News.objects.exclude(id__in=digested_ids)
    news = filterByCreatedWhen(news, time_start, time_end)
    news = viewer.filterContentOnlyMyContent(news)
    news = news.order_by("-status")

    return news

#-----------------------------------------------------------------------------------------------------------------------
# get vals for displaying info about who chose what about question
#-----------------------------------------------------------------------------------------------------------------------
def valsQuestionMetrics(viewer, question, response, vals, in_feed=True):

    percents_chosen_dict = {}
    lg_group = getLoveGovGroup()
    lg_response = lg_group.getResponseToQuestion(question)
    if lg_response:
        for a in question.answers.all():
            a_id = a.id
            percents_chosen_dict[a_id] = {'percent_agreed':lg_response.getPercent(a_id), 'a_id':a_id}

    percents_chosen_list = percents_chosen_dict.values()
    for bubble_vals in percents_chosen_list:
        bubble_html = renderHelper('site/pages/feed/feed_items/question_item_percent_agreed.html', bubble_vals)
        bubble_vals['html'] = bubble_html
    vals['lg_percent_agreed_bubbles'] = percents_chosen_list

def getAgreementBarGraphHTMLHelper(viewer, question, response, in_feed=True):

    groups = []

    if in_feed:
        lg_group = getLoveGovGroup()
        groups.append((lg_group, 'LoveGov'))

        if question.official:
            congress = getCongressGroup()
            groups.append((congress, 'Congress'))

        i_follow_group = viewer.i_follow
        if i_follow_group.num_members:
            groups.append((i_follow_group, 'Friends'))

        if viewer.location and viewer.location.state:
            state = viewer.location.state
            state_group = getStateGroupFromState(state)
            groups.append((state_group, state))

        if len(groups) < 4:
            num_parties_to_select = 4 - len(groups)
            parties = Party.objects.all()
            for x in random.sample(parties, num_parties_to_select):
                groups.append((x, x.getCasualName()))

    groups_dict_list = []
    for g, g_title in groups:
        g_response = g.getResponseToQuestion(question)
        if g_response:
            percent_agreed = g_response.getPercent(response.most_chosen_answer_id)
            total_num = g_response.total_num
        else:
            percent_agreed = 0
            total_num = 0
        g_vals = {'g_title': g_title,'group':g, 'percent_agreed': percent_agreed, 'percent_disagreed':100-percent_agreed, 'total_num':total_num}
        groups_dict_list.append(g_vals)

    to_render = {'groups_dict_list': groups_dict_list}
    return renderHelper('site/pages/feed/feed_items/agreement_bargraph.html', to_render)

#-----------------------------------------------------------------------------------------------------------------------
# vals for likeminded filter
#-----------------------------------------------------------------------------------------------------------------------
def valsLikeMinded(vals):
    viewer = vals['viewer']
    like_minded = viewer.getLikeMindedGroup()
    if like_minded:
        members = like_minded.members.all()
        vals['num_members'] = len(members)
        vals['members'] = members
        vals['num_processed'] = like_minded.processed.count()
    vals['like_minded'] = like_minded

    valsQuestionsThreshold(vals)

#-----------------------------------------------------------------------------------------------------------------------
# sets vals whether viewer is over or under question answering threshold
#-----------------------------------------------------------------------------------------------------------------------
def valsQuestionsThreshold(vals):
    viewer = vals['viewer']

    valsLGPoll(vals)
    poll_progress = vals['lgpoll_progress']

    above_questions_threshold = poll_progress['completed'] >= QUESTIONS_THRESHOLD
    vals['ABOVE_QUESTIONS_THRESHOLD'] = above_questions_threshold
    if not above_questions_threshold:
        getMainTopics(vals)

    if not viewer.checkTask("O"):
        vals['first_only_unanswered'] = True

    return above_questions_threshold

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
    subscriptions = viewer.getSubscriptions()
    group_subscriptions = subscriptions.filter(is_election=False)
    election_subscriptions =  subscriptions.filter(is_election=True)
    for g in group_subscriptions:
        g.num_new = g.getNumNewContent(viewer)
    for g in election_subscriptions:
        g.num_new = g.getNumNewContent(viewer)
    vals['group_subscriptions'] = group_subscriptions
    vals['election_subscriptions'] = election_subscriptions
    valsQuestionsThreshold(vals)

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
                          'topic_text': 'All Topics',
                          'bucket_uids': bucket_uids,
                          'current_bucket': -1 ,
                          'loading_members_nonce':0,
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
# Recursively generates the html for a comment thread (depth-first search).
# Paramater usage:
#   request: the request object
#   object: the content object (News, Petition, etc. or a parent comment)
#   user: the viewer's UserProfile
#   depth: the level of nesting of the current comment
#   user_votes: list of all votes made by the user
#   user_commetns: list of all comments made by the user
#   start: the comment to start rendering at
#   limit: the max number of comments to render
#   rendered_so_far: number of comments rendered so far, wrapped in a list so it is mutable (I know)
#   excluded: a list of comments to exclude from the results, e.g. because they were added by the user and already rendered
# Returns:
#   a string containing the content thread html
#   the number of actual top-level comments (and their children) actually returned
#-----------------------------------------------------------------------------------------------------------------------
def makeThread(request, object, user, depth=0, user_votes=None, user_comments=None, vals={}, start=0, limit=None, rendered_so_far=None, excluded=None):
    """Creates the html for a comment thread."""
    if not user_votes:
        user_votes = Voted.objects.filter(user=user)
    if not user_comments:
        user_comments = Comment.allobjects.filter(creator=user)
    if not rendered_so_far:
        rendered_so_far = [0]
    if not excluded:
        excluded = []
    # Get all comments that are children of the object
    comments = Comment.allobjects.filter(on_content=object).order_by('-status').exclude(id__in=excluded)[start:]
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
        user_comments = Comment.allobjects.filter(creator=user)
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
def getQuestionStats(vals, poll=None):

    viewer = vals['viewer']
    responses = viewer.view.responses.all()
    topic_stats = []
    if poll:
        vals['poll'] = poll
        questions = poll.questions.all()
    else:
        questions = Question.objects.all()
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


def valsLGPoll(vals):

    viewer = vals['viewer']

    lgpoll = vals.get('lgpoll')
    if not lgpoll:
        lgpoll = getLoveGovPoll()
        vals['lgpoll'] = lgpoll

    lgpoll_progress = vals.get('lgpoll_progress')
    if not lgpoll_progress:
        lgpoll_progress = lgpoll.getPollProgress(viewer)
        vals['lgpoll_progress'] = lgpoll_progress


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
    group_members = group.getMembers().order_by("-created_when")
    if admins:
        num_members_display = 16
    else:
        num_members_display = 24
    vals['group_members'] = group_members[:num_members_display]

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
    running = election.members.all().order_by("-num_supporters")

    supporting = viewer.getPoliticians()
    for r in running:
        r.comparison = r.getComparison(viewer)
        r.is_supporting = r in supporting
    vals['running'] = running
    vals['election'] = election
    vals['i_am_running'] = viewer in running
    vals['is_user_following'] = election in viewer.getElectionSubscriptions()
    return vals

#-----------------------------------------------------------------------------------------------------------------------
# fill dictionary for a petition
#-----------------------------------------------------------------------------------------------------------------------
def valsPetition(viewer, petition, vals):
    signers_limit = 6
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
                    fb_id = friend['id']
                    if not UserProfile.lg.get_or_none(facebook_id=fb_id):
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

def valsParties(vals):
    viewer = vals['viewer']
    parties = list(Party.objects.all())
    parties.sort(key=lambda x: x.title[0])
    vals['parties'] = parties
    vals['user_parties'] = viewer.parties.all()

#-----------------------------------------------------------------------------------------------------------------------
# fills vals for reps header
#-----------------------------------------------------------------------------------------------------------------------
def valsRepsHeader(vals):
    viewer = vals['viewer']
    location = viewer.temp_location or viewer.location
    vals['location'] = location

    if location:
        vals['state'] = location.state
        vals['district'] = location.district
        vals['latitude'] = location.latitude
        vals['longitude'] = location.longitude

    congressmen = viewer.getRepresentatives(location)

    if LOCAL and location:
        bush = getUser("George Bush")
        congressmen = [bush, bush, bush]
    vals['congressmen'] = congressmen
    for x in congressmen:
        x.comparison = x.getComparison(viewer)
    congressmen.sort(key=lambda x:x.comparison.result,reverse=True)
    if len(congressmen) < 3:
        vals['few_congressmen'] = True

#-----------------------------------------------------------------------------------------------------------------------
# randomly (or by user info), chooses a teaser header
#-----------------------------------------------------------------------------------------------------------------------
def valsDismissibleHeader(request, vals):

    viewer = vals['viewer']

    if viewer.checkTask("H"):
        return None

    header = random.choice(DISMISSIBLE_HEADERS)
    vals['dismissible_header'] = header

    if header == 'congress_teaser':
        vals['compare_congress_task'] = congress_task = viewer.checkTask("C")
        if not congress_task:
            congress = Group.lg.get_or_none(alias="congress")
            #congress_members = list(UserProfile.objects.filter(primary_role__office__governmental=True))
            #congress_members = random.sample(congress_members, min(16, len(congress_members)))
            #congress_members = UserProfile.objects.filter(primary_role__office__governmental=True)[:16]
            congress_members = UserProfile.objects.filter(currently_in_office=True)[:16]
            if LOCAL:
                congress_members = UserProfile.objects.all()[:16]
            vals['congress'] = congress
            vals['congress_members'] = congress_members

            # warning or not?
            valsLGPoll(vals)
            poll_progress = vals['lgpoll_progress']
            vals['answer_warning'] = poll_progress['completed'] < 15

    elif header == 'find_reps':
        pass

    elif header == 'lovegov_poll':
        valsLGPoll(vals)
        vals['poll_progress'] = vals['lgpoll_progress']


#-----------------------------------------------------------------------------------------------------------------------
# vals for first login
#-----------------------------------------------------------------------------------------------------------------------
def valsFirstLogin(vals):

    viewer = vals['viewer']
    vals['hide_intros'] = hide_intros = viewer.checkTask("H")

    if not hide_intros:
        vals['presidential_task'] = presidential_task = viewer.checkTask("P")
        vals['reps_task'] = reps_task = viewer.checkTask("F")
        vals['like_minded_task'] = like_minded_task = viewer.checkTask("L")
        vals['join_groups_task'] = join_groups_task = viewer.checkTask("J")

        # if user has completed all matching tasks, they see explore feed task
        if presidential_task and reps_task and like_minded_task and join_groups_task:
            vals['completed_all_first_tasks'] = True

            vals['congratulations_task'] = congratulations_task = viewer.checkTask("W")

            # if completed congratulations task (clicking on see congratulations), then show congratulations message and get started header
            if congratulations_task:
                vals['see_congratulations'] = True
                viewer.completeTask("W")
                viewer.completeTask("H")    # and complete hide task, because no get started header from now on

    vals['qa_tutorial'] = not viewer.checkTask("Q")
