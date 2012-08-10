
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
    user.last_answered = datetime.datetime.now()
    user.save()
    if not my_response:
        response = Response( question = question,
            most_chosen_answer = chosen_answer,
            weight = weight,
            explanation = explanation)
        response.most_chosen_num = 1
        response.total_num = 1
        response.autoSave(creator=user, privacy=privacy)
        action = Action(privacy=privacy,relationship=response.getCreatedRelationship())
        action.autoSave()
    # else update old response
    else:
        response = my_response[0]
        response.most_chosen_answer = chosen_answer
        response.weight = weight
        response.explanation = explanation
        # update creation relationship
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