########################################################################################################################
########################################################################################################################
#
#           Modals
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.actions import *

def getGroupInviteModal(group,user):
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
    context = { 'group': group , 'non_member_followers': non_member_followers }

    return render_to_string('site/pages/group/group_invite_modal.html',context)


def getGroupRequestsModal(group,user):
    # Check if the user is an admin
    admins = group.admins.all()
    if user not in admins:
        return render_to_string( 'site/pages/basic_message.html' , { 'basic_message' : 'You are not a moderator for the group: ' + group.title } )

    context = { 'group': group , 'group_requests': group.getFollowRequests() }

    return render_to_string('site/pages/group/group_requests_modal.html',context)