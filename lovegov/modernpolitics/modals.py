########################################################################################################################
########################################################################################################################
#
#           Modals
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.actions import *

def getGroupInviteModal(group,user,request,vals={}):
    # Check if the user is an admin
    admins = group.admins.all()
    if user not in admins:
        return ajaxRender( 'site/pages/basic_message.html' , { 'basic_message' : 'You are not a moderator for the group: ' + group.title }, request )

    # Get all members and user followers
    members = group.members.all()
    followers = user.getFollowMe()

    # Find all non-member followers
    non_member_followers = []
    for follower in followers:
        if follower not in members:
            non_member_followers.append(follower)

    # Generate a context for the modal
    vals['group'] = group
    vals['non_member_followers'] = non_member_followers

    return ajaxRender('site/pages/group/group_invite_modal.html',vals,request)


def getGroupRequestsModal(group,user,request,vals={}):
    # Check if the user is an admin
    admins = group.admins.all()
    if user not in admins:
        return ajaxRender( 'site/pages/basic_message.html' , { 'basic_message' : 'You are not a moderator for the group: ' + group.title } )

    # Generate a context for the modal
    vals['group'] = group
    vals['group_requests'] = group.getGroupFollowRequests()

    return ajaxRender('site/pages/group/group_requests_modal.html',vals,request)


def getGroupInvitedModal(user,request,vals={}):
    # Generate a context for the modal
    vals['group_invites'] = user.getGroupInvites()

    return ajaxRender('site/pages/profile/group_invites_modal.html',vals,request)


def getFollowRequestsModal(user,request,vals={}):
    # Generate a context for the modal
    vals['follow_requests'] = user.getFollowRequests()

    return ajaxRender('site/pages/profile/follow_requests_modal.html',vals,request)


def getFacebookShareModal(fb_share_id,fb_name,request,vals):

#    vals['fb_name'] = fb_name
#    vals['fb_image'] = "https://graph.facebook.com/" + str(fb_share_id) + "/picture?type=large"
#    vals['fb_share_id'] = fb_share_id
#    vals['default_facebook_message'] = DEFAULT_FACEBOOK_MESSAGE
#
#    return ajaxRender('site/pages/friends/facebook_share_modal.html',vals,request)
    return HttpResponseRedirect("http://www.facebook.com/dialog/send?display=popup"+
                                "app_id="+settings.FACEBOOK_APP_ID+"&"+
                                "name=LoveGov&"+
                                "link=http://www.lovegov.com&"+
                                "redirect_uri=http://www.lovegov.com/home")


def getFacebookShareContentModal(share_content,request,vals):

    vals['share_content'] = share_content
    vals['default_facebook_message'] = "Look at this!"

    return ajaxRender('site/pages/feed/feed_items/facebook_share_content_modal.html',vals,request)


def getCreateModal(request,vals={}):
    # From vals, gid is the id of the group that the create modal was clicked from
    # selected_group is the id of the group that should be preselected in the create modal
    main_topics = Topic.objects.filter(Q(alias='general') | Q(topic_text__in=MAIN_TOPICS))
    general_topic = Topic.lg.get(alias='general')
    vals['main_topics'] = main_topics
    vals['general_t'] = general_topic
    from lovegov.frontend.views_helpers import getStateTuples
    getStateTuples(vals)
    viewer = vals['viewer']
    vals['all_polls'] = Poll.objects.all()
    gid = request.POST.get('gid')
    selected_group_id = request.POST.get('selected_group')
    selected_group = Group.lg.get_or_none(id=selected_group_id)
    subscriptions = list(viewer.getSubscriptions())
    if selected_group not in subscriptions:
        subscriptions.append(selected_group)
    vals['selected_group'] = selected_group_id
    vals['viewerSubscriptions'] = subscriptions
    vals['group'] = Group.lg.get_or_none(id=gid)
    return ajaxRender('site/pages/create_modal.html',vals,request)


def getMessagePoliticianModal(politician, request,vals={}):
    vals['politician'] = politician
    return ajaxRender('site/pages/profile/message_politician_modal.html',vals,request)

def getPinContentModal(content,user,request,vals):
    vals['content'] = content

    admin_of_groups = user.admin_of.all()

    pinnable_groups = []

    for group in admin_of_groups:
        if content not in group.pinned_content.all():
            pinnable_groups.append(group)

    vals['groups'] = pinnable_groups

    return ajaxRender('site/pages/content_detail/pin_content_modal.html',vals,request)


def getGroupDescriptionModal(group,request,vals):
    vals['group'] = group
    return ajaxRender('site/pages/group/description_modal.html', vals,request)

def getGroupModeratorsModal(group,request,vals):
    vals['group'] = group
    vals['moderators'] = group.admins.all()
    return ajaxRender('site/pages/group/moderators_modal.html', vals,request)

def getPetitionSignersModal(petition, request, vals):
    vals['petition'] = petition
    return ajaxRender('site/pages/content_detail/petition_signers_modal.html', vals,request)


## add to scorecard ##
def getAddToScorecardModal(scorecard, request, vals):
    vals['scorecard'] = scorecard
    already_ids = scorecard.politicians.all().values_list("id", flat=True)
    vals['politicians'] = UserProfile.objects.filter(politician=True).exclude(id__in=already_ids)
    return ajaxRender('site/pages/content_detail/scorecards/add_to_scorecard_modal.html', vals,request)


## invite someone off lovegov to run for your election ##
def getInviteToRunForModal(election, request, vals):
    vals['election'] = election
    return ajaxRender('site/pages/elections/invite_to_run_for_modal.html', vals,request)


def getAnswerQuestionsWarningModal(request, vals):
    viewer = vals['viewer']
    vals['which'] = request.POST['which']
    lgpoll = getLoveGovPoll()
    poll_progress = lgpoll.getPollProgress(viewer)
    vals['lgpoll'] = lgpoll
    vals['lgpoll_progress'] = poll_progress['completed']
    vals['congress'] = getCongressGroup()
    return ajaxRender('site/pages/dismissible_headers/answer_warning_modal.html', vals,request)

def getFullImageModal(request, vals):
    uid = request.POST.get('uid')
    if uid:
        vals['viewee'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/profile/full_profile_image.html",vals,request)

### get modal with full bio text for profile ###
def getBioModal(request, vals):
    profile = UserProfile.objects.get(id=request.POST['p_id'])
    vals['profile'] = profile
    return ajaxRender("site/pages/profile/bio_modal.html",vals,request)

### forbidden modal ###
def getForbiddenModal(request, vals):
    vals['action'] = request.POST.get('action')
    return ajaxRender("site/pages/modals/forbidden_modal.html",vals,request)

def getUserFollowingModal(request,vals):
    uid = request.POST.get('user')
    vals['u'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/modals/user_following_modal.html",vals,request)

def getFollowingUserModal(request,vals):
    uid = request.POST.get('user')
    vals['u'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/modals/following_user_modal.html",vals,request)

def getUserGroupsModal(request,vals):
    uid = request.POST.get('user')
    vals['u'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/modals/user_groups_modal.html",vals,request)

def getUserSignaturesModal(request,vals):
    uid = request.POST.get('user')
    u = UserProfile.lg.get_or_none(id=uid)
    vals['u'] = u
    vals['petitions'] = u.petitions.all()
    return ajaxRender("site/pages/modals/user_signatures_modal.html",vals,request)

def getUserSupportingModal(request,vals):
    uid = request.POST.get('user')
    vals['u'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/modals/user_supporting_modal.html",vals,request)

def getSupportingUserModal(request,vals):
    uid = request.POST.get('user')
    vals['u'] = UserProfile.lg.get_or_none(id=uid)
    return ajaxRender("site/pages/modals/supporting_user_modal.html",vals,request)
























