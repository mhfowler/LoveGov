from lovegov.frontend.views import *

#-----------------------------------------------------------------------------------------------------------------------
# Group page
#-----------------------------------------------------------------------------------------------------------------------
def group(request, g_id=None, vals={}):

    viewer = vals['viewer']

    if not g_id:
        return HttpResponse('Group id not provided to view function')
    group = Group.lg.get_or_none(id=g_id)
    if not group:
        return HttpResponse('Group id not found in database')

    vals['group'] = group
    comparison, json = group.getComparisonJSON(viewer)
    vals['comparison'] = comparison
    vals['json'] = json

    loadHistogram(5, group.id, 'mini', increment=5, vals=vals)

    # Get Follow Requests
    vals['group_requests'] = list(group.getFollowRequests())

    # Get Activity
    num_actions = NOTIFICATION_INCREMENT
    actions = group.getActivity(num=num_actions)
    actions_text = []
    for action in actions:
        actions_text.append( action.getVerbose(view_user=viewer) )
    vals['actions_text'] = actions_text
    vals['num_actions'] = num_actions

    # Is the current viewer already (requesting to) following this group?
    vals['is_user_follow'] = False
    vals['is_user_confirmed'] = False
    vals['is_user_rejected'] = False
    vals['is_visible'] = False
    group_joined = GroupJoined.lg.get_or_none(user=viewer,group=group)
    if group_joined:
        if group_joined.confirmed:
            vals['is_visible'] = True
        if group_joined.requested:
            vals['is_user_follow'] = True
        if group_joined.confirmed:
            vals['is_user_confirmed'] = True
        if group_joined.rejected:
            vals['is_user_rejected'] = True

    if not group.group_privacy == 'S':
        vals['is_visible'] = True

    if group == viewer.i_follow:
        vals['is_visible'] = True

    vals['is_user_admin'] = False
    admins = list( group.admins.all() )
    for admin in admins:
        if admin.id == viewer.id:
            vals['is_user_admin'] = True
    vals['group_admins'] = group.admins.all()

    all_members = list(group.getMembers())
    num_members = MEMBER_INCREMENT
    vals['group_members'] = all_members[:num_members]
    vals['num_members'] = num_members

    members = list( all_members )
    for admin in admins:
        members.remove(admin)
    vals['normal_members'] = members

    vals['num_group_members'] = group.num_members

    followers = list(viewer.getFollowMe())
    for member in all_members:
        if member in followers:
            followers.remove(member)

    vals['non_member_followers'] = followers

    html = ajaxRender('site/pages/home/home_frame.html', vals, request)
    url = group.get_url()
    return framedResponse(request, html, url, vals)


#-----------------------------------------------------------------------------------------------------------------------
# Match page.
#-----------------------------------------------------------------------------------------------------------------------
def newMatch(request,start='presidential', vals={}):

    sections = {'presidential':0,
                'senate':1,
                'social':2,
                'representatives':3}
    vals['start_sequence'] = sections[start]

    viewer = vals['viewer']
    comparison, json = viewer.getComparisonJSON(viewer)
    viewer.compare = json
    viewer.result = comparison.result

    matchSocial(request, vals)
    matchPresidential(request, vals)
    matchSenate(request, vals)
    matchRepresentatives(request, vals)

    html = ajaxRender('site/pages/match/match-new.html', vals, request)
    url = "/match/"
    return framedResponse(request, html, url, vals)

def matchSocial(request, vals={}):
    viewer = vals['viewer']
    vals['friends'] = viewer.getIFollow(num=6)
    vals['groups'] = viewer.getUserGroups(num=6)
    vals['networks'] = viewer.getNetworks()[:4]

def matchPresidential(request, vals={}):
    viewer = vals['viewer']
    if not LOCAL:
        obama = UserProfile.lg.get_or_none(first_name="Barack",last_name="Obama", politician=True)
        paul = UserProfile.lg.get_or_none(first_name="Ronald",last_name="Paul", politician=True)
        romney = UserProfile.lg.get_or_none(first_name="Mitt",last_name="Romney", politician=True)
    else:
        obama = viewer
        paul = viewer
        romney = viewer
    list = [obama,paul,romney]
    for x in list:
        x.prepComparison(viewer)

    list.sort(key=lambda x:x.result,reverse=True)
    vals['presidential'] = list

def matchSenate(request, vals={}):
    viewer = vals['viewer']
    if not LOCAL:
        elizabeth = UserProfile.lg.get_or_none(first_name="Elizabeth", last_name="Warren", politician=True)
        brown = UserProfile.lg.get_or_none(first_name="Scott", last_name="Brown", politician=True)
        voters = getLoveGovGroup()
    else:
        elizabeth = viewer
        brown = viewer
        voters = viewer

    for x in [elizabeth, brown, voters]:
        x.prepComparison(viewer)

    vals['elizabeth'] = elizabeth
    vals['brown'] = brown
    vals['mass'] = voters

def matchRepresentatives(request, vals={}):

    viewer = vals['viewer']
    congressmen = []

    if viewer.location:
        address = viewer.location
        congressmen = []
        congress = CongressSession.lg.get_or_none(session=CURRENT_CONGRESS)
        senator_tag = OfficeTag.lg.get_or_none(name="senator")
        rep_tag = OfficeTag.lg.get_or_none(name="representative")

        if congress:
            rep_office = rep_tag.tag_offices.filter(location__state=address.state,location__district=address.district)[0]
            representative = rep_office.office_terms.filter(end_date__gte=datetime.date.today())[0].user
            if representative:
                congressmen.append(representative)

            senator_office = senator_tag.tag_offices.filter(location__state=address.state)[0]
            senators = map( lambda x : x.user , senator_office.office_terms.filter(end_date__gte=datetime.date.today()) )
            for senator in senators:
                congressmen.append(senator)

        vals['congressmen'] = congressmen
        vals['state'] = address.state
        vals['district'] = address.district
        vals['latitude'] = address.latitude
        vals['longitude'] = address.longitude

    for x in congressmen:
        x.prepComparison(viewer)

    congressmen.sort(key=lambda x:x.result,reverse=True)

    if not congressmen:
        vals['invalid_address'] = True


#-----------------------------------------------------------------------------------------------------------------------
# sensibly redirects to next question
#-----------------------------------------------------------------------------------------------------------------------
def nextQuestion(request, vals={}):
    question = getNextQuestion(request, vals)
    valsQuestion(request, question.id, vals)

    html = ajaxRender('site/pages/content/question_detail.html', vals, request)
    url = question.get_url()
    return framedResponse(request, html, url, vals)

def getNextQuestion(request, vals={}):
    user = vals['viewer']
    responses = user.getView().responses
    answered_ids = responses.values_list('question__id', flat=True)
    unanswered = Question.objects.exclude(id__in=answered_ids)
    if unanswered:
        return random.choice(unanswered)
    else:
        question = Question.objects.all()
        return random.choice(question)

#-----------------------------------------------------------------------------------------------------------------------
# Profile Link
#-----------------------------------------------------------------------------------------------------------------------
def profileOld(request, alias=None, vals={}):
    viewer = vals['viewer']
    if request.method == 'GET':
        if alias:
            frame(request, vals)
            getUserResponses(request,vals)
            # get comparison of person you are looking at
            user_prof = UserProfile.lg.get_or_none(alias=alias)
            ## TODO :: make a warning for multiple aliases!

            comparison, json = user_prof.getComparisonJSON(viewer)
            vals['user_prof'] = user_prof
            vals['comparison'] = comparison
            vals['json'] = json

            # Get users followers
            if user_prof.isNormal():
                prof_follow_me = list(user_prof.getFollowMe())
                for follow_me in prof_follow_me:
                    comparison = getUserUserComparison(user_prof, follow_me)
                    follow_me.compare = comparison.toJSON()
                    follow_me.result = comparison.result
                prof_follow_me.sort(key=lambda x:x.result,reverse=True)
                vals['prof_follow_me'] = prof_follow_me[0:5]
            else:       # get politician supporters
                prof_support_me = user_prof.getSupporters()
                vals['prof_support_me'] = prof_support_me[0:5]


            num_groups = GROUP_INCREMENT
            vals['prof_groups'] = user_prof.getUserGroups(num=num_groups)
            vals['num_groups'] = num_groups

            # Get user's random 5 groups
            #vals['prof_groups'] = user_prof.getGroups(5)

            # Get Follow Requests
            vals['prof_requests'] = list(user_prof.getFollowRequests())
            vals['prof_invites'] = list(user_prof.getGroupInvites())

            # Get Schools and Locations:
            networks = user_prof.networks.all()
            vals['prof_locations'] = networks.filter(network_type='L')
            vals['prof_schools'] = networks.filter(network_type='S')
            vals['prof_parties'] = user_prof.parties.all()

            vals['is_following_you'] = False
            if viewer.id != user_prof.id:
                following_you = UserFollow.lg.get_or_none( user=user_prof, to_user=viewer )
                if following_you and following_you.confirmed:
                    vals['is_following_you'] = True

            # Is the current user already (requesting to) following this profile?
            vals['is_user_requested'] = False
            vals['is_user_confirmed'] = False
            vals['is_user_rejected'] = False
            user_follow = UserFollow.lg.get_or_none(user=viewer,to_user=user_prof)
            if user_follow:
                if user_follow.requested:
                    vals['is_user_requested'] = True
                if user_follow.confirmed:
                    vals['is_user_confirmed'] = True
                if user_follow.rejected:
                    vals['is_user_rejected'] = True

            # Get Activity
            num_actions = NOTIFICATION_INCREMENT
            actions = user_prof.getActivity(num=num_actions)
            actions_text = []
            for action in actions:
                actions_text.append( action.getVerbose(view_user=viewer, vals=vals) )
            vals['actions_text'] = actions_text
            vals['num_actions'] = num_actions

            # Get Notifications
            if viewer.id == user_prof.id:
                notifications_text = []

                num_notifications = NOTIFICATION_INCREMENT
                notifications = viewer.getNotifications(num=num_notifications)
                for notification in notifications:
                    notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )

                vals['notifications_text'] = notifications_text
                vals['num_notifications'] = num_notifications

            # get politician page values
            if not user_prof.isNormal():
                supported = Supported.lg.get_or_none(user=viewer, to_user=user_prof)
                if supported:
                    vals['yousupport'] = supported.confirmed

            # get responses
            vals['responses'] = user_prof.getView().responses.count()
            html = ajaxRender('site/pages/profile/profile_base.html', vals, request)
            url = '/profile/' + alias
            return framedResponse(request, html, url, vals)
        else:
            return shortcuts.redirect('/profile/' + viewer.alias)
    else:
        if request.POST['action']:
            return answer(request, vals)
        else:
            to_alias = request.POST['alias']
            return shortcuts.redirect('/alpha/' + to_alias)