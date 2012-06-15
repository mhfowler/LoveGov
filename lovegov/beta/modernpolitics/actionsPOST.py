########################################################################################################################
########################################################################################################################
#
#       ActionsPOST [modify database by post request]
#               - check post
#               - turn post into form
#               - if valid form
#                   - autosave
#                   - [optional case for returning something via json]
#               - else
#                   - return list of error messages via json
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

### INTERNAL ###
from lovegov.beta.modernpolitics import backend
from lovegov.beta.modernpolitics.backend import getUserProfile, getPrivacy
from lovegov.beta.modernpolitics.forms import *

### DJANGO LIBRARIES ###
from django.forms import *
from django import shortcuts
from django.template import RequestContext, loader
from django.utils.datastructures import MultiValueDictKeyError

#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all actions. [checks is post]
# post: actionPOST - which actionPOST to call
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def actionPOST(request, dict={}):
    """Splitter between all actions. [checks is post]"""
    ###### CAN'T UNDERSTAND WHY ######
    user = getUserProfile(request)
    dict['user'] = user
    ###############################
    if request.method =='POST' and request.user:
        action = request.POST['action']
        if action == 'postcomment':
            return comment(request, dict)
        elif action == 'create':
            return create(request, dict)
        elif action == 'invite':
            return invite(request, dict)
        elif action == 'edit':
            return edit(request, dict)
        elif action == 'delete':
            return delete(request, dict)
        elif action == 'setprivacy':
            return setPrivacy(request, dict)
        elif action == 'vote':
            return vote(request, dict)
        elif action == 'hoverComparison':
            return hoverComparison(request,dict)
        elif action == 'sign':
            return sign(request, dict)
        elif action == 'finalize':
            return finalize(request, dict)
        elif action == 'userfollow':
            return userFollowRequest(request, dict)
        elif action == 'followresponse':
            return userFollowResponse(request, dict)
        elif action == 'stopfollow':
            return userFollowStop(request, dict)
        elif action == 'answer':
            return answer(request, dict)
        elif action == 'joingroup':
            return joinGroupRequest(request, dict)
        elif action == 'joinresponse':
            return joinGroupResponse(request, dict)
        elif action == 'leavegroup':
            return leaveGroup(request, dict)
        elif action == 'matchComparison':
            return matchComparison(request,dict)
        ### actions below have not been proof checked ###
        elif action == 'linkfrom':
            return linkfrom(request, dict)
        elif action == 'linkto':
            return linkto(request, dict)
        elif action == 'share':
            return share(request, dict)
        elif action == 'follow':
            return follow(request, dict)
        elif action == 'posttogroup':
            return posttogroup(request)
        elif action == 'deinvolve':
            return deinvolve(request, dict)
        elif action == 'updateCompare':
            return updateCompare(request, dict)
        elif action == 'viewCompare':
            return viewCompare(request, dict)
        elif action == 'answerWeb':
            return answerWeb(request, dict)
        elif action == "debateMessage":
            return debateMessage(request)
        elif action == 'refreshfeed':
            return refreshfeed(request, dict)
        elif action == 'updatefeed':
            return updatefeed(request, dict)
        elif action == 'persistent_vote':
            return persistent_vote(request, dict)
        elif action == 'persistent_message':
            return persistent_message(request, dict)
        elif action == 'persistent_accept':
            return persistent_accept(request, dict)
        elif action == 'persistent_reject':
            return persistent_reject(request, dict)
        elif action == 'feedback':
            return feedback(request,dict)
        elif action == 'updateGroupView':
            return updateGroupView(request, dict)
        elif action == 'invite_to_debate':
            return debateCreateAndInvite(request, dict)
        elif action == 'create_motion':
            return createMotion(request, dict)
        else:
            dict['message'] = "There is no such actionPOST."
            return renderToResponseCSRF('usable/message.html',dict,request)
    elif request.method =='POST':
        action = request.POST['action']
        if action == 'mailingList':
            return addEmailList(request)
        else:
            dict['message'] = "There is no such non-user actionPOST."
            return HttpResponse('No such action')
    else:
        dict['message'] = "This is not a viewable page."
        return renderToResponseCSRF('usable/message.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Creates a piece of content and stores it in database.
# post: depends on type of content
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def create(request, val={}):
    """Creates a piece of content and stores it in database."""
    formtype = request.POST['type']
    user = val['user']
    if formtype == 'P':
        form = CreatePetitionForm(request.POST)
    elif formtype == 'N':
        form = CreateNewsForm(request.POST)
    elif formtype =='E':
        form = CreateEventForm(request.POST)
    elif formtype =='G':
        form = CreateUserGroupForm(request.POST)
    elif formtype =='I':
        form = UserImageForm(request.POST)
        # if valid form, save to db
    if form.is_valid():
        # save new piece of content
        c = form.complete(request)
        # if ajax, return page center
        if request.is_ajax():
            if formtype == "P":
                from lovegov.alpha.splash.views import petitionDetail
                return petitionDetail(request=request,p_id=c.id,dict=val)
            elif formtype == "N":
                from lovegov.alpha.splash.views import newsDetail
                return newsDetail(request=request,n_id=c.id,dict=val)
            elif formtype == "G":
                group_joined = GroupJoined(user=user, group=c, privacy=getPrivacy(request))
                group_joined.confirm()
                group_joined.autoSave()
                c.admins.add(user)
                c.members.add(user)
                action = Action(relationship=c.getCreatedRelationship())
                action.autoSave()
                from lovegov.alpha.splash.views import group
                return HttpResponse( json.dumps( { 'success':True , 'url':c.getUrl() } ) )
        else:
            return shortcuts.redirect('/display/' + str(c.id))
    else:
        if request.is_ajax():
            errors = dict([(k, form.error_class.as_text(v)) for k, v in form.errors.items()])
            vals = {
                    'success':False,
                    'errors':errors,
                }
            print simplejson.dumps(vals)
            return HttpResponse(json.dumps(vals))
        else:
            vals = {'petition': petition, 'event':event, 'news':news, 'group':group, 'album':album}
            return renderToResponseCSRF('usable/create_content_simple.html',vals,request)

#-----------------------------------------------------------------------------------------------------------------------
# Sends invite email and and addds email to valid emails.
#-----------------------------------------------------------------------------------------------------------------------
def invite(request, vals={}):
    email = request.POST['email']
    user_name = vals['user'].get_name()
    description = "invited by: " + user_name
    if not ValidEmail.objects.filter(email=email).exists():
        valid = ValidEmail(email=email, description=description)
        valid.save()
    subject = user_name + " has invited you to join them on LoveGov"
    dictionary = {'user_name':user_name}
    send_email.sendTemplateEmail(subject,'userInvite.html', dictionary,"team@lovegov.com",email)
    return HttpResponse("+")

#-----------------------------------------------------------------------------------------------------------------------
# Signs a petition.
#-----------------------------------------------------------------------------------------------------------------------
def sign(request, vals={}):
    user = vals['user']
    privacy = getPrivacy(request)
    if privacy == 'PUB':
        petition = Petition.objects.get(id=request.POST['c_id'])
        if petition.finalized:
            if petition.sign(user):
                signed = Signed(user=user, content=petition)
                signed.autoSave()
                action = Action(relationship=signed)
                action.autoSave()
                petition.getCreator().notify(action)
                vals['signer'] = user
                context = RequestContext(request,vals)
                template = loader.get_template('deployment/snippets/signer.html')
                signer_string = template.render(context)  # render html snippet
                vals = {"success":True, "signer":signer_string}
            else:
                vals = {"success":False, "error": "You have already signed this petition."}
        else:
            vals = {"success":False, "error": "This petition has not been finalized."}
    else:
        vals = {"success":False, "error": "You must be in public mode to sign a petition."}
    return HttpResponse(json.dumps(vals))

#-----------------------------------------------------------------------------------------------------------------------
# Finalizes a petition.
#-----------------------------------------------------------------------------------------------------------------------
def finalize(request, vals={}):
    user = vals['user']
    petition = Petition.objects.get(id=request.POST['c_id'])
    creator = petition.getCreator()
    if user==creator:
        petition.finalize()
    return HttpResponse("success")


#-----------------------------------------------------------------------------------------------------------------------
# Edit content based on editform.
# post: c_id - id of content to be edited, <field> - value to replace field with
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def edit(request, dict={}):
    """Simple interface for editing content (to be deprecated)"""
    user = dict['user']
    content = Content.objects.get(id=request.POST['c_id'])
    creator = content.getCreator()
    if creator == user:
        # get correct form, and fill with POST data
        form = content.getEditForm(request)
        if form.is_valid():
            # complete (saves changes)
            form.complete(request)
            return shortcuts.redirect(content.get_url())
        else:
            dict = {'form':form}
            return renderToResponseCSRF('forms/contentform.html', dict, request)
    else:
        dict = {'message':'You cannot edit a piece of content you did not create.'}
        return renderToResponseCSRF('usable/message.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Deletes content.
# post: c_id - id of content to be deleted.
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def delete(request, dict={}):
    user = dict['user']
    content = Content.objects.get(id=request.POST['c_id'])
    if user == content.getCreator():
        content.active = False
        content.save()
        deleted = Deleted(user=user, content=content, privacy=getPrivacy(request))
        deleted.autoSave()
        return HttpResponse("successfully deleted content with id:" + request.POST['c_id'])
    else:
        return HttpResponse("you don't have permission")

#-----------------------------------------------------------------------------------------------------------------------
# Saves comment to database from post request.
# post: comment - text of comment, c_id - id of content to be commented on
# cookies: privacy - privacy setting
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------

def comment(request, dict={}):
    """
    Saves comment to database from post request.

    @param request
    @param dict
            - user
    """
    user = dict['user']
    privacy = getPrivacy(request)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(creator=user, privacy=privacy)
        comment.on_content.status += constants.STATUS_COMMENT
        comment.on_content.save()
        # save relationship, action and send notification
        rel = Commented(user=user, content=comment.on_content, comment=comment, privacy=privacy)
        rel.autoSave()
        action = Action(relationship=rel)
        action.autoSave()
        comment.on_content.getCreator().notify(action)
        return HttpResponse("+")
    else:
        if request.is_ajax():
            to_return = {'errors':[]}
            for e in comment_form.errors:
                to_return['errors'] = to_return['errors'].append(e)
            return HttpResponse(simplejson.dumps(to_return))
        else:
            dict = {'message':'Comment post failed'}
            return renderToResponseCSRF('usable/message.html',dict,request)

#-----------------------------------------------------------------------------------------------------------------------
# Sets privacy cookie and redirects to inputted page.
# post: path - current url, mode - new privacy setting
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def setPrivacy(request, dict={}):
    """Sets privacy cookie and redirects to inputted page."""
    path = request.POST['path']
    mode = request.POST['mode']
    response = shortcuts.redirect(path)
    response.set_cookie('privacy',value=mode)
    return response

#-----------------------------------------------------------------------------------------------------------------------
# Likes or dislikes content based on post.
# post: vote - type of vote (like or dislike), c_id - id of content to be voted on
# cookies: privacy - privacy setting
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def vote(request, dict):
    """Likes or dislikes content based on post."""
    user = dict['user']
    privacy = getPrivacy(request)
    content = Content.objects.get(id=request.POST['c_id'])
    vote = request.POST['vote']
    # save vote
    if vote == 'L':
        value = content.like(user=user, privacy=privacy)
    elif vote == 'D':
        value = content.dislike(user=user, privacy=privacy)
    to_return = {'my_vote':value, 'status':content.status}
    return HttpResponse(json.dumps(to_return))
    """
        return HttpResponse("+")
    if content.type == "C":
        return HttpResponse("+")
    else:

    """

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question.
# post: q_id - id of question, choice - value of users answer, explanation - user explanation
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def answer(request, dict={}):
    """ Saves a users answer to a question."""
    user = dict['user']
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = getPrivacy(request)
    my_response = user.getView().responses.filter(question=question)
    # save new response
    if 'choice' in request.POST:
        answer_val = request.POST['choice']
        weight = request.POST['weight']
        explanation = request.POST['explanation']
        user.last_answered = datetime.datetime.now()
        user.save()
        if not my_response:
            response = UserResponse(responder=user,
                question = question,
                answer_val = answer_val,
                weight = weight,
                explanation = explanation)
            response.autoSave(creator=user, privacy=privacy)
            action = Action(relationship=response.getCreatedRelationship())
            action.autoSave()
        # else update old response
        else:
            response = my_response[0]
            user_response = response.userresponse
            user_response.answer_val = answer_val
            user_response.weight = weight
            user_response.explanation = explanation
            # update creation relationship
            user_response.saveEdited(privacy)
            action = Action(relationship=user_response.getCreatedRelationship())
            action.autoSave()
        if request.is_ajax():
            url = response.get_url()
            # get percentage agreed
            agg = backend.getLoveGovGroupView().filter(question=question)
            if agg:
                agg = agg[0].aggregateresponse
                choice = agg.responses.filter(answer_val=int(request.POST['choice']))
                if agg.total:
                    percent_agreed = float(choice[0].tally) / float(agg.total)
                else:
                    percent_agreed = 0
                    # print("total: " + str(agg.total))
            else:
                percent_agreed = 0
            return HttpResponse(simplejson.dumps({'url': url,'answer_avg':percent_agreed}))
        else:
            return shortcuts.redirect(question.get_url())
    else:
        if my_response:
            response = my_response[0]
            response.delete()
        return shortcuts.redirect(question.get_url())

#----------------------------------------------------------------------------------------------------------------------
# Joins group if user is not already a part.
# post: g_id - id of group
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupRequest(request, dict={}):
    """Joins group if user is not already a part."""
    from_user = dict['user']
    group = Group.objects.get(id=request.POST['g_id'])
    #Secret groups and System Groups cannot be join requested
    if group.system:
        return HttpResponse("cannot request to join system group")
    #Get GroupJoined relationship if it exists already
    already = GroupJoined.objects.filter(user=from_user, group=group)
    if already:
        group_joined = already[0]
        if group_joined.confirmed:
            return HttpResponse("you are already a member of group")
    else: #If it doesn't exist, create it
        group_joined = GroupJoined(user=from_user, content=group, group=group, privacy=getPrivacy(request))
        group_joined.autoSave()
    #If the group is privacy secret...
    if group.group_privacy == 'S':
        if group_joined.invited:
            group_joined.confirm()
            group.members.add(from_user)
            action = Action(relationship=group_joined,modifier="D")
            action.autoSave()
            for admin in group.admins.all():
                admin.notify(action)
            return HttpResponse("joined")
        return HttpResponse("cannot request to join secret group")
    #If the group type is open...
    if group.group_privacy == 'O':
        group_joined.confirm()
        group.members.add(from_user)
        action = Action(relationship=group_joined,modifier="D")
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return HttpResponse("joined")
    #If the group type is private and not requested yet
    else: # group.group_privacy == 'P'
        if group_joined.requested and not group_joined.rejected:
            return HttpResponse("you have already requested to join this group")
        group_joined.clear()
        group_joined.request()
        action = Action(relationship=group_joined,modifier='R')
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return HttpResponse("request to join")



#----------------------------------------------------------------------------------------------------------------------
# Confirms or denies GroupJoined, if GroupJoined was requested.
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupResponse(request, dict={}):
    response = request.POST['response']
    from_user = UserProfile.objects.get(id=request.POST['follow_id'])
    group = Group.objects.get(id=request.POST['g_id'])
    already = GroupJoined.objects.filter(user=from_user, group=group)
    if already:
        group_joined = already[0]
        if group_joined.requested:
            if response == 'Y':
                group_joined.confirm()
                group.members.add(from_user)
                action = Action(relationship=group_joined,modifier="D")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("they're now following you")
            elif response == 'N':
                group_joined.reject()
                action = Action(relationship=group_joined,modifier="X")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have rejected their follow request")
        if group_joined.confirmed:
            return HttpResponse("This person is already following you")
    return HttpResponse("this person has not requested to follow you")

#----------------------------------------------------------------------------------------------------------------------
# Requests to follow inputted user.
#-----------------------------------------------------------------------------------------------------------------------
def userFollowRequest(request, dict={}):
    from_user = dict['user']
    to_user = UserProfile.objects.get(id=request.POST['p_id'])
    #No Self Following
    if to_user.id == from_user.id:
        return HttpResponse("you cannot follow yourself")
    already = UserFollow.objects.filter(user=from_user, to_user=to_user)
    #If there's already a follow relationship
    if already: #If it exists, get it
        user_follow = already[0]
        if user_follow.confirmed: #If you're confirmed following already, you're done
            return HttpResponse("you are already following this person")
    else: #If there's no follow relationship, make one
        user_follow = UserFollow(user=from_user, to_user=to_user)
        user_follow.autoSave()
    # If this user is public follow
    if not to_user.private_follow:
        from_user.follow(to_user)
        action = Action(relationship=user_follow,modifier='D')
        action.autoSave()
        to_user.notify(action)
        return HttpResponse("you are now following this person")
    #otherwise, if you've already requested to follow this user, you're done
    elif user_follow.requested and not user_follow.rejected:
        return HttpResponse("you have already requested to follow this person")
    #Otherwise, make the request to follow this user
    else:
        user_follow.clear()
        user_follow.request()
        action = Action(relationship=user_follow,modifier='R')
        action.autoSave()
        to_user.notify(action)
        return HttpResponse("you have requested to follow this person")

#----------------------------------------------------------------------------------------------------------------------
# Confirms or denies user follow, if user follow was requested.
#-----------------------------------------------------------------------------------------------------------------------
def userFollowResponse(request, dict={}):
    to_user = dict['user']
    response = request.POST['response']
    from_user = UserProfile.objects.get(id=request.POST['p_id'])
    already = UserFollow.objects.filter(user=from_user, to_user=to_user)
    if already:
        user_follow = already[0]
        if user_follow.requested:
            if response == 'Y':
                # Create follow relationship!
                from_user.follow(to_user)
                action = Action(relationship=user_follow,modifier='D')
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("they're now following you")
            elif response == 'N':
                user_follow.reject()
                action = Action(relationship=user_follow,modifier='X')
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have rejected their follow request")
        if user_follow.confirmed:
            return HttpResponse("This person is already following you")
    return HttpResponse("this person has not requested to follow you")

#-----------------------------------------------------------------------------------------------------------------------
# Clears userfollow relationship between users.
#-----------------------------------------------------------------------------------------------------------------------
def userFollowStop(request, dict={}):
    """Removes connection between users."""
    from_user = dict['user']
    to_user = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if to_user:
        already = UserFollow.objects.filter(user=from_user, to_user=to_user)
        if not already:
            user_follow = UserFollow(user=from_user, to_user=to_user)
            user_follow.autoSave()
        else:
            user_follow = already[0]
        from_user.unfollow(to_user)
        action = Action(relationship=user_follow,modifier='S')
        action.autoSave()
        to_user.notify(action)
        return HttpResponse("removed")
    return HttpResponse("To User does not exist")


#----------------------------------------------------------------------------------------------------------------------
# Invites inputted user to join group.
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupInvite(request, dict={}):
    """Invites inputted to join group, if inviting user is admin."""
    user = dict['user']
    to_invite = UserProfile.objects.get(id=request.POST['invited_id'])
    group = Group.objects.get(id=request.POST['g_id'])
    admin = group.admins.filter(id=user.id)
    if admin:
        already = GroupJoined.objects.filter(user=to_invite, group=group)
        if already:
            join=already[0]
            if join.invited or join.confirmed:
                return HttpResponse("already invited or already member")
        else:
            join = GroupJoined(user=to_invite, content=group, group=group, privacy=getPrivacy(request))
            join.invite(inviter=user)
    else:
        return HttpResponse("You are not admin.")


#-----------------------------------------------------------------------------------------------------------------------
# Leaves group if user is a member (and does stuff if user would be last admin)
# post: g_id - id of group
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def leaveGroup(request, dict={}):
    """Leaves group if user is a member (and does stuff if user would be last admin)"""
    # if not system then remove
    from_user = dict['user']
    group = Group.objects.get(id=request.POST['g_id'])
    group_joined = GroupJoined.objects.get(group=group, user=from_user)
    if group_joined:
        group_joined.clear()
    if not group.system:
        group.members.remove(from_user)
        group.admins.remove(from_user)
        if not group.admins.all():
            members = list( group.members.all() )
            if not members:
                group.active = False
                group.save()
            for member in members:
                group.admins.add(member)
        action = Action(relationship=group_joined,modifier='S')
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return HttpResponse("left")
    else:
        return HttpResponse("system group")

#-----------------------------------------------------------------------------------------------------------------------
# Sets linkfrom cooke to be posted piece of content.
# post: c_id - id of content to be set as linkfrom
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def linkfrom(request, dict={}):
    """Links content from linkfrom cookie to content in post"""
    response = HttpResponse("linkfrom set")
    response.set_cookie('linkfrom',value=request.POST['c_id'])
    return response

#-----------------------------------------------------------------------------------------------------------------------
# Links content from linkfrom cookie to content in post
# post: c_id - id of content to be linked
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def linkto(request, dict={}):
    """Links content from linkfrom cookie to content in post"""
    # get data
    from_content = Content.objects.get(id=request.COOKIES['linkfrom'])
    to_content= Content.objects.get(id=request.POST['c_id'])
    if Linked.objects.filter(from_content=from_content, to_content=to_content):
        return HttpResponse("already linked")
    else:
        when = datetime.datetime.now()
        link = Linked(from_content_id=from_content.id, to_content_id=to_content.id,when=when,link_strength=1)
        link.save()
        if request.is_ajax():
            to_return = {'from_id':from_content.id}
            return HttpResponse(simplejson.dumps(to_return))
        else:
            return HttpResponse("linked")

#-----------------------------------------------------------------------------------------------------------------------
# Creates share relationship between user and content.
# post: c_id - id of content to be shared
# cookies: privacy - privacy setting
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def share(request, dict={}):
    # get data
    user = dict['user']
    content = Content.objects.get(id=request.POST['c_id'])
    # check if already following
    my_share = Shared.objects.filter(user=user,content=content)
    if not my_share:
        privacy = getPrivacy(request)
        share = Shared(user=user,content=content,privacy=privacy)
        share.autoSave()
        # add to myinvolvement
        user.updateInvolvement(content=content,amount=constants.INVOLVED_FOLLOW)
        # update status of content
        content.status += constants.STATUS_FOLLOW
        content.save()
        return HttpResponse("shared")
    else:
        return HttpResponse("already shared")

#-----------------------------------------------------------------------------------------------------------------------
# Creates follow relationship between user and content.
# post: c_id - id of content to be followed
# cookies: privacy - privacy setting
# args: request
# tags: USABLE
# TODO: how do you stop following? can you set email notifications for things you follow?
#-----------------------------------------------------------------------------------------------------------------------
def follow(request, dict={}):
    # get data
    user = dict['user']
    content = Content.objects.get(id=request.POST['c_id'])
    # check if already following
    my_follow = Followed.objects.filter(user=user,content=content)
    if not my_follow:
        privacy = getPrivacy(request)
        follow = Followed(user=user,content=content,privacy=privacy)
        follow.autoSave()
        # update status of content
        content.status += constants.STATUS_FOLLOW
        content.save()
        return HttpResponse("following")
    else:
        return HttpResponse("already following")

#-----------------------------------------------------------------------------------------------------------------------
# Adds content to group.
# post: c_id - id of content to be followed, g_id - group to be added to
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def posttogroup(request, dict={}):
    """Adds content to group."""
    content_id = request.POST['c_id']
    group_id = request.POST['g_id']
    content = Content.objects.get(id=content_id)
    group = Group.objects.get(id=group_id)
    group.group_content.add(content)
    return HttpResponse("added")

#-----------------------------------------------------------------------------------------------------------------------
# Updates inputted comparison.
# post: c_id (comparison id)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def updateCompare(request, dict={}):
    """Saves a Comparison between the two inputted users."""
    comp = ViewComparison.objects.get(id=request.POST['c_id'])
    comparison = backend.updateComparison(comp)
    return HttpResponse(simplejson.dumps({'url':comparison.get_url()}))

#-----------------------------------------------------------------------------------------------------------------------
# Returns the url of the latest comparison between two users, or creates a comparison between two users and then
# returns url if one does not already exist.
# post: a_id - id of personA, b_id - id of personB
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def viewCompare(request, dict={}):
    """Returns link to comparison between the two inputted users via simplejson/ajax."""
    dict = {'url':'/compare/' + request.POST['a_id'] + '/' +  request.POST['b_id'] + '/'}
    return HttpResponse(simplejson.dumps(dict))


#-----------------------------------------------------------------------------------------------------------------------
# Removes piece of content from users myinvolvement.
# post: c_id - id of content to be removed
# args: request
# tags: USABLE, DEPRECATE
#-----------------------------------------------------------------------------------------------------------------------
def deinvolve(request, dict={}):
    user = dict['user']
    content = Content.objects.get(id=request.POST['c_id'])
    to_remove = user.my_involvement.get(content=content)
    user.my_involvement.remove(to_remove)
    return HttpResponse('removed')

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question from the QAWeb interface
# post: q_id - id of question, choice - value of users answer, explanation - user explanation
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def answerWeb(request, dict={}):
    """ Saves a users answer to a question."""
    user = dict['user']
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = getPrivacy(request)
    # check if already responded
    my_response = UserResponse.objects.filter(responder=user, question=question)
    if not my_response:
        # save new response
        response = UserResponse(responder=user,
            question = question,
            answer_val=request.POST['choice'],
            explanation=request.POST['explanation'])
        response.autoSave()
        # save creation relationship
        response.saveCreated(user, privacy)
    # else update old response
    else:
        # update response
        response = my_response[0]
        response.autoUpdate(answer_val=request.POST['choice'], explanation=request.POST['explanation'])
        # update creation relationship
        response.updateCreated(user, privacy)
        # if ajax return url via simplejson
    if request.is_ajax():
        dict = {'object': response, 'back': request.POST['back']}
        return renderToResponseCSRF('qaweb/display_response.html', dict, request)
    else:
        return shortcuts.redirect(response.get_url)

#-----------------------------------------------------------------------------------------------------------------------
#
# post: q_id - id of question, choice - value of users answer, explanation - user explanation
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def debateMessage(request, dict={}):
    debater = dict['user']
    message = request.POST['message']
    debate = Debate.objects.get(id=request.POST['debateID'])
    debaterSide = (Debaters.objects.get(user=debater, content=debate)).side
    debateMessage = DebateMessage(room=debate, sender=debater, message_type='M', debate_side=debaterSide, message=message)
    debateMessage.save()
    toReturn = model_to_dict(debateMessage)
    toReturn['now'] = debateMessage.timestamp.__str__()
    toReturn['main_image'] = ''
    toReturn['sender'] = debater.first_name
    return HttpResponse(simplejson.dumps(toReturn))

#-----------------------------------------------------------------------------------------------------------------------
# Updates a users feed (doesn't clear it, just regets the best)
# post:
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def updatefeed(request,dict={}):
    user = dict['user']
    backend.updateUserFeed(user)
    return HttpResponse("updated")

#-----------------------------------------------------------------------------------------------------------------------
# Updates a users feed with all new stuff (nothing they've ever seen or was in their feed)
# post:
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def refreshfeed(request,dict={}):
    user = dict['user']
    return HttpResponse("refreshed")

#-----------------------------------------------------------------------------------------------------------------------
# Adds a vote to either affirmative or negative in persistent debate.
# post: d_id (debate id), vote (1 or 0)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def persistent_vote(request, dict={}):
    debate = Persistent.objects.get(id=request.POST['d_id'])
    user = dict['user']
    my_vote = DebateVoted.objects.filter(user=user, content=debate)
    # check if already voted
    if my_vote:
        return HttpResponse("you already voted.")
    else:
        # save new vote
        new_vote = DebateVoted(user=user, value=request.POST['vote'],privacy=getPrivacy(request), content=debate)
        new_vote.autoSave()
        # change vote totals
        vote = int(new_vote.value)
        if vote == 1:
            debate.votes_affirmative += 1
        else: debate.votes_negative += 1
        debate.save()
        return HttpResponse("voted")

#-----------------------------------------------------------------------------------------------------------------------
# Adds a message to persistent debate if correct turn.
# post: d_id (debate id), text (text of message)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def persistent_message(request, dict={}):
    debate = Persistent.objects.get(id=request.POST['d_id'])
    user = dict['user']
    # check debate over
    if debate.debate_finished:
        return HttpResponse("already finished")
    # check correct turn
    correct_turn = False
    if debate.turn_current and debate.affirmative == user:
        correct_turn = True
    elif (not debate.turn_current) and debate.negative == user:
        correct_turn = True
    if correct_turn:
        debate.addMessage(text=request.POST['message'])
        return HttpResponse("message added")
    else:
        return HttpResponse("not your turn or not in debate")

def persistent_update(request, dict):
    debate = Persistent.objects.get(id=request.POST['d_id'])
    debate.update()

#-----------------------------------------------------------------------------------------------------------------------
# Accepts or persistent debate invitation.
# post: d_id (debate id), side (1=affirmative, -1=negative)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def persistent_accept(request,dict={}):
    debate = Persistent.objects.get(id=request.POST['d_id'])
    user = dict['user']
    # check if invited to debate
    invited = debate.possible_users.filter(id=user.id)
    if invited:
        side = int(request.POST['side'])
        if side == 1:
            if not debate.affirmative:
                debate.affirmative = user
                debate.save()
                side_verbose = "affirmative"
            else:
                return HttpResponse("someone is already debating this side")
        elif side == -1:
            if not debate.negative:
                debate.negative = user
                debate.save()
                side_verbose = "negative"
            else:
                return HttpResponse("someone is already debating this side")
        else:
            print "no"
            return HttpResponse('this shouldnt happen')
        # create action, and send notification
        to_user = debate.getCreator()
        action = Action(type='YD', creator=user, privacy=getPrivacy(request),
            with_user=to_user, with_content=debate, must_notify=True)
        action.autoSave()
        return HttpResponse("you are now debating the " + side_verbose)
    else:
        return HttpResponse("request invitation to this debate")

#-----------------------------------------------------------------------------------------------------------------------
# Declines invitation to persistent debate.
# post: d_id (debate id)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def persistent_reject(request,dict={}):
    debate = Persistent.objects.get(id=request.POST['d_id'])
    user = dict['user']
    # check if invited to debate
    invited = debate.possible_users.filter(id=user.id)
    if invited:
        debate.possible_users.remove(user)
        # alert creator that person declined invitation
        to_user = debate.getCreator()
        action = Action(type='ND', creator=user, privacy=getPrivacy(request),
            with_user=to_user, with_content=debate)
        action.autoSave()
        return HttpResponse("you rejected invitation.")
    else:
        return HttpResponse("you weren't invited anyway..")

#-----------------------------------------------------------------------------------------------------------------------
# Saves user feedback to db.
# post: text (feedback text), path (page user made feedback on)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def feedback(request,dict={}):
    def sendFeedbackEmail(text,user):
        dict = {'text':text,'name':name}
        for team_member in constants.TEAM_EMAILS:
            send_email.sendTemplateEmail("LoveGov Feedback",'feedback.html',dict,"team@lovegov.com",team_member)
        return
    user = dict['user']
    page = request.POST['path']
    text = request.POST['text']
    name = request.POST['name']
    feedback = Feedback(user=user,page=page,feedback=text)
    feedback.save()
    thread.start_new_thread(sendFeedbackEmail,(text,name,))
    return HttpResponse("+")

#-----------------------------------------------------------------------------------------------------------------------
# Updates the aggregate view in the db for a particular group of users.
# post: g_id (group id)
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupView(request,dict={}):
    group = Group.objects.get(id=request.POST['g_id'])
    backend.updateGroupView(group)
    return HttpResponse("updated")

#-----------------------------------------------------------------------------------------------------------------------
# Adds content to profile page of user.
# args: request, user, content
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def addContent(request, user, content):
    user.getProfilePage().addContent(content)
    return HttpResponse("added")

#-----------------------------------------------------------------------------------------------------------------------
# Adds politician to profile page of user.
# args: request, user, politician
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def addPolitician(request, user, politician):
    user.getProfilePage().addPolitician(politician)
    return HttpResponse("added")

#-----------------------------------------------------------------------------------------------------------------------
# Adds politician to profile page of user.
# args: request, user, politician
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def debateCreateAndInvite(request, dict={}):
    user = dict['user']
    person = UserProfile.objects.get(id=request.POST['to_invite'])
    debate = Persistent(resolution=request.POST['resolution'], debate_type=request.POST['type'])
    debate.autoSave(creator=user, privacy=getPrivacy(request))
    # add person to possible users
    debate.possible_users.add(person)
    debate.possible_users.add(user)
    # send user notification that they were invited
    join_person = DebateJoined(user=person, content=debate, debate=debate)
    join_person.autoSave()
    join_person.invite(inviter=user)
    join_user = DebateJoined(user=user, content=debate, debate=debate)
    join_user.autoSave()
    join_user.invite(inviter=user)
    # return url of newly created debate
    return HttpResponse(simplejson.dumps({'url':debate.get_url()}))

#-----------------------------------------------------------------------------------------------------------------------
# Creates a motion for a group.
# args: request, user, politician
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def createMotion(request, dict={}):
    user = dict['user']
    group = Group.objects.get(id=request.POST['g_id'])
    if group.hasMember(user):
        title = group.title + ' Motion'
        motion = Motion(title=title, full_text=request.POST['motion_text'], motion_type=request.POST['type'], group=group)
        motion.autoSave(creator=user, privacy=getPrivacy(request))
        return HttpResponse(simplejson.dumps({'url':motion.get_url()}))
    else:
        return HttpResponse("you are not member of group")


#-----------------------------------------------------------------------------------------------------------------------
# Compares the session's user with the provided alias and returns JSON dump of comparison data.
# args: request, user
# POST: alias
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def hoverComparison(request,dict={}):
    user = dict['user']
    alias = request.POST['alias']
    to_compare = UserProfile.objects.get(alias=alias)
    comparison = backend.getUserUserComparison(user, to_compare, force=True)
    return HttpResponse(comparison.toJSON())

########################################################################################################################
########################################################################################################################
#
# Non-User Posts
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Adds e-mail to mailing list
# post: email
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def addEmailList(request):
    email = request.POST['email']
    newEmail = EmailList(email=email)
    newEmail.save()
    return HttpResponse("Success")


def matchComparison(request,dict={}):
    from lovegov.alpha.splash.views import ajaxRender
    def returnComparison(to_compare):
        dict['entity'] = to_compare
        html = ajaxRender('deployment/center/match/match-new-box.html',dict,request)
        return HttpResponse(json.dumps({'html':html}))

    user = dict['user']
    url = request.POST['entity_url'].replace('/','').replace('profile','').replace('network','')
    to_compare = UserProfile.lg.get_or_none(alias=url)
    if to_compare:
        to_compare.comparison = backend.getUserUserComparison(user, to_compare).toJSON()
        return returnComparison(to_compare)
    else:
        to_compare = Group.lg.get_or_none(id=url)
        to_compare.comparison = backend.getUserGroupComparison(user, to_compare).toJSON()
        return returnComparison(to_compare)
