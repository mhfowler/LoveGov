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

    html = ajaxRender('site/pages/home/home.html', vals, request)
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