
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
def answerAction(user, question, privacy, answer_id, weight=-1, explanation=None):
    chosen_answer = Answer.lg.get_or_none(id=answer_id)
    if not chosen_answer:
        chosen_answer = None
    user.last_answered = datetime.datetime.now()
    user.save()

    view = user.view
    my_response = view.responses.filter(question=question)

    if not my_response:
        if weight == -1:
            weight = 50
        if not explanation:
            explanation = ""
        if question.answers.count() != 2:
            weight = 0
        response = Response( question = question,
            most_chosen_answer = chosen_answer,
            weight = weight
            )
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        else:
            response.most_chosen_num = 0
            response.total_num = 0
        response.autoSave(creator=user, privacy=privacy)
        response.addExplanation(explanation)
        view.responses.add(response)
        user.num_answers += 1
        user.upvotes += 1
        user.save()
        user.makeStale(question)
        question = response.question
        question.num_responses += 1
        question.save()
    # else update old response
    else:
        response = my_response[0]
        if weight == -1:
            weight = response.weight
        if not explanation:
            explanation = response.explanation
        response.most_chosen_answer = chosen_answer
        response.weight = weight
        response.editExplanation(explanation)
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        else:
            response.most_chosen_num = 0
            response.total_num = 0
        response.edited_when = datetime.datetime.now()
        response.saveEdited(privacy)

    # if just reached number of answers of threshold, start computing like-minded group and congress comparison
    if user.num_answers >= QUESTIONS_THRESHOLD:
        user.addBackgroundTask("L")

    return response


def scorecardAnswerAction(user, scorecard, question, answer_id):

    chosen_answer = Answer.lg.get_or_none(id=answer_id)
    if not chosen_answer:
        chosen_answer = None
    scorecard.last_answered = datetime.datetime.now()
    scorecard.save()

    scorecard_view = scorecard.scorecard_view
    my_response = scorecard_view.responses.filter(question=question)

    weight = 50
    explanation = ""

    if not my_response:
        response = Response( question = question,
            most_chosen_answer = chosen_answer,
            weight = weight,
            explanation = explanation)
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        response.autoSave(creator=user, privacy="PRI")
        scorecard_view.responses.add(response)
    # else update old response
    else:
        response = my_response[0]
        if not weight:
            weight = response.weight
        if not explanation:
            explanation = response.explanation
        response.most_chosen_answer = chosen_answer
        response.weight = weight
        response.explanation = explanation
        if chosen_answer:
            response.most_chosen_num = 1
            response.total_num = 1
        response.saveEdited("PRI")

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
    else:
        value = content.unvote(user=user, privacy=privacy)

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
        action = GroupJoinedAction(user=user,privacy=privacy,group_joined=group_joined,modifier='S')
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
        action = GroupJoinedAction(user=user,privacy=privacy,group_joined=group_joined,modifier="F")
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
        action = GroupJoinedAction(user=user,privacy=privacy,group_joined=group_joined,modifier="F")
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
        action = GroupJoinedAction(user=user,privacy=privacy,group_joined=group_joined,modifier='R')
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
        action = UserFollowAction(user=from_user,privacy=privacy,user_follow=user_follow,modifier='F')
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
        action = UserFollowAction(user=from_user,privacy=privacy,user_follow=user_follow,modifier='R')
        action.autoSave()
        to_user.notify(action)
        return "requested"


def userFollowStopAction(from_user,to_user,privacy):
    from_user.unfollow(to_user)
    user_follow = UserFollow.lg.get_or_none(user=from_user,to_user=to_user)
    if user_follow:
        action = UserFollowAction(user=from_user,privacy=privacy,user_follow=user_follow,modifier='S')
        action.autoSave()
        to_user.notify(action)


## Action for joinGroup Responses ##
## Returns a boolean of whether or not the user is in the group POST action completion ##
def joinGroupResponseAction(group,from_user,response,responder,privacy):
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if not group_joined:
        return False

    if group_joined.confirmed:
        return True

    elif group_joined.requested:
        if response == 'Y':
            group.joinMember(from_user, privacy=privacy)
            action = GroupJoinedAction(user=responder,privacy=privacy,group_joined=group_joined,modifier="A")
            action.autoSave()
            from_user.notify(action)
            return True

        elif response == 'N':
            group_joined.reject()
            action = GroupJoinedAction(user=responder,privacy=privacy,group_joined=group_joined,modifier="X")
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
            action = GroupJoinedAction(user=from_user,privacy=privacy,group_joined=group_joined,modifier="F")
            action.autoSave()
            for admin in group.admins.all():
                admin.notify(action)
            return True

        elif response == 'N':
            group_joined.decline()
            action = GroupJoinedAction(user=from_user,privacy=privacy,group_joined=group_joined,modifier="N")
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
            group_joined.invite(inviter)
            return True

        elif group_joined.requested:
            group.joinMember(from_user, privacy=privacy)
            action = GroupJoinedAction(user=inviter,privacy=privacy,group_joined=group_joined,modifier="F")
            action.autoSave()
            from_user.notify(action)
            return True

    else:
        group_joined = GroupJoined(user=from_user, group=group, privacy=privacy)
        group_joined.autoSave()

    group_joined.invite(inviter)
    action = GroupJoinedAction(user=inviter,privacy=privacy,group_joined=group_joined,modifier="I")
    action.autoSave()
    from_user.notify(action)
    return True



## Action for responding to a follow request ##
## Returns a boolean of whether or not the from_user is following the to_user when the function is finished ##
def userFollowResponseAction(from_user,to_user,response,privacy):
    user_follow = UserFollow.lg.get_or_none(user=from_user, to_user=to_user)

    if not user_follow:
        LGException( "User ID #" + str(to_user.id) + " has responded to a follow request with a non-existant UserFollow from " + str(from_user.id) )
        return False

    if user_follow.requested:
        if response == 'Y':
            # Create follow relationship!
            from_user.follow(to_user)
            action = UserFollowAction(user=to_user,privacy=privacy,user_follow=user_follow,modifier='A')
            action.autoSave()
            from_user.notify(action)
            return True
        elif response == 'N':
            user_follow.reject()
            action = UserFollowAction(user=to_user,privacy=privacy,user_follow=user_follow,modifier='X')
            action.autoSave()
            from_user.notify(action)
            return False

    elif user_follow.confirmed:
        LGException( "User ID #" + str(to_user.id) + " has responded to a UserFollow that was already confirmed from " + str(from_user.id) )
        return True

    else:
        LGException( "User ID #" + str(to_user.id) + " has responded to a UserFollow that was not requested from " + str(from_user.id) )
        return False


## Action causes user to support or unsupport inputted politician, support is true or false, depending on whether to start or stop ##
def supportAction(viewer, politician, support, privacy):
    if politician.politician:
        # relationship
        support_relationship = Supported.lg.get_or_none(user=viewer, to_user=politician)
        change = False
        if not support_relationship:
            support_relationship = Supported(user=viewer, to_user=politician)
            support_relationship.autoSave()
            if support:
                politician.num_supporters += 1
                politician.upvotes += 1
                politician.save()
                change = True
        else:
            if support and not support_relationship.confirmed:
                politician.num_supporters += 1
                politician.upvotes += 1
                politician.save()
                change = True
            if not support and support_relationship.confirmed:
                politician.num_supporters -= 1
                politician.upvotes -= 1
                politician.save()
                change = True
            support_relationship.confirmed = support
            support_relationship.privacy = privacy
            support_relationship.save()
        # action
        if support:
            modifier = "A"
        else:
            modifier = "S"
        if change:
            action = SupportedAction(user=viewer,privacy=privacy,support=support_relationship,modifier=modifier)
            action.autoSave()
            # notification
            politician.notify(action)

## Action causes user to follow or unfollow inputted group, follow is true or false, depending on whether to start or stop ##
def followGroupAction(viewer, group, follow, privacy):
    if group.subscribable:
        # action and add or remove from many to many
        change = False
        if follow:
            modifier = "A"
            if group.id not in viewer.group_subscriptions.all().values_list("id", flat=True):
                viewer.group_subscriptions.add(group)
                group.num_followers += 1
                group.save()
                change = True
                group.setNewContentSeen(viewer)
        else:
            modifier = "S"
            if group.id in viewer.group_subscriptions.all().values_list("id", flat=True):
                viewer.group_subscriptions.remove(group)
                group.num_followers -= 1
                group.save()
                change = True
        if change:
            action = GroupFollowAction(user=viewer,privacy=privacy,group=group,modifier=modifier)
            action.autoSave()


## content gets pinned to group, if viewer is admin of group and content not already pinned ##
def pinContentAction(viewer, content, group, privacy):
    if group.hasAdmin(viewer):
        if not content in group.pinned_content.all():
            group.pinned_content.add(content)
            pinned_action = PinnedAction(user=viewer, privacy=privacy, to_group=group, content=content, confirmed=True)
            pinned_action.autoSave()
            return True
        else:
            LGException("user " + str(viewer.id) + " tried to pin content to group which content was already pinned to. g_id:" + str(group.id) )
            return False
    else:
        LGException("user " + str(viewer.id) + " tried to pin content to group they were not admin of. g_id:" + str(group.id) )
        return False

## content gets unpinned from group, if viewer is admin of group and content was previously pinned ##
def unpinContentAction(viewer, content, group, privacy):
    if group.hasAdmin(viewer):
        if content in group.pinned_content.all():
            group.pinned_content.remove(content)
            pinned_action = PinnedAction(user=viewer, privacy=privacy, to_group=group, content=content, confirmed=False)
            pinned_action.autoSave()
            return True
        else:
            LGException("user " + str(viewer.id) + " tried to unpin content from group which content was not pinned to. g_id:" + str(group.id) )
            return False
    else:
        LGException("user " + str(viewer.id) + " tried to unpin content from group they were not admin of. g_id:" + str(group.id) )
        return False



## run for or stop running for an election ##
def runForElectionAction(viewer, election, run):
    if run:
        if not election.system:
            election.joinRace(viewer)
            LGException("user " + str(viewer.id) + " tried to run for an invited only election. e_id:" + str(election.id) )
    else:
        election.leaveRace(viewer)
    return election