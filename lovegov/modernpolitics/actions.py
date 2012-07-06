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

#-----------------------------------------------------------------------------------------------------------------------
# Takes URL and retrieves HTML.  Parses HTML and extracts title and description metadata.  Also takes a picture
# snapshot of the website.
#-----------------------------------------------------------------------------------------------------------------------
PREFIX_ITERATIONS = ["","http://","http://www."]
def getLinkInfo(request, vals={}, html="",URL=""):
    vals = {}
    url = str(request.POST['remote_url'])
    url.strip()
    # url may not be well formed so try variations until one works
    for prefix in PREFIX_ITERATIONS:
        try:
            URL = prefix + url
            html = urllib2.urlopen(URL,data=None).fp.read()
            if html: break
        except:
            continue
    if html and URL:
        soup = BeautifulStoneSoup(html,selfClosingTags=['img'])
        try: vals['title'] = soup.title.string
        except: vals['title'] = "No Title"
        try:  vals['description'] = soup.findAll(attrs={"name":"description"})[0]['content']
        except: vals['description'] = "No Description"
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
                imageobj['path'] = open(imageobj['path'],'r+')
        except:
            pass

        if len(list) == 0 and (first_image is not None and first_image is not False):
            first_image['path'] =open(first_image['path'],'r+')
            list.append(first_image)

        if len(list) == 0:
            rel_path = 'images/top-logo-default.png'
            this_path = os.path.join(settings.STATIC_ROOT, rel_path)
            list.append({'path':open(this_path,'r+')})

        vals['imglink'] = list

        html = ajaxRender('deployment/snippets/news-autogen.html', vals, request)
        return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# Takes address and/or zip code, finds a geolocation from Google Maps, finds congressional district, POSTs congressmen,
# generates comparisons, and returns HTML back to user
#-----------------------------------------------------------------------------------------------------------------------
def getCongressmen(request, vals={}):
    # POST variables from POST request and formats data
    viewer = vals['viewer']
    address = request.POST['address']
    zip = request.POST['zip']

    location = locationHelper(address, zip)

    congressmen = []
    representative = Representative.objects.get(congresssessions=112,state=location.state,district=location.district)
    representative.json = representative.getComparison(viewer).toJSON()
    congressmen.append(representative)
    senators = Senator.objects.filter(congresssessions=112,state=location.state)
    for senator in senators:
        senator.json = senator.getComparison(viewer).toJSON()
        congressmen.append(senator)

    vals['userProfile'] = viewer
    vals['congressmen'] = congressmen
    vals['state'] = state_district[0]['state']
    vals['district'] = state_district[0]['number']
    vals['latitude'] = location.latitude
    vals['longitude'] = location.longitude
    html = ajaxRender('deployment/snippets/match-compare-div.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))


#-----------------------------------------------------------------------------------------------------------------------
# Given a search "term", returns lists of UserProfiles, News, Petitions, and Questions
# that match given term.
#-----------------------------------------------------------------------------------------------------------------------
def lovegovSearch(term):
    userProfiles = SearchQuerySet().models(UserProfile).autocomplete(content_auto=term)
    news = SearchQuerySet().models(News).filter(content=term)
    questions = SearchQuerySet().models(Question).filter(content=term)
    petitions = SearchQuerySet().models(Petition).filter(content=term)

    # Get lists of actual objects
    userProfiles = [x.object for x in userProfiles]
    petitions = [x.object for x in petitions]
    questions = [x.object for x in questions]
    news = [x.object for x in news]

    return userProfiles, petitions, questions, news


#-----------------------------------------------------------------------------------------------------------------------
# Returns json of list of results which match inputted 'term'. For jquery autocomplete.
#
#-----------------------------------------------------------------------------------------------------------------------
def searchAutoComplete(request,vals={},limit=5):
    string = request.POST['string'].lstrip().rstrip()

    userProfiles, petitions, questions, news = lovegovSearch(string)

    total_results = sum(map(len, (userProfiles, petitions, questions, news)))

    results_length = 0

    userProfile_results = []
    petition_results = []
    question_results = []
    news_results = []

    # If total results is less than the given limit, 
    # show up to the number of actual results
    limit = min(limit, total_results)

    # Get one of each type of result, or as many as will fit until limit is reached
    while results_length < limit:
        if len(userProfiles) > 0:
            userProfile_results.append(userProfiles.pop(0))
        if len(petitions) > 0:
            petition_results.append(petitions.pop(0))
        if len(questions) > 0:
            question_results.append(questions.pop(0))
        if len(news) > 0:
            news_results.append(news.pop(0))
        results_length = sum(map(len, (news_results, question_results, petition_results, userProfile_results)))
    
    # Store results in context values
    vals['userProfiles'], vals['petitions'], vals['questions'], vals['news'] = \
        userProfile_results, petition_results, question_results, news_results
    vals['search_string'] = string
    vals['num_results'] = total_results
    vals['shown'] = results_length
    html = ajaxRender('deployment/pieces/autocomplete.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# Loads members.
#
#-----------------------------------------------------------------------------------------------------------------------
def loadGroupUsers(request,vals={}):
    user = vals['viewer']
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
    vals['defaultImage'] = getDefaultImage().image
    for member in more_members:
        vals['member'] = member
        html += ajaxRender('deployment/snippets/group-member.div.html',vals,request)
    return HttpResponse(json.dumps({'html':html,'num':next_num}))

#-----------------------------------------------------------------------------------------------------------------------
# Loads histogram data.
#
#-----------------------------------------------------------------------------------------------------------------------
def loadHistogram(request, vals={}):
    user = vals['viewer']
    group = Group.objects.get(id=request.POST['group_id'])
    histogram_topic = request.POST['histogram_topic']
    vals['histogram'] = group.getComparisonHistogram(user, topic_alias=histogram_topic, resolution=HISTOGRAM_RESOLUTION)
    html = ajaxRender('deployment/pieces/histogram.html', vals, request)
    to_return = {'html':html}
    return HttpResponse(json.dumps(to_return))


#-----------------------------------------------------------------------------------------------------------------------
# Creates a piece of content and stores it in database.
#
#-----------------------------------------------------------------------------------------------------------------------
def create(request, val={}):
    """Creates a piece of content and stores it in database."""
    formtype = request.POST['type']
    viewer = val['viewer']
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
        action = Action(relationship=c.getCreatedRelationship())
        action.autoSave()
        # if ajax, return page center
        if request.is_ajax():
            if formtype == "N":
                viewer.num_articles += 1
                viewer.save();
                from lovegov.frontend.views import newsDetail
                return newsDetail(request=request,n_id=c.id,vals=val)

            return HttpResponse( json.dumps( { 'success':True , 'url':c.getUrl() } ) )

        else:
            if formtype == "G":
                c.joinMember(viewer)
                c.admins.add(viewer)
                try:
                    file_content = ContentFile(request.FILES['image'].read())
                    Image.open(file_content)
                    c.setMainImage(file_content)
                except IOError:
                    print "Image Upload Error"
            elif formtype == "P":
                try:
                    if 'image' in request.FILES:
                        file_content = ContentFile(request.FILES['image'].read())
                        Image.open(file_content)
                        c.setMainImage(file_content)
                except IOError:
                    print "Image Upload Error"
                viewer.num_petitions += 1
                viewer.save()
            return shortcuts.redirect(c.get_url())
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
            return shortcuts.redirect('/web/')
            vals = {'petition': petition, 'event':event, 'news':news, 'group':group, 'album':album}
            return renderToResponseCSRF('usable/create_content_simple.html',vals,request)

#-----------------------------------------------------------------------------------------------------------------------
# Sends invite email and and addds email to valid emails.
#-----------------------------------------------------------------------------------------------------------------------
def invite(request, vals={}):
    email = request.POST['email']
    user_name = vals['viewer'].get_name()
    description = "invited by: " + user_name
    if not ValidEmail.objects.filter(email=email).exists():
        valid = ValidEmail(email=email, description=description)
        valid.save()
    subject = user_name + " has invited you to join them on LoveGov"
    dictionary = {'user_name':user_name}
    sendTemplateEmail(subject,'userInvite.html', dictionary,"team@lovegov.com",email)
    return HttpResponse("+")

#-----------------------------------------------------------------------------------------------------------------------
# Signs a petition.
#-----------------------------------------------------------------------------------------------------------------------
def sign(request, vals={}):
    user = vals['viewer']
    privacy = getPrivacy(request)
    if privacy == 'PUB':
        petition = Petition.lg.get_or_none(id=request.POST['c_id'])
        if not petition:
            return HttpResponse("This petition does not exist")
        if petition.finalized:
            if petition.sign(user):
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
# Support a politician.
#-----------------------------------------------------------------------------------------------------------------------
def support(request, vals={}):

    viewer = vals['viewer']
    politician = Politician.objects.get(id=request.POST['p_id'])

    confirmed = int(request.POST['confirmed'])
    if confirmed:
        politician.support(viewer)
    else:
        politician.unsupport(viewer)

    return HttpResponse(json.dumps({'num':politician.num_supporters}))

#-----------------------------------------------------------------------------------------------------------------------
# Messages a politician.
#-----------------------------------------------------------------------------------------------------------------------
def messageRep(request, vals={}):

    viewer = vals['viewer']
    politician = Politician.objects.get(id=request.POST['p_id'])
    message = request.POST['message']

    message = Messaged(user=viewer, to_user=politician, message=message)
    num_messages = message.autoSave()

    return HttpResponse(json.dumps({'num':num_messages}))

#-----------------------------------------------------------------------------------------------------------------------
# changes address for a user
#-----------------------------------------------------------------------------------------------------------------------
def submitAddress(request, vals={}):

    address = request.POST['address']
    city = request.POST['city']
    zip = request.POST['zip']
    address = address + ', ' + city

    location = locationHelper(address, zip)

    viewer = vals['viewer']
    viewer.location = location
    viewer.save()

    return HttpResponse("yea!")


#-----------------------------------------------------------------------------------------------------------------------
# Finalizes a petition.
#-----------------------------------------------------------------------------------------------------------------------
def finalize(request, vals={}):
    user = vals['viewer']
    petition = Petition.objects.get(id=request.POST['c_id'])
    creator = petition.getCreator()
    if user==creator:
        petition.finalize()
    return HttpResponse("success")


#-----------------------------------------------------------------------------------------------------------------------
# FORM Edits user profile information from /account/ page
#-----------------------------------------------------------------------------------------------------------------------
def editAccount(request, vals={}):
    viewer = vals['viewer']
    box = request.POST['box']

    if box == 'basic_info':
        if 'first_name' in request.POST: viewer.first_name = request.POST['first_name']
        if 'last_name' in request.POST: viewer.last_name = request.POST['last_name']

        if 'address' in request.POST:
            address = request.POST['address']
            zip = address
            try:
                viewer.location = locationHelper(address, zip)
                viewer.save()
            except:
                viewer.location = None
                viewer.save()

    elif box == 'profile':
        if 'image' in request.FILES:
            try:
                file_content = ContentFile(request.FILES['image'].read())
                Image.open(file_content)
                viewer.setProfileImage(file_content)
            except IOError:
                print "Image Upload Error"
        if 'lock' in request.POST:
            viewer.private_follow = True
        else:
            viewer.private_follow = False
        viewer.save()

        all_parties = list( Party.objects.all() )

        for party_type in PARTY_TYPE:
            if party_type[1] in request.POST:
                party = Party.lg.get_or_none( party_type=party_type[0] )
                party.joinMember(viewer)
                all_parties.remove(party)

        for party in all_parties:
            party.removeMember(viewer)

        viewer.bio = request.POST['bio']
        viewer.save()
        return shortcuts.redirect('/account/profile/')

    return shortcuts.redirect('/account/')

#-----------------------------------------------------------------------------------------------------------------------
# INLINE Edits user profile information
#-----------------------------------------------------------------------------------------------------------------------
def editProfile(request, vals={}):
    viewer = vals['viewer']
    if not 'val' in request.POST or not 'key' in request.POST:
        return HttpResponse( json.dumps({'success':False,'value':''}) )
    value = request.POST['val']
    key = request.POST['key']
    if key not in USERPROFILE_EDITABLE_FIELDS:
        return HttpResponse( json.dumps({'success':True,'value':'Stop trying to break our site'}) )
    setattr( viewer , key , value )
    viewer.save()
    return HttpResponse( json.dumps({'success':True,'value':value}) )

#-----------------------------------------------------------------------------------------------------------------------
# INLINE Edits user profile information
#-----------------------------------------------------------------------------------------------------------------------
def editContent(request, vals={}):
    viewer = vals['viewer']
    if not 'val' in request.POST or not 'key' in request.POST or not 'c_id' in request.POST:
        return HttpResponse( json.dumps({'success':False,'value':''}) )
    value = request.POST['val']
    key = request.POST['key']
    if key not in CONTENT_EDITABLE_FIELDS:
        return HttpResponse( json.dumps({'success':True,'value':'Stop trying to break our site'}) )
    content = Content.lg.get_or_none(id=request.POST['c_id'])
    if content and viewer.id == content.getCreator().id:
        save_content = content.downcast()
        setattr( save_content , key , value )
        save_content.save()
        return HttpResponse( json.dumps({'success':True,'value':value}) )
    return HttpResponse( json.dumps({'success':False,'value':''}) )


#-----------------------------------------------------------------------------------------------------------------------
# Edit content based on editform.
#
#-----------------------------------------------------------------------------------------------------------------------
def edit(request, vals={}):
    """Simple interface for editing content (to be deprecated)"""
    user = vals['viewer']
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
            vals = {'form':form}
            return renderToResponseCSRF('forms/contentform.html', vals, request)
    else:
        vals = {'message':'You cannot edit a piece of content you did not create.'}
        return renderToResponseCSRF('usable/message.html',vals,request)

#-----------------------------------------------------------------------------------------------------------------------
# Deletes content.
#
#-----------------------------------------------------------------------------------------------------------------------
def delete(request, vals={}):
    user = vals['viewer']
    content = Content.objects.get(id=request.POST['c_id'])
    if user == content.getCreator() and content.active:
        content.active = False
        content.save()
        if content.type == 'C':
            comment = content.downcast()
            root_content = comment.root_content
            root_content.num_comments -= 1
            root_content.save()
            on_content = comment.on_content
            if on_content != root_content:
                on_content.num_comments -= 1
                on_content.save()
        deleted = Deleted(user=user, content=content, privacy=getPrivacy(request))
        deleted.autoSave()
        return HttpResponse("successfully deleted content with id:" + request.POST['c_id'])
    else:
        return HttpResponse("you don't have permission")

#-----------------------------------------------------------------------------------------------------------------------
# Saves comment to database from post request.
#
#-----------------------------------------------------------------------------------------------------------------------
def comment(request, vals={}):
    """
    Saves comment to database from post request.

    @param request
    @param vals
            - user
    """
    user = vals['viewer']
    privacy = getPrivacy(request)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(creator=user, privacy=privacy)
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
            vals = {'message':'Comment post failed'}
            return renderToResponseCSRF('usable/message.html',vals,request)

#-----------------------------------------------------------------------------------------------------------------------
# Sets privacy cookie and redirects to inputted page.
#
#-----------------------------------------------------------------------------------------------------------------------
def setPrivacy(request, vals={}):
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
def setFollowPrivacy(request, vals={}):
    user = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if not user:
        return HttpResponse("User does not exist")
    if not request.POST['private_follow']:
        return HttpResponse("No user follow privacy specified")
    user.private_follow = bool(int(request.POST['private_follow']))
    user.save()
    return HttpResponse("follow privacy set")


#-----------------------------------------------------------------------------------------------------------------------
# Likes or dislikes content based on post.
#
#-----------------------------------------------------------------------------------------------------------------------
def vote(request, vals):
    """Likes or dislikes content based on post."""
    user = vals['viewer']
    privacy = getPrivacy(request)
    content = Content.objects.get(id=request.POST['c_id'])
    vote = int(request.POST['vote'])
    # save vote
    if vote == 1:
        value = content.like(user=user, privacy=privacy)
    elif vote == -1:
        value = content.dislike(user=user, privacy=privacy)
    to_return = {'my_vote':value, 'status':content.status}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question.
#
#-----------------------------------------------------------------------------------------------------------------------
def answer(request, vals={}):
    """ Saves a users answer to a question."""
    user = vals['viewer']
    question = Question.objects.get(id=request.POST['q_id'])
    if request.POST['questionPRI'] != "":
        privacy = request.POST['questionPRI']
    else:
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
        return HttpResponse("+")

#----------------------------------------------------------------------------------------------------------------------
# Joins group if user is not already a part.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupRequest(request, vals={}):
    """Joins group if user is not already a part."""
    from_user = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()
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
    if group_joined.invited:
        group.joinMember(from_user, privacy=getPrivacy(request))
        action = Action(relationship=group_joined,modifier="D")
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return HttpResponse("follow success")
    #If the group is privacy secret...
    if group.group_privacy == 'S':
        return HttpResponse("cannot request to join secret group")
    #If the group type is open...
    if group.group_privacy == 'O':
        group.joinMember(from_user, privacy=getPrivacy(request))
        action = Action(relationship=group_joined,modifier="D")
        action.autoSave()
        for admin in group.admins.all():
            admin.notify(action)
        return HttpResponse("follow success")
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
        return HttpResponse("follow request")

#----------------------------------------------------------------------------------------------------------------------
# Confirms or rejects a user GroupJoined, if GroupJoined was requested.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupResponse(request, vals={}):
    response = request.POST['response']
    from_user = UserProfile.objects.get(id=request.POST['follow_id'])
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()
    already = GroupJoined.objects.filter(user=from_user, group=group)
    if already:
        group_joined = already[0]
        if group_joined.confirmed:
            return HttpResponse("This person is already in your group")
        elif group_joined.requested:
            if response == 'Y':
                group.joinMember(from_user, privacy=getPrivacy(request))
                action = Action(relationship=group_joined,modifier="A")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("they're now in your group")
            elif response == 'N':
                group_joined.reject()
                action = Action(relationship=group_joined,modifier="X")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have rejected their join request")
    return HttpResponse("this person has not requested to join you")

#----------------------------------------------------------------------------------------------------------------------
# Confirms or declines a group GroupJoined, if GroupJoined was invited.
#
#-----------------------------------------------------------------------------------------------------------------------
def groupInviteResponse(request, vals={}):
    response = request.POST['response']
    from_user = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    already = GroupJoined.objects.filter(user=from_user, group=group, privacy=getPrivacy(request))
    if already:
        group_joined = already[0]
        if group_joined.confirmed:
            return HttpResponse("You have already joined that group")
        if group_joined.invited:
            if response == 'Y':
                group.joinMember(from_user, privacy=getPrivacy(request))
                action = Action(relationship=group_joined,modifier="D")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have joined this group!")
            elif response == 'N':
                group_joined.reject()
                action = Action(relationship=group_joined,modifier="N")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have rejected this group invitation")
    return HttpResponse("you were not invitied to join this group")

#----------------------------------------------------------------------------------------------------------------------
# Requests to follow inputted user.
#
#-----------------------------------------------------------------------------------------------------------------------
def userFollowRequest(request, vals={}):
    from_user = vals['viewer']
    to_user = UserProfile.objects.get(id=request.POST['p_id'])
    #No Self Following
    if to_user.id == from_user.id:
        return HttpResponse("cannot follow yourself")
    already = UserFollow.objects.filter(user=from_user, to_user=to_user)
    #If there's already a follow relationship
    if already: #If it exists, get it
        user_follow = already[0]
        if user_follow.confirmed: #If you're confirmed following already, you're done
            return HttpResponse("already following this person")
    else: #If there's no follow relationship, make one
        user_follow = UserFollow(user=from_user, to_user=to_user, privacy=getPrivacy(request))
        user_follow.autoSave()
    # If this user is public follow
    if not to_user.private_follow:
        from_user.follow(to_user)
        action = Action(relationship=user_follow,modifier='D')
        action.autoSave()
        to_user.notify(action)
        return HttpResponse("follow success")
    #otherwise, if you've already requested to follow this user, you're done
    elif user_follow.requested and not user_follow.rejected:
        return HttpResponse("already requested to follow this person")
    #Otherwise, make the request to follow this user
    else:
        user_follow.clear()
        user_follow.request()
        action = Action(relationship=user_follow,modifier='R')
        action.autoSave()
        to_user.notify(action)
        return HttpResponse("follow request")

#----------------------------------------------------------------------------------------------------------------------
# Confirms or denies user follow, if user follow was requested.
#-----------------------------------------------------------------------------------------------------------------------
def userFollowResponse(request, vals={}):
    to_user = vals['viewer']
    response = request.POST['response']
    from_id = request.POST.get('p_id')
    if not from_id:
        return HttpResponse("Invalid user id given")
    from_user = UserProfile.objects.get(id=request.POST['p_id'])
    already = UserFollow.objects.filter(user=from_user, to_user=to_user)
    if already:
        user_follow = already[0]
        if user_follow.requested:
            if response == 'Y':
                # Create follow relationship!
                from_user.follow(to_user)
                action = Action(relationship=user_follow,modifier='A')
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
def userFollowStop(request, vals={}):
    """Removes connection between users."""
    from_user = vals['viewer']
    to_user = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if to_user:
        already = UserFollow.objects.filter(user=from_user, to_user=to_user)
        if not already:
            user_follow = UserFollow(user=from_user, to_user=to_user, privacy=getPrivacy(request))
            user_follow.autoSave()
        else:
            user_follow = already[0]
        from_user.unfollow(to_user)
        action = Action(relationship=user_follow,modifier='S')
        action.autoSave()
        to_user.notify(action)
        # to_user.notify(action)
        return HttpResponse("follow removed")
    return HttpResponse("To User does not exist")


#----------------------------------------------------------------------------------------------------------------------
# Invites inputted user to join group.
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupInvite(request, vals={}):
    """Invites inputted to join group, if inviting user is admin."""
    user = vals['viewer']
    to_invite = UserProfile.objects.get(id=request.POST['invited_id'])
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()
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
def leaveGroup(request, vals={}):
    """Leaves group if user is a member (and does stuff if user would be last admin)"""
    # if not system then remove
    from_user = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()
    group_joined = GroupJoined.objects.get(group=group, user=from_user)
    if group_joined and not group.system:
        group.removeMember(from_user)
        group.admins.remove(from_user)
        if not group.admins.all() and not group.group_type == 'P':
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
        return HttpResponse("follow removed")
    else:
        return HttpResponse("system group")

#-----------------------------------------------------------------------------------------------------------------------
# Adds content to group.
#
#-----------------------------------------------------------------------------------------------------------------------
def posttogroup(request, vals={}):
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
def updateCompare(request, vals={}):
    """Saves a Comparison between the two inputted users."""
    comp = ViewComparison.objects.get(id=request.POST['c_id'])
    comparison = updateComparison(comp)
    return HttpResponse(simplejson.dumps({'url':comparison.get_url()}))

#-----------------------------------------------------------------------------------------------------------------------
# Returns the url of the latest comparison between two users, or creates a comparison between two users and then
#
#-----------------------------------------------------------------------------------------------------------------------
def viewCompare(request, vals={}):
    """Returns link to comparison between the two inputted users via simplejson/ajax."""
    vals = {'url':'/compare/' + request.POST['a_id'] + '/' +  request.POST['b_id'] + '/'}
    return HttpResponse(simplejson.dumps(vals))

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question from the QAWeb interface
#-----------------------------------------------------------------------------------------------------------------------
def answerWeb(request, vals={}):
    """ Saves a users answer to a question."""
    user = vals['viewer']
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
        vals = {'object': response, 'back': request.POST['back']}
        return renderToResponseCSRF('qaweb/display_response.html', vals, request)
    else:
        return shortcuts.redirect(response.get_url)

#-----------------------------------------------------------------------------------------------------------------------
# Saves user feedback to db.
#-----------------------------------------------------------------------------------------------------------------------
def feedback(request,vals={}):
    def sendFeedbackEmail(text,user):
        vals = {'text':text,'name':name}
        for team_member in TEAM_EMAILS:
            sendTemplateEmail("LoveGov Feedback",'feedback.html',vals,"team@lovegov.com",team_member)
        return
    user = vals['viewer']
    page = request.POST['path']
    text = request.POST['text']
    name = request.POST['name']
    feedback = Feedback(user=user,page=page,feedback=text)
    feedback.save()
    thread.start_new_thread(sendFeedbackEmail,(text,name,))
    temp_logger.debug("feedback sent.")
    return HttpResponse("+")

#-----------------------------------------------------------------------------------------------------------------------
# Updates the aggregate view in the db for a particular group of users.
#-----------------------------------------------------------------------------------------------------------------------
def updateGroupView(request,vals={}):
    group = Group.objects.get(id=request.POST['g_id'])
    updateGroupView(group)
    return HttpResponse("updated")

#-----------------------------------------------------------------------------------------------------------------------
# Compares the session's user with the provided alias and returns JSON dump of comparison data.
# args: request, user
# POST: alias
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def hoverComparison(request,vals={}):
    object = urlToObject(request.POST['href'])
    comparison = object.getComparison(vals['viewer'])
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
def matchComparison(request,vals={}):

    viewer = vals['viewer']
    object = urlToObject(request.POST['item_url'])
    object.compare = object.getComparison(viewer).toJSON()

    vals['item'] = object
    html = ajaxRender('deployment/center/match/match-new-box.html',vals,request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# reloads html for thread
#-----------------------------------------------------------------------------------------------------------------------
def ajaxThread(request, vals={}):
    from lovegov.frontend.views import makeThread
    content = Content.objects.get(id=request.POST['c_id'])
    user = vals['viewer']
    thread = makeThread(request, content, user, vals=vals)
    to_return = {'html':thread}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# gets feed using inputted post parameters
#-----------------------------------------------------------------------------------------------------------------------
def ajaxGetFeed(request, vals={}):

    feed_ranking = request.POST['feed_ranking']
    feed_topics = json.loads(request.POST['feed_topics'])
    feed_types = json.loads(request.POST['feed_types'])
    feed_levels = json.loads(request.POST['feed_levels'])
    feed_groups = json.loads(request.POST['feed_groups'])
    feed_submissions_only = bool(int(request.POST['feed_submissions_only']))
    feed_display = request.POST['feed_display']

    feed_start = int(request.POST['feed_start'])
    feed_end = int(request.POST['feed_end'])

    filter = {
        'topics': feed_topics,
        'types': feed_types,
        'levels': feed_levels,
        'groups': feed_groups,
        'ranking': feed_ranking,
        'submissions_only': feed_submissions_only
    }

    content = getFeed(filter, start=feed_start, stop=feed_end)
    items = ajaxFeedHelper(content, vals['viewer'])
    vals['items']=items
    vals['display']=feed_display

    if feed_display == 'L':
        html = ajaxRender('deployment/center/feed/linear_helper.html', vals, request)
        to_return = {'html':html, 'num':len(content)}
    else:
        cards = []
        for x in items:
            vals['item'] = x[0].downcast()
            vals['my_vote'] = x[1]
            card =  ajaxRender('deployment/center/feed/pinterest.html', vals, request)
            cards.append(card)
        to_return = {'cards':json.dumps(cards), 'num':len(content)}
    return HttpResponse(json.dumps(to_return))

def ajaxFeedHelper(content, user):
    list = []
    user_votes = Voted.objects.filter(user=user)
    for c in content:
        vote = user_votes.filter(content=c)
        if vote:
            my_vote=vote[0].value
        else:
            my_vote=0
        list.append((c,my_vote))    # content, my_vote
    return list

#-----------------------------------------------------------------------------------------------------------------------
# saves a filter setting
#-----------------------------------------------------------------------------------------------------------------------
def saveFilter(request, vals={}):

    viewer = vals['viewer']

    name = request.POST['feed_name']

    ranking = request.POST['feed_ranking']
    types = json.loads(request.POST['feed_types'])
    levels = json.loads(request.POST['feed_levels'])
    topics = json.loads(request.POST['feed_topics'])
    groups = json.loads(request.POST['feed_groups'])
    submissions_only = bool(int(request.POST['feed_submissions_only']))
    display = request.POST['feed_display']

    already = viewer.my_filters.filter(name=name)
    if already:
        filter = already[0]
        filter.ranking = ranking
        filter.types = types
        filter.levels = levels
        filter.submissions_only = submissions_only
        filter.display = display
        filter.save()
    else:
        filter = SimpleFilter(ranking=ranking, types=types,
            levels=levels, submissions_only=submissions_only,
        display=display, name=name, creator=viewer)
        filter.save()
        viewer.my_filters.add(filter)

    filter.topics.clear()
    for t in topics:
        filter.topics.add(t)
    filter.groups.clear()
    for g in groups:
        filter.groups.add(g)

    return HttpResponse("success")

#-----------------------------------------------------------------------------------------------------------------------
# deletes a filter setting
#-----------------------------------------------------------------------------------------------------------------------
def deleteFilter(request, vals={}):

    viewer = vals['viewer']
    name = request.POST['f_name']

    if name == 'default':
        return HttpResponse("cant delete default filter.")

    already = viewer.my_filters.filter(name=name)
    if already:
        to_delete = already[0]
        viewer.my_filters.remove(to_delete)

    return HttpResponse("deleted")

#-----------------------------------------------------------------------------------------------------------------------
# gets a filter setting and returns via json dump
#-----------------------------------------------------------------------------------------------------------------------
def getFilter(request, vals={}):

    f_id = request.POST['filter_id']
    filter = SimpleFilter.objects.get(id=f_id)
    to_return = filter.getDict()

    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# gets notifications
#-----------------------------------------------------------------------------------------------------------------------
def getNumNotifications(request, vals={}):

    viewer = vals['viewer']
    new_notifications = viewer.getNotifications(new=True)
    num = new_notifications.count()

    return HttpResponse('wooo')

#-----------------------------------------------------------------------------------------------------------------------
# gets notifications
#-----------------------------------------------------------------------------------------------------------------------
def getNotifications(request, vals={}):
    # Get Notifications
    viewer = vals['viewer']
    num_notifications = 0
    if 'num_notifications' in request.POST:
        num_notifications = int(request.POST['num_notifications'])

    notifications_text = []
    num_still_new = 0

    if 'dropdown' in request.POST:

        new_notifications = viewer.getNotifications(new=True)
        num_new = len(new_notifications)
        new_notifications = new_notifications[0:NOTIFICATION_INCREMENT+2]
        num_returned = len(new_notifications)
        num_still_new = num_new - num_returned

        old_notifications = None
        diff = NOTIFICATION_INCREMENT - num_returned
        if diff > 0:
            old_notifications = viewer.getNotifications(num=diff,start=num_notifications,old=True)
        elif diff < 0:
            diff = 0
        for notification in new_notifications:
            notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )
        if old_notifications:
            for notification in old_notifications:
                notifications_text.append( notification.getVerbose(view_user=viewer) )
        num_notifications += diff + num_returned

    else:
        notifications = viewer.getNotifications(num=NOTIFICATION_INCREMENT,start=num_notifications)
        if not notifications:
            return HttpResponse(json.dumps({'error':'No more notifications'}))
        for notification in notifications:
            notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )
        num_notifications += NOTIFICATION_INCREMENT

    vals['dropdown_notifications_text'] = notifications_text
    vals['num_notifications'] = num_notifications
    html = ajaxRender('deployment/snippets/notification_snippet.html', vals, request)
    if 'dropdown' in request.POST:
        html = ajaxRender('deployment/snippets/notification_dropdown.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_notifications':num_notifications,'num_still_new':num_still_new}))

#-----------------------------------------------------------------------------------------------------------------------
# gets user activity feed
#-----------------------------------------------------------------------------------------------------------------------
def getUserActions(request, vals={}):
    # Get Actions
    viewer = vals['viewer']
    if not 'p_id' in request.POST:
        return HttpResponse(json.dumps({'error':'No profile id given'}))
    user_prof = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if not user_prof:
        return HttpResponse(json.dumps({'error':'Invalid profile id'}))
    num_actions = 0
    if 'num_actions' in request.POST:
        num_actions = int(request.POST['num_actions'])
    actions = user_prof.getActivity(num=NOTIFICATION_INCREMENT,start=num_actions)
    if len(actions) == 0:
        return HttpResponse(json.dumps({'error':'No more actions'}))
    actions_text = []
    for action in actions:
        actions_text.append( action.getVerbose(view_user=viewer) )
    vals['actions_text'] = actions_text
    num_actions += NOTIFICATION_INCREMENT
    vals['num_actions'] = num_actions
    html = ajaxRender('deployment/snippets/action_snippet.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_actions':num_actions}))

#-----------------------------------------------------------------------------------------------------------------------
# gets group activity feed
#-----------------------------------------------------------------------------------------------------------------------
def getGroupActions(request, vals={}):
    # Get Actions
    viewer = vals['viewer']
    if not 'g_id' in request.POST:
        return HttpResponse(json.dumps({'error':'No group id given'}))
    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        return HttpResponse(json.dumps({'error':'Invalid group id'}))
    num_actions = 0
    if 'num_actions' in request.POST:
        num_actions = int(request.POST['num_actions'])
    actions = group.getActivity(num=NOTIFICATION_INCREMENT,start=num_actions)
    if len(actions) == 0:
        print 'no more actions'
        return HttpResponse(json.dumps({'error':'No more actions'}))
    actions_text = []
    for action in actions:
        actions_text.append( action.getVerbose(view_user=viewer) )
    vals['actions_text'] = actions_text
    num_actions += NOTIFICATION_INCREMENT
    vals['num_actions'] = num_actions
    html = ajaxRender('deployment/snippets/action_snippet.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_actions':num_actions}))

#-----------------------------------------------------------------------------------------------------------------------
# gets group members
#-----------------------------------------------------------------------------------------------------------------------
def getGroupMembers(request, vals={}):
    # Get Members
    viewer = vals['viewer']
    if not 'g_id' in request.POST:
        return HttpResponse(json.dumps({'error':'No group id given'}))
    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        return HttpResponse(json.dumps({'error':'Invalid group id'}))
    num_members = 0
    if 'num_members' in request.POST:
        num_members = int(request.POST['num_members'])
    print num_members
    members = group.getMembers(num=MEMBER_INCREMENT,start=num_members)
    print len(members)
    if len(members) == 0:
        return HttpResponse(json.dumps({'error':'No more members'}))
    members_text = []
    for member in members:
        member_text = render_to_string( 'deployment/snippets/group-member-new.html' , {'member':member} )
        members_text.append( member_text )
    vals['members_text'] = members_text
    num_members += MEMBER_INCREMENT
    vals['num_members'] = num_members
    html = ajaxRender('deployment/snippets/member-snippet.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_members':num_members}))

#-----------------------------------------------------------------------------------------------------------------------
# gets user groups
#-----------------------------------------------------------------------------------------------------------------------
def getUserGroups(request, vals={}):
    # Get Groups
    viewer = vals['viewer']
    if not 'p_id' in request.POST:
        return HttpResponse(json.dumps({'error':'No profile id given'}))
    user_prof = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if not user_prof:
        return HttpResponse(json.dumps({'error':'Invalid profile id'}))
    num_groups = 0
    if 'num_groups' in request.POST:
        num_groups = int(request.POST['num_groups'])
    groups = user_prof.getUserGroups(num=GROUP_INCREMENT,start=num_groups)
    if len(groups) == 0:
        return HttpResponse(json.dumps({'error':'No more groups'}))
    vals['user_groups'] = groups
    num_groups += GROUP_INCREMENT
    vals['num_groups'] = num_groups
    html = ajaxRender('deployment/snippets/group_snippet.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_groups':num_groups}))


def matchSection(request, vals={}):
    section = request.POST['section']
    vals['defaultImage'] = getDefaultImage().image
    if section == 'election':
        user = vals['viewer']
        c1 = UserProfile.objects.get(first_name="Barack", last_name="Obama")
        c2 = UserProfile.objects.get(first_name="Mitt",last_name="Romney")

        list = [c1,c2]
        for c in list:
            comparison = getUserUserComparison(user,c)
            c.compare = comparison.toJSON()
            c.result = comparison.result
        vals['c1'] = c1
        vals['c2'] = c2

        # vals['viewer'] doesn't translate well in the template
        vals['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-tryptic-template.html', vals, request)

    elif section == 'social':
        user = vals['viewer']
        comparison = getUserUserComparison(user,user)
        user.compare = comparison.toJSON()
        user.result = comparison.result
        vals['c1'] = user

        # friends
        vals['friends'] = user.getIFollow()[0:5]

        # groups
        vals['groups'] = user.getGroups()

        # networks
        lovegov = getLoveGovUser()
        network = user.getNetwork()
        congress = getCongressNetwork()
        vals['networks'] = [network,congress,lovegov]

        vals['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-social-network.html', vals, request)

    elif section == 'cause':
        user = vals['viewer']
        comparison = getUserUserComparison(user,user)
        user.compare = comparison.toJSON()
        user.result = comparison.result
        vals['c1'] = user

        # friends
        vals['friends'] = user.getIFollow()[0:5]

        # groups
        vals['groups'] = user.getGroups()

        # networks
        lovegov = getLoveGovUser()
        network = user.getNetwork()
        congress = getCongressNetwork()
        vals['networks'] = [network,congress,lovegov]

        vals['userProfile'] = user
        html = ajaxRender('deployment/center/match/match-social-network.html', vals, request)

    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# Shares a piece of content
#-----------------------------------------------------------------------------------------------------------------------
def shareContent(request, vals={}):

    user = vals['viewer']
    content = Content.objects.get(id=request.POST['share_this'])
    share_with = json.loads(request.POST['share_with'])

    follow_ids = []
    group_ids = []
    all_followers = False
    all_groups = False
    all_networks = False
    for x in share_with:
        splitted = x.split('_')
        pre = splitted[0]
        id = splitted[1]
        if pre == 'follower':
            follow_ids.append(id)
        elif pre == 'group':
            group_ids.append(id)
        elif pre == 'network':
            group_ids.append(id)
        elif pre == 'all':
            if id == 'followers':
                all_followers=True
            elif id == 'groups':
                all_groups = True
            elif id == 'networks':
                all_networks = True

    if all_followers:
        share_users = user.getFollowMe()
    else:
        if follow_ids:
            share_users = user.getFollowMe().filter(id__in=follow_ids)
        else:
            share_users = []

    if all_networks and all_groups:
        share_groups = user.getGroups()
    else:
        if all_networks:
            share_groups = user.getNetworks()
        elif all_groups:
            share_groups = user.getUserGroups()
        else:
            if group_ids:
                groups = user.getGroups()
                share_groups = user.getGroups().filter(id__in=group_ids)
            else:
                share_groups = []

    shared = Shared.lg.get_or_none(user=user, content=content)
    if not shared:
        shared = Shared(user=user, content=content)
        shared.autoSave()
    for u in share_users:
        shared.addUser(u)
    for g in share_groups:
        shared.addGroup(g)

    return HttpResponse('shared')

#-----------------------------------------------------------------------------------------------------------------------
# blog action
#-----------------------------------------------------------------------------------------------------------------------
def blogAction(request,vals={}):
    user = vals['viewer']
    if 'url' in request.POST:
        from lovegov.modernpolitics.helpers import urlToObject
        blogEntry = urlToObject(request.POST['url'])
        if blogEntry:blogEntry.delete()
        return HttpResponse("+")
    elif 'category' in request.POST:
        category = string.capitalize(request.POST['category'])
        blogPosts = BlogEntry.objects.all().order_by('-id')
        blogList = []

        for blogPost in blogPosts:
            if category in blogPost.category: blogList.append(blogPost)

        html = ''
        for blogPost in blogList:
            html += ajaxRender('deployment/pages/blog/blog-item.html',{'blogPost':blogPost},request)

    else:
        if user.isDeveloper():
            title = request.POST['title']
            text = request.POST['text']

            category = []
            if 'update' in request.POST: category.append('Update')
            if 'general' in request.POST: category.append('General')
            if 'news' in request.POST: category.append('News')
            if not category: return HttpResponse(json.dumps({'error':" < Select a Category"}))

            blog = BlogEntry(creator=user,title=title,message=text,category=category)
            blog.save()

            vals['blogPost'] = blog

            html = ajaxRender('deployment/pages/blog/blog-item.html',vals,request)
        else:
            html = ''

    return HttpResponse(json.dumps({'html':html}))


def flag(request,vals={}):
    c_id = request.POST.get('c_id')
    c = Comment.lg.get_or_none(id=c_id)
    val_data = {'flagger': vals['viewer'].get_name(), 'comment': c}
    for team_member in TEAM_EMAILS:
            sendTemplateEmail("LoveGov Flag",'flag.html',val_data,"team@lovegov.com",team_member)
    return HttpResponse("Comment has been flagged successfully.")

#-----------------------------------------------------------------------------------------------------------------------
# get histogram data
#-----------------------------------------------------------------------------------------------------------------------
def updateHistogram(request, vals={}):

    group = Group.objects.get(id=request.POST['g_id'])
    resolution = int(request.POST['resolution'])
    start = int(request.POST['start'])
    num = int(request.POST['num'])
    topic_alias = request.POST['topic_alias']
    viewer = vals['viewer']

    bucket_list = getBucketList(resolution=resolution)
    histogram = group.getComparisonHistogram(viewer, bucket_list, start=start, num=num, topic_alias=topic_alias)

    return HttpResponse(json.dumps(histogram))

#-----------------------------------------------------------------------------------------------------------------------
# returns html to render avatars of histogram percentile
#-----------------------------------------------------------------------------------------------------------------------
def getHistogramMembers(request, vals={}):

    u_ids = json.loads(request.POST['u_ids'])
    members = UserProfile.objects.filter(id__in=u_ids).order_by('id')

    vals['users'] = members
    how_many = len(members)
    html = ajaxRender('deployment/snippets/histogram/avatars_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}

    return HttpResponse(json.dumps(to_return))

def getAllGroupMembers(request, vals={}):

    group = Group.objects.get(id=request.POST['g_id'])
    start = int(request.POST['start'])
    num = int(request.POST['num'])
    members = group.getMembers(start=start, num=num)

    vals['users'] = members
    how_many = len(members)
    html = ajaxRender('deployment/snippets/histogram/avatars_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}

    return HttpResponse(json.dumps(to_return))

def likeThis(request, vals={}):

    html = ajaxRender('deployment/pieces/like_this.html', vals, request)
    to_return = {'html':html}

    return HttpResponse(json.dumps(to_return))

def changeContentPrivacy(request, vals={}):
    html = ''
    viewer = vals['viewer']
    content_id = request.POST.get('content_id')
    error = ''
    if content_id:
        if Content.lg.get_or_none(id=content_id):
            content = Content.lg.get_or_none(id=content_id)
            if viewer==content.creator:
                if content.privacy == 'PRI':
                    content.privacy = 'PUB'
                elif content.privacy == 'PUB':
                    content.privacy = 'PRI'
                else:
                    error = 'Content set to invalid privacy type.'
            else:
                error = 'You are not the owner of this content.'
        else:
            error = 'The given content identifier is invalid.'
    else:
        error = 'No content identifier given.'
    if error=='':
        content.save()
        vals['content'] = content
        html =ajaxRender('deployment/snippets/content-privacy.html', vals, request)
    to_return = {'html':html, 'error': error}
    print "to_return: "+str(to_return)
    return HttpResponse(json.dumps(to_return))

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
            'editaccount': editAccount,
            'editprofile': editProfile,
            'editcontent': editContent,
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
            'groupinviteresponse': groupInviteResponse,
            'leavegroup': leaveGroup,
            'matchComparison': matchComparison,
            'posttogroup': posttogroup,
            'updateCompare': updateCompare,
            'viewCompare': viewCompare,
            'answerWeb': answerWeb,
            'feedback': feedback,
            'updateGroupView': updateGroupView,
            'ajaxThread': ajaxThread,
            'getnotifications': getNotifications,
            'getuseractions': getUserActions,
            'getusergroups': getUserGroups,
            'getgroupactions': getGroupActions,
            'getgroupmembers': getGroupMembers,
            'ajaxGetFeed': ajaxGetFeed,
            'matchSection': matchSection,
            'saveFilter': saveFilter,
            'deleteFilter': deleteFilter,
            'getFilter': getFilter,
            'matchSection': matchSection,
            'shareContent': shareContent,
            'blogAction': blogAction,
            'flag': flag,
            'updateHistogram': updateHistogram,
            'getHistogramMembers': getHistogramMembers,
            'getAllGroupMembers': getAllGroupMembers,
            'support': support,
            'messageRep': messageRep,
            'submitAddress':submitAddress,
            'likeThis':likeThis,
            'changeContentPrivacy': changeContentPrivacy,
        }

#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all actions. [checks is post]
# post: actionPOST - which actionPOST to call
# args: request
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def actionPOST(request, vals={}):
    """Splitter between all actions."""
    if request.user:
        vals['viewer'] = getUserProfile(request)
    if not request.REQUEST.__contains__('action'):
        return HttpResponse('No action specified.')
    action = request.REQUEST['action']
    if action not in actions:
        return HttpResponse('The specified action ("%s") is not valid.' % (action))
    return actions[action](request, vals)
