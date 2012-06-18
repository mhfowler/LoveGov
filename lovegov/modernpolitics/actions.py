########################################################################################################################
########################################################################################################################
#
#           Actions
#
#
########################################################################################################################
########################################################################################################################

# lovegov
from lovegov.modernpolitics.defaults import *
from lovegov.modernpolitics.forms import *
from lovegov.modernpolitics.compare import *
from lovegov.modernpolitics.feed import *
from lovegov.modernpolitics.images import *
from haystack.query import SearchQuerySet

# django
from django.utils import simplejson

# python
import urllib2
from googlemaps import GoogleMaps

#-----------------------------------------------------------------------------------------------------------------------
# Takes URL and retrieves HTML.  Parses HTML and extracts title and description metadata.  Also takes a picture
# snapshot of the website.
#-----------------------------------------------------------------------------------------------------------------------
PREFIX_ITERATIONS = ["","http://","http://www."]
def getLinkInfo(request, dict={}):
    url = str(request.POST['url'])
    url.strip()
    # url may not be well formed so try variations until one works
    for prefix in PREFIX_ITERATIONS:
        try:
            URL = prefix + url
            html = urllib2.urlopen(URL,data=None).fp.read()
            if html: break
        except ValueError:
            continue
    if html and URL:
        soup = BeautifulStoneSoup(html,selfClosingTags=['img'])
        dict = {}
        try:
            dict['title'] = soup.title.string
        except:
            dict['title'] = "No Title"
        try:
            dict['description'] = soup.findAll(attrs={"name":"description"})[0]['content']
        except:
            dict['description'] = "No Description"
        try:
            image_refs = soup.findAll("img")
            list = []
            first_image = None

            for num in range(0,len(image_refs)):
                try:
                    img_url = image_refs[num]['src']
                    if num == 0:
                        first_image = downloadImage(img_url=img_url,url=URL,min_size=1)
                    elif len(list) == 3:
                        break
                    else:
                        toAdd = downloadImage(img_url=img_url,url=URL)
                        if toAdd: list.append(toAdd)
                except:
                    continue

            list.sort(key=lambda img:img['size'],reverse=True)

            try:
                for imageobj in list:
                    imageobj['path'] = resizeImage(imageobj['path'])
            except:
                pass

            if len(list) == 0 and (first_image is not None or first_image is not False):
                first_image['path'] = resizeImage(first_image['path'])
                list.append(first_image)

            if len(list) == 0:
                list.append({'path':"/static/images/top-logo-default.png"})

            dict['imglink'] = list
            html = ajaxRender('deployment/snippets/news-autogen.html', dict, request)
            return HttpResponse(json.dumps({'html':html,'imglink':list}))

        except:
            return HttpResponse(json.dumps({'html':"exception",'imglink':[{'path':"/static/images/top-logo-default.png"}]}))

#-----------------------------------------------------------------------------------------------------------------------
# Takes address and/or zip code, finds a geolocation from Google Maps, finds congressional district, POSTs congressmen,
# generates comparisons, and returns HTML back to user
#-----------------------------------------------------------------------------------------------------------------------
def getCongressmen(request, dict={}):
    # POST variables from POST request and formats data
    user = dict['user']
    address = request.POST['address']
    zip = request.POST['zip']
    if zip is None: zip = ""
    if address is None: address= ""

    # Load from database if we have this address or zip code stored already
    if address != "" and zip != "" and UserPhysicalAddress.objects.filter(Q(address_string=address)&Q(zip=zip)).exists():
        address = UserPhysicalAddress.objects.filter(Q(address_string=address)&Q(zip=zip))[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    elif address == "" and zip != "" and UserPhysicalAddress.objects.filter(Q(zip=zip)).exists():
        address = UserPhysicalAddress.objects.filter(zip=zip)[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    elif address != "" and zip == "" and UserPhysicalAddress.objects.filter(Q(address_string=address)).exists():
        address = UserPhysicalAddress.objects.filter(address_string=address)[0]
        coordinates = (address.latitude,address.longitude)
        state_district = [{'state':address.state,'number':address.district}]
    else: # Load from Google Maps and Sunlight if we don't have this address or zip code stored
        if address== "" and zip != "": address=zip
        gmaps = GoogleMaps(GOOGLEMAPS_API_KEY)
        coordinates = gmaps.address_to_latlng(address)
        state_district = sunlight.congress.districts_for_lat_lon(coordinates[0],coordinates[1])
        try:
            address = UserPhysicalAddress(user=user.id,address_string=address,zip=zip,latitude=coordinates[0],longitude=coordinates[1],state=state_district[0]['state'],district=state_district[0]['number'])
            address.save()
        except:
            pass
    user.userAddress = address
    user.save()
    # Get congressmen objects and generate comparisons
    congressmen = []
    for s_d in state_district:
        representative = Representative.objects.get(congresssessions=112,state=s_d['state'],district=s_d['number'])
        representative.json = getUserUserComparison(user,representative).toJSON()
        congressmen.append(representative)
    senators = Senator.objects.filter(congresssessions=112,state=state_district[0]['state'])
    for senator in senators:
        senator.json = getUserUserComparison(user,senator).toJSON()
        congressmen.append(senator)

    # Generate HTML and send back HTML to user via ajax
    dict['userProfile'] = user
    dict['congressmen'] = congressmen
    dict['state'] = state_district[0]['state']
    dict['district'] = state_district[0]['number']
    dict['latitude'] = coordinates[0]
    dict['longitude'] = coordinates[1]
    html = ajaxRender('deployment/snippets/match-compare-div.html', dict, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# Returns json of list of results which match inputted 'term'. For jquery autocomplete.
#
#-----------------------------------------------------------------------------------------------------------------------
def searchAutoComplete(request,dict={},limit=5):
    string = request.POST['string'].lstrip().rstrip()
    userProfiles = SearchQuerySet().models(UserProfile).autocomplete(content_auto=string)
    dict['userProfiles'] = [userProfile.object for userProfile in userProfiles][:limit]
    html = ajaxRender('deployment/pieces/autocomplete.html', dict, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# Loads members.
#
#-----------------------------------------------------------------------------------------------------------------------
def loadGroupUsers(request,dict={}):
    user = dict['user']
    num = int(request.POST['histogram_displayed_num'])
    histogram_topic = request.POST['histogram_topic']
    histogram_block = int(request.POST['histogram_block'])
    group = Group.objects.get(id=request.POST['group_id'])
    print 'topic: ' + histogram_topic
    print 'block: ' + str(histogram_block)
    next_num = num + 25
    all_members = group.getMembers(user, block=histogram_block, topic_alias=histogram_topic)
    if len(all_members) >= next_num or not num:
        more_members = all_members[num:next_num]
    else:
        more_members = []
    for x in more_members:
        print x.get_name()
    html = ""
    dict['defaultImage'] = getDefaultImage().image
    for member in more_members:
        dict['member'] = member
        html += ajaxRender('deployment/snippets/group-member.div.html',dict,request)
    return HttpResponse(json.dumps({'html':html,'num':next_num}))

#-----------------------------------------------------------------------------------------------------------------------
# Loads histogram data.
#
#-----------------------------------------------------------------------------------------------------------------------
def loadHistogram(request, dict={}):
    user = dict['user']
    group = Group.objects.get(id=request.POST['group_id'])
    histogram_topic = request.POST['histogram_topic']
    dict['histogram'] = group.getComparisonHistogram(user, topic_alias=histogram_topic, resolution=HISTOGRAM_RESOLUTION)
    html = ajaxRender('deployment/pieces/histogram.html', dict, request)
    to_return = {'html':html}
    return HttpResponse(json.dumps(to_return))


#-----------------------------------------------------------------------------------------------------------------------
# Creates a piece of content and stores it in database.
#
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
                from lovegov.frontend.views import petitionDetail
                return petitionDetail(request=request,p_id=c.id,dict=val)
            elif formtype == "N":
                from lovegov.frontend.views import newsDetail
                return newsDetail(request=request,n_id=c.id,dict=val)
            elif formtype == "G":
                group_joined = GroupJoined(user=user, content=c, group=c, privacy=getPrivacy(request))
                group_joined.confirm()
                group_joined.autoSave()
                c.admins.add(user)
                c.members.add(user)
                action = Action(relationship=c.getCreatedRelationship())
                action.autoSave()
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
        petition = Petition.lg.get_or_none(id=request.POST['c_id'])
        if not petition:
            return HttpResponse("This petition does not exist")
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
#
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
#
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
#
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
        comment.on_content.status += STATUS_COMMENT
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
#
#-----------------------------------------------------------------------------------------------------------------------
def setPrivacy(request, dict={}):
    """Sets privacy cookie and redirects to inputted page."""
    path = request.POST['path']
    mode = request.POST['mode']
    response = shortcuts.redirect(path)
    response.set_cookie('privacy',value=mode)
    return response

#-----------------------------------------------------------------------------------------------------------------------
# Sets privacy cookie and redirects to inputted page.
#
#-----------------------------------------------------------------------------------------------------------------------
def setFollowPrivacy(request, dict={}):
    user = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if not user:
        return HttpResponse("User does not exist")
    if not request.POST['private_follow']:
        return HttpResponse("No user follow privacy specified")
    user.private_follow = request.POST['private_follow']
    user.save()
    return HttpResponse("Follow privacy set")


#-----------------------------------------------------------------------------------------------------------------------
# Likes or dislikes content based on post.
#
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

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question.
#
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
            agg = getLoveGovGroupView().filter(question=question)
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
#
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
#
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
#
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
# Creates share relationship between user and content.
#
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
        user.updateInvolvement(content=content,amount=INVOLVED_FOLLOW)
        # update status of content
        content.status += STATUS_FOLLOW
        content.save()
        return HttpResponse("shared")
    else:
        return HttpResponse("already shared")

#-----------------------------------------------------------------------------------------------------------------------
# Creates follow relationship between user and content.
#
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
        content.status += STATUS_FOLLOW
        content.save()
        return HttpResponse("following")
    else:
        return HttpResponse("already following")

#-----------------------------------------------------------------------------------------------------------------------
# Adds content to group.
#
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
#
#-----------------------------------------------------------------------------------------------------------------------
def updateCompare(request, dict={}):
    """Saves a Comparison between the two inputted users."""
    comp = ViewComparison.objects.get(id=request.POST['c_id'])
    comparison = updateComparison(comp)
    return HttpResponse(simplejson.dumps({'url':comparison.get_url()}))

#-----------------------------------------------------------------------------------------------------------------------
# Returns the url of the latest comparison between two users, or creates a comparison between two users and then
#
#-----------------------------------------------------------------------------------------------------------------------
def viewCompare(request, dict={}):
    """Returns link to comparison between the two inputted users via simplejson/ajax."""
    dict = {'url':'/compare/' + request.POST['a_id'] + '/' +  request.POST['b_id'] + '/'}
    return HttpResponse(simplejson.dumps(dict))

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question from the QAWeb interface
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
# Saves user feedback to db.
#-----------------------------------------------------------------------------------------------------------------------
def feedback(request,dict={}):
    def sendFeedbackEmail(text,user):
        dict = {'text':text,'name':name}
        for team_member in TEAM_EMAILS:
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
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupView(request,dict={}):
    group = Group.objects.get(id=request.POST['g_id'])
    updateGroupView(group)
    return HttpResponse("updated")

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
    comparison = getUserUserComparison(user, to_compare, force=True)
    return HttpResponse(comparison.toJSON())


#-----------------------------------------------------------------------------------------------------------------------
# Adds e-mail to mailing list
#-----------------------------------------------------------------------------------------------------------------------
def addEmailList(request):
    email = request.POST['email']
    newEmail = EmailList(email=email)
    newEmail.save()
    return HttpResponse("Success")

#-----------------------------------------------------------------------------------------------------------------------
# returns match of user
#-----------------------------------------------------------------------------------------------------------------------
def matchComparison(request,dict={}):
    user = dict['user']
    object = urlToObject(request.POST['entity_url'])

    if object.type == "U": object.compare = getUserUserComparison(user, object).toJSON()
    elif object.type == "G": object.compare = getUserGroupComparison(user, object).toJSON()
    else: object.compare =  getUserContentComparison(user, object).toJSON()

    dict['entity'] = object
    html = ajaxRender('deployment/center/match/match-new-box.html',dict,request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# returns more feed items
#-----------------------------------------------------------------------------------------------------------------------
def ajaxFeed(request, dict={}):
    if request.method == 'POST':
        user = dict['user']
        feed_type = request.POST['feed_type']
        start = int(request.POST['start'])
        how_many = int(request.POST['how_many'])
        json_data = request.POST['topics']
        topic_aliases = json.loads(json_data)
        stop = start + how_many
        if topic_aliases:
            topics = Topic.objects.filter(alias__in=topic_aliases)
            content = Content.objects.filter(Q(type='P') | Q(type='N'))
            content = content.filter(main_topic__in=topics)
        else:
            content = Content.objects.filter(Q(type='P') | Q(type='N'))
        if feed_type == 'N':
            feed = latest(user, start, stop, content)
        elif feed_type == 'B':
            feed = greatest(user, start, stop, content)
        else:
            if not topic_aliases:
                feed = feedHelper(user, feed_type, start, stop)
            else:
                print ("check it: " + str(topics))
                feed = feedHelper(user, feed_type, start, stop, topics)
        dict['feed'] = feed
        position = start + len(feed)
        dict['defaultImage'] = getDefaultImage().image
        context = RequestContext(request,dict)
        template = loader.get_template('deployment/snippets/feed_helper.html')
        feed_string = template.render(context)  # render comment html
        to_return = {'feed':feed_string, 'position':position}
        return HttpResponse(json.dumps(to_return))
    else:
        return HttpResponse("not a real page")

#-----------------------------------------------------------------------------------------------------------------------
# reloads html for thread
#-----------------------------------------------------------------------------------------------------------------------
def ajaxThread(request, dict={}):
    from lovegov.frontend.views import makeThread
    content = Content.objects.get(id=request.POST['c_id'])
    user = dict['user']
    thread = makeThread(request, content, user)
    to_return = {'html':thread}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# gets feed using inputted post parameters
#-----------------------------------------------------------------------------------------------------------------------
def ajaxGetFeed(request, dict={}):

    feed_ranking = request.POST['feed_ranking']
    feed_topics = json.loads(request.POST['feed_topics'])
    feed_types = json.loads(request.POST['feed_types'])
    feed_groups = json.loads(request.POST['feed_groups'])
    feed_just = bool(request.POST['feed_just'])
    feed_start = int(request.POST['feed_start'])
    feed_end = int(request.POST['feed_end'])
    feed_display = request.POST['feed_display']

    filter = {
        'topics': feed_topics,
        'types': feed_types,
        'groups': feed_groups,
        'ranking': feed_ranking,
        'just_created_by_group': feed_just
    }

    content = getFeed(filter, start=feed_start, stop=feed_end)
    vals = {'content':content}
    if feed_display == 'pinterest':
        html = ajaxRender('test/pinterest.html', vals, request)
    else:
        html = ajaxRender('test/linear.html', vals, request)
    to_return = {'html':html, 'num':len(content)}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# gets dropdown notifications
#-----------------------------------------------------------------------------------------------------------------------
def getDropdownNotifications(request, dict={}):
    # Get Notifications
    user = dict['user']
    notifications = user.getNotifications(5,dropdown=True)
    notifications_text = []
    for notification in notifications:
        from_you = False
        to_you = False
        n_action = notification.action
        relationship = n_action.relationship
        if relationship.getFrom().id == user.id:
            from_you = True
        elif relationship.getTo().id == user.id:
            to_you = True
        notifications_text.append( n_action.getVerbose(from_you=from_you,to_you=to_you,notification=True) )
    dict['notifications_text'] = notifications_text
    html = ajaxRender('deployment/pieces/notifications_dropdown.html', dict, request)
    return HttpResponse(json.dumps({'html':html}))


def matchSection(request, dict={}):
    section = request.POST['section']
    dict['defaultImage'] = getDefaultImage().image
    if section == 'election':
        user = dict['user']
        c1 = UserProfile.objects.get(first_name="Barack", last_name="Obama")
        c2 = UserProfile.objects.get(first_name="Mitt",last_name="Romney")

        list = [c1,c2]
        for c in list:
            comparison = getUserUserComparison(user,c)
            c.compare = comparison.toJSON()
            c.result = comparison.result
        dict['c1'] = c1
        dict['c2'] = c2

        # dict['user'] doesn't translate well in the template
        dict['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-election-center.html', dict, request)

    elif section == 'social':
        user = dict['user']
        comparison = getUserUserComparison(user,user)
        user.compare = comparison.toJSON()
        user.result = comparison.result
        dict['c1'] = user

        # friends
        dict['friends'] = user.getIFollow()[0:5]

        # groups
        dict['groups'] = user.getGroups()

        # networks
        lovegov = getLoveGovUser()
        network = user.getNetwork()
        congress = getCongressNetwork()
        dict['networks'] = [network,congress,lovegov]

        dict['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-social-network.html', dict, request)

    elif section == 'cause':
        user = dict['user']
        comparison = getUserUserComparison(user,user)
        user.compare = comparison.toJSON()
        user.result = comparison.result
        dict['c1'] = user

        # friends
        dict['friends'] = user.getIFollow()[0:5]

        # groups
        dict['groups'] = user.getGroups()

        # networks
        lovegov = getLoveGovUser()
        network = user.getNetwork()
        congress = getCongressNetwork()
        dict['networks'] = [network,congress,lovegov]

        dict['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-social-network.html', dict, request)

    return HttpResponse(json.dumps({'html':html}))

########################################################################################################################
########################################################################################################################
#
#       Switcher for the actual action.
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Dictionary of callabe functions.
#-----------------------------------------------------------------------------------------------------------------------
actions = { 'getLinkInfo': getLinkInfo,
            'postCongressmen': getCongressmen,
            'loadGroupUsers': loadGroupUsers,
            'loadHistogram': loadHistogram,
            'searchAutoComplete': searchAutoComplete,
            'postcomment': comment,
            'create': create,
            'invite': invite,
            'edit': edit,
            'delete': delete,
            'setprivacy': setPrivacy,
            'followprivacy': setFollowPrivacy,
            'vote': vote,
            'hoverComparison': hoverComparison,
            'sign': sign,
            'finalize': finalize,
            'userfollow': userFollowRequest,
            'followresponse': userFollowResponse,
            'stopfollow': userFollowStop,
            'answer': answer,
            'joingroup': joinGroupRequest,
            'joinresponse': joinGroupResponse,
            'leavegroup': leaveGroup,
            'matchComparison': matchComparison,
            'share': share,
            'follow': follow,
            'posttogroup': posttogroup,
            'updateCompare': updateCompare,
            'viewCompare': viewCompare,
            'answerWeb': answerWeb,
            'feedback': feedback,
            'updateGroupView': updateGroupView,
            'ajaxFeed': ajaxFeed,
            'ajaxThread': ajaxThread,
            'ajaxGetFeed': ajaxGetFeed,
            'dropdownnotifications': getDropdownNotifications,
            'matchSection': matchSection
        }

#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all actions. [checks is post]
# post: actionPOST - which actionPOST to call
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def actionPOST(request, dict={}):
    """Splitter between all actions."""
    if request.user:
        dict['user'] = getUserProfile(request)
    action = request.POST['action']
    return actions[action](request, dict)