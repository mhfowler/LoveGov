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

    vals['fb_name'] = fb_name
    vals['fb_image'] = "https://graph.facebook.com/" + str(fb_share_id) + "/picture?type=large"
    vals['fb_share_id'] = fb_share_id
    vals['default_facebook_message'] = DEFAULT_FACEBOOK_MESSAGE

    return ajaxRender('site/pages/friends/facebook_share_modal.html',vals,request)


def getCreateModal(request,vals={}):
    getMainTopics(vals)
    from lovegov.frontend.views_helpers import getStateTuples
    getStateTuples(vals)
    viewer = vals['viewer']
    vals['all_polls'] = Poll.objects.all()
    gid = request.POST.get('gid')
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
    return ajaxRender('site/pages/dismissible_header/answer_warning_modal.html', vals,request)