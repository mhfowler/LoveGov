########################################################################################################################
########################################################################################################################
#
#           Modals
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.actions import *

def getGroupInviteModal(group,user,vals={}):
    # Check if the user is an admin
    admins = group.admins.all()
    if user not in admins:
        return render_to_string( 'site/pages/basic_message.html' , { 'basic_message' : 'You are not a moderator for the group: ' + group.title } )

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

    return render_to_string('site/pages/group/group_invite_modal.html',vals)


def getGroupRequestsModal(group,user,vals={}):
    # Check if the user is an admin
    admins = group.admins.all()
    if user not in admins:
        return render_to_string( 'site/pages/basic_message.html' , { 'basic_message' : 'You are not a moderator for the group: ' + group.title } )

    # Generate a context for the modal
    vals['group'] = group
    vals['group_requests'] = group.getGroupFollowRequests()

    return render_to_string('site/pages/group/group_requests_modal.html',vals)


def getGroupInvitedModal(user,vals={}):
    # Generate a context for the modal
    vals['group_invites'] = user.getGroupInvites()

    return render_to_string('site/pages/profile/group_invites_modal.html',vals)


def getFollowRequestsModal(user,vals={}):
    # Generate a context for the modal
    vals['follow_requests'] = user.getFollowRequests()

    return render_to_string('site/pages/profile/follow_requests_modal.html',vals)


def getFacebookShareModal(fb_share_id,fb_name,vals):

    vals['fb_name'] = fb_name
    vals['fb_image'] = "https://graph.facebook.com/" + str(fb_share_id) + "/picture?type=large"
    vals['fb_share_id'] = fb_share_id
    vals['default_facebook_message'] = DEFAULT_FACEBOOK_MESSAGE

    return render_to_string('site/pages/friends/facebook_share_modal.html',vals)