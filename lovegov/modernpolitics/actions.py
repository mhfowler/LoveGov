
# lovegov
from lovegov.modernpolitics.forms import *
from lovegov.modernpolitics.compare import *
from lovegov.modernpolitics.feed import *
from lovegov.modernpolitics.register import *
from lovegov.modernpolitics.images import *

from haystack.query import SearchQuerySet

# django
from django.utils import simplejson

# python
import urllib2
from bs4 import BeautifulSoup

#----------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------
def answerAction(user, question, my_response, privacy, answer_id, weight, explanation):
    chosen_answer = Answer.lg.get_or_none(id=answer_id)
    if not chosen_answer:
        chosen_answer = None
    user.last_answered = datetime.datetime.now()
    user.save()
    if not my_response:
        response = Response( question = question,
            most_chosen_answer = chosen_answer,
            weight = weight,
            explanation = explanation)
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        response.autoSave(creator=user, privacy=privacy)
        action = Action(privacy=privacy,relationship=response.getCreatedRelationship())
        action.autoSave()
        user.num_answers += 1
        user.save()
    # else update old response
    else:
        response = my_response[0]
        response.most_chosen_answer = chosen_answer
        response.weight = weight
        response.explanation = explanation
        # update creation relationship
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        response.saveEdited(privacy)
        action = Action(privacy=privacy,relationship=response.getCreatedRelationship())
        action.autoSave()
    return response


#-----------------------------------------------------------------------------------------------------------------------
# Likes or dislikes content based on post.
#-----------------------------------------------------------------------------------------------------------------------
def voteAction(vote,user,content,privacy):
    """
    Likes or dislikes content based on vote.
    vote( int , Content ) ==> int
    vote( vote , content ) ==> new value
    """

    if content.type == "M":
        motion = content.downcast()
        if not user in motion.group.members.all():
            return 0

    value = 0
    # save vote
    if vote == 1:
        value = content.like(user=user, privacy=privacy)
    elif vote == -1:
        value = content.dislike(user=user, privacy=privacy)

    return value


def leaveGroupAction(group,user,privacy):
    # Find the group joined relationship
    group_joined = GroupJoined.objects.get(group=group, user=user)
    # If there's a group joined relationship
    if group_joined: # Remove this member from that group
        group.removeMember(user)

        # If you just removed the last admin and this isn't a party
        if not group.admins.all() and not group.group_type == 'P':
            # Make all current users admins
            members = list( group.members.all() )
            if not members:
                group.active = False
                group.save()
            for member in members:
                group.admins.add(member)

        # Make an action object for this action
        action = Action(privacy=privacy,relationship=group_joined,modifier='S')
        action.autoSave()
        # And notify the admins of this action
        for admin in group.admins.all():
            admin.notify(action)


def joinGroupAction(group,user,privacy):
    '''
    Returns either 'joined','requested', or 'failed'
    '''

    #Secret groups and System Groups cannot be join requested
    if group.system:
        LGException('user ID #' + str(user.id) + ' cannot request to join system group ID #' + str(group.id))
        return "failed"

    #Get GroupJoined relationship if it exists already
    group_joined = GroupJoined.lg.get_or_none(user=user, group=group)
    if group_joined:
        if group_joined.confirmed:
            return "joined"
    else: #If it doesn't exist, create it
        group_joined = GroupJoined(user=user, content=group, group=group, privacy=privacy)
        group_joined.autoSave()

    #REGARDLESS OF GROUP PRIVACY: If the user is invited and requests to join, add them.
    if group_joined.invited:
        group.joinMember(user, privacy=privacy)
        action = Action(privacy=privacy,relationship=group_joined,modifier="D")
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return "joined"

    # Othwerise you cannot request hidden group.
    if group.group_privacy == 'S':
        LGException('user ID #' + str(user.id) + ' cannot request to join secret group ID #' + str(group.id))
        return "failed"

    # You can automatically join open groups
    elif group.group_privacy == 'O':
        group.joinMember(user, privacy=privacy)
        action = Action(privacy=privacy,relationship=group_joined,modifier="D")
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return "joined"

    #If the group type is private and not requested yet
    else: # group.group_privacy == 'P'
        if group_joined.requested and not group_joined.rejected: # If there already an active request, do nothing
            return "requested"
        # Otherwise reset the group joined relationship and request to join
        group_joined.clear()
        group_joined.request()
        action = Action(privacy=privacy,relationship=group_joined,modifier='R')
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return "requested"


def userFollowAction(from_user,to_user,privacy):
    '''
        Returns either 'followed','requested', or 'failed'
    '''
    #No Self Following
    if to_user.id == from_user.id:
        LGException("User ID #" + str(from_user.id) + " attempted to follow himself")
        return "failed"

    user_follow = UserFollow.lg.get_or_none(user=from_user, to_user=to_user)
    #If there's already a follow relationship
    if user_follow: #If it exists, get it
        if user_follow.confirmed: #If you're confirmed following already, you're done
            return "followed"
    else: #If there's no follow relationship, make one
        user_follow = UserFollow(user=from_user, to_user=to_user, privacy=privacy)
        user_follow.autoSave()

    # If this user is public follow then follows are automatically confirmed
    if not to_user.private_follow:
        from_user.follow(to_user)
        action = Action(privacy=privacy,relationship=user_follow,modifier='D')
        action.autoSave()
        to_user.notify(action)
        return "followed"

    #otherwise, if you've already requested to follow this user, you're done
    elif user_follow.requested and not user_follow.rejected:
        return "requested"

    #Otherwise, make the request to follow this user
    else:
        user_follow.clear()
        user_follow.request()
        action = Action(privacy=privacy,relationship=user_follow,modifier='R')
        action.autoSave()
        to_user.notify(action)
        return "requested"


def userFollowStopAction(from_user,to_user,privacy):
    from_user.unfollow(to_user)
    user_follow = UserFollow.lg.get_or_none(user=from_user,to_user=to_user)
    if user_follow:
        action = Action(privacy=privacy,relationship=user_follow,modifier='S')
        action.autoSave()
        to_user.notify(action)


## Action for joinGroup Responses ##
## Returns a boolean of whether or not the user is in the group POST action completion ##
def joinGroupResponseAction(group,from_user,response,privacy):
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if not group_joined:
        return False

    if group_joined.confirmed:
        return True

    elif group_joined.requested:
        if response == 'Y':
            group.joinMember(from_user, privacy=privacy)
            action = Action(privacy=privacy,relationship=group_joined,modifier="A")
            action.autoSave()
            from_user.notify(action)
            return True

        elif response == 'N':
            group_joined.reject()
            action = Action(privacy=privacy,relationship=group_joined,modifier="X")
            action.autoSave()
            from_user.notify(action)
            return False

    else:
        return False


## Action for group invite Responses ##
## Returns a boolean of whether or not the user is in the group POST action completion ##
def groupInviteResponseAction(group,from_user,response,privacy):
    # Find any groupJoined objects that exist
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if not group_joined: # If there are any
        LGException("User #" + str(from_user.id) + " attempted to respond to a nonexistant group invite to group #" + str(group.id) )
        return False

    if group_joined.confirmed:
        return True

    if group_joined.invited:
        if response == 'Y':
            group.joinMember(from_user, privacy=privacy)
            action = Action(privacy=privacy,relationship=group_joined,modifier="D")
            action.autoSave()
            for admin in group.admins.all():
                admin.notify(action)
            return True

        elif response == 'N':
            group_joined.decline()
            action = Action(privacy=privacy,relationship=group_joined,modifier="N")
            action.autoSave()
            for admin in group.admins.all():
                admin.notify(action)
            return False

    else:
        LGException("User #" + str(from_user.id) + " attempted to respond to a group invite to group #" + str(group.id) + " when they were never invited." )
        return False



## Action for sending a group invite ##
## Returns a boolean of whether or not the user is invited or added to the group POST action completion ##
def groupInviteAction(from_user,group,inviter,privacy):
    # Find any groupJoined objects that exist
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if group_joined: # If there are any

        if group_joined.confirmed:
            return True

        elif group_joined.invited:
            return True

        elif group_joined.requested:
            group.joinMember(from_user, privacy=privacy)
            action = Action(privacy=privacy,relationship=group_joined,modifier="D")
            action.autoSave()
            from_user.notify(action)
            return True
    else:
        group_joined = GroupJoined(user=from_user, group=group, privacy=getPrivacy(request))
        group_joined.autoSave()

    group_joined.invite(inviter)
    action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="I")
    action.autoSave()
    from_user.notify(action)
    return True