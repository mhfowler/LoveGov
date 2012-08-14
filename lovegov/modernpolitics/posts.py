########################################################################################################################
########################################################################################################################
#
#           Actions
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.actions import *

#-----------------------------------------------------------------------------------------------------------------------
# Takes URL and retrieves HTML.  Parses HTML and extracts title and description metadata.  Also takes a picture
# snapshot of the website.
#-----------------------------------------------------------------------------------------------------------------------
PREFIX_ITERATIONS = ["","http://","http://www."]
DESCRIPTION_TAGS = [("name","description"),("property","og:description")]
def getLinkInfo(request, vals={}, html="",URL=""):
    try:
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
            # make HTML well formed
            html = re.sub(r'<script\s*.*</script>',"",html)
            html = re.sub(r'<!DOCTYPE html\s*.*>',"",html)
            soup = BeautifulSoup(html)

            # set title
            try: vals['title'] = soup.find('title').string
            except: vals['title'] = "No Title"

            # set description
            for tag in DESCRIPTION_TAGS:
                description = soup.findAll(attrs={tag[0]:tag[1]})
                if description:
                    vals['description'] = description[0]['content']
                    break
            if 'description' not in vals:
                vals['description'] = "No Description"

            # init image collection
            image_refs = soup.findAll("img")
            list = []
            first_image = None

            for num in range(0,len(image_refs)):
                try:
                    img_url = image_refs[num]['src']
                    if num == 0:
                        first_image = downloadImage(img_url=img_url,url=URL,min_size=1)
                    elif len(list) == 5:
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

            html = ajaxRender('site/snippets/news-autogen.html', vals, request)
            return HttpResponse(json.dumps({'html':html}))
        else:
            return HttpResponse("-")
    except:
        return HttpResponse("-")

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
    html = ajaxRender('site/snippets/match-compare-div.html', vals, request)
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
    groups = SearchQuerySet().models(Group).filter(content=term)

    # Get lists of actual objects
    userProfiles = [x.object for x in userProfiles]
    petitions = [x.object for x in petitions]
    questions = [x.object for x in questions]
    news = [x.object for x in news]
    groups = [x.object for x in groups]

    return userProfiles, petitions, questions, news, groups


#-----------------------------------------------------------------------------------------------------------------------
# Returns json of list of results which match inputted 'term'. For jquery autocomplete.
#
#-----------------------------------------------------------------------------------------------------------------------
def searchAutoComplete(request,vals={},limit=5):
    string = request.POST['string'].lstrip().rstrip()

    userProfiles, petitions, questions, news, groups = lovegovSearch(string)

    total_results = sum(map(len, (userProfiles, petitions, questions, news, groups)))

    results_length = 0

    userProfile_results = []
    petition_results = []
    question_results = []
    news_results = []
    group_results = []

    # If total results is less than the given limit, 
    # show up to the number of actual results
    limit = min(limit, total_results)

    # Get one of each type of result, or as many as will fit until limit is reached
    while results_length < limit:
        if len(userProfiles) > 0:
            popped = userProfiles.pop(0)
            if popped:
                userProfile_results.append(popped)
        if len(petitions) > 0:
            popped = petitions.pop(0)
            if popped:
                petition_results.append(popped)
        if len(questions) > 0:
            popped = questions.pop(0)
            if popped:
                question_results.append(popped)
        if len(news) > 0:
            popped = news.pop(0)
            if popped:
                news_results.append(popped)
        if len(groups) > 0:
            popped = groups.pop(0)
            if popped:
                group_results.append(popped)
        results_length = sum(map(len, (news_results, question_results, petition_results, userProfile_results, group_results)))
    
    # Store results in context values
    vals['userProfiles'], vals['petitions'], vals['questions'], vals['news'], vals['groups'] = \
        userProfile_results, petition_results, question_results, news_results, group_results
    vals['search_string'] = string
    vals['num_results'] = total_results
    vals['shown'] = results_length
    html = ajaxRender('site/pieces/autocomplete.html', vals, request)
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
        html += ajaxRender('site/pieces/misc/group-member.div.html',vals,request)
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
    html = ajaxRender('site/pieces/histogram.html', vals, request)
    to_return = {'html':html}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# Creates a piece of content and stores it in database.
#
#-----------------------------------------------------------------------------------------------------------------------
def create(request, vals={}):
    formtype = request.POST['type']
    viewer = vals['viewer']
    if formtype == 'P':
        form = CreatePetitionForm(request.POST)
    elif formtype == 'N':
        form = CreateNewsForm(request.POST)
    elif formtype =='G':
        form = CreateUserGroupForm(request.POST)

    # if valid form, save to db
    if form.is_valid():
        # save new piece of content
        c = form.complete(request)
        action = Action(privacy=getPrivacy(request),relationship=c.getCreatedRelationship())
        action.autoSave()
        # if ajax, return page center
        if request.is_ajax():
            if formtype == "N":
                viewer.num_articles += 1
                viewer.num_posts += 1
                viewer.save()
                from lovegov.frontend.views import newsDetail
                return newsDetail(request=request,n_id=c.id,vals=vals)
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
                viewer.num_posts += 1
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

def createMotion(request, vals={}):

    group = Group.lg.get_or_none(id=request.POST['g_id'])

    if group.democratic:
        motion_type = request.POST['motion_type']
        motion = None

        if motion_type == 'add_moderator':
            moderator = UserProfile.objects.get(id=request.POST['moderator_id'])
            if moderator not in group.members.all():
                error_message = "motion to add moderator of member who is not in group," + group.get_name()
                LGException(error_message)
                return HttpResponseServerError(error_message)
            elif moderator in group.admins.all():
                error_message = "motion to add moderator of member who is already moderator," + group.get_name()
                LGException(error_message)
                return HttpResponseServerError(error_message)
            else:
                motion = Motion(motion_type=motion_type, moderator=moderator,
                    full_text=request.POST['because'], group=group)

        elif motion_type == 'remove_moderator':
            moderator = UserProfile.objects.get(id=request.POST['moderator_id'])
            if moderator not in group.admins.all():
                error_message = "motion to remove moderator who is not moderator of group," + group.get_name()
                LGException(error_message)
                return HttpResponseServerError(error_message)
            else:
                motion = Motion(motion_type=motion_type, moderator=moderator,
                    full_text=request.POST['because'], group=group)

        elif motion_type == 'coup_detat':
            motion = Motion(motion_type=motion_type, government_type=request.POST['government_type'],
                full_text=request.POST['because'], group=group)

        if motion:
            motion.autoSave(creator=vals['viewer'], privacy=getPrivacy(request))
            return HttpResponse(json.dumps({'success':True}))
        else:
            error_message = "create motion action did not create motion for group", group.get_name()
            LGException(error_message)
            return HttpResponse(error_message)

    else:
        error_message = "post to create motion for non-democratic group," + group.get_name()
        LGException(error_message)
        return HttpResponse(error_message)

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
                context['p'] = petition
                template = loader.get_template('deployment/snippets/signer.html')
                signer_string = template.render(context)  # render html snippet
                template = loader.get_template('deployment/snippets/petition_bar.html')
                bar_string = template.render(context)  # render html snippet
                vals = {"success":True, "signer":signer_string, "bar":bar_string}
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
    full_address = ''

    address = request.POST.get('address')
    if address:
        full_address += address

    city = request.POST.get('city')
    if city:
        if not full_address == '':
            full_address += ', '
        full_address += city

    state = request.POST.get('state')
    if state:
        if not full_address == '':
            full_address += ', '
        full_address += state

    zip = request.POST.get('zip')
    if zip:
        if full_address == '':
            full_address = zip


    try:
        location = locationHelper(full_address, zip)
        viewer = vals['viewer']
        viewer.location = location
        viewer.save()
    except:
        return HttpResponse("The given address was not specific enough to determine your voting district")

    return HttpResponse("success")


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
# FORM Edits group profile info
#-----------------------------------------------------------------------------------------------------------------------
def editGroup(request, vals={}):
    viewer = vals['viewer']

    g_id = request.POST.get('g_id')

    if not g_id:
        errors_logger.error('Group id not provided to editGroup action')
        return shortcuts.redirect('/')

    group = Group.lg.get_or_none(id=g_id)
    if not group:
        errors_logger.error('Group id #' + str(g_id) + ' not found in database.  Requested by editGroup action')
        return shortcuts.redirect('/')

    vals['group'] = group

    if viewer not in group.admins.all():
        return HttpResponseForbidden("You are not authroized to edit this group")

    if 'title' in request.POST: group.title = request.POST['title']
    if 'summary' in request.POST: group.summary = request.POST['summary']
    if 'full_text' in request.POST: group.full_text = request.POST['full_text']
    if 'group_privacy' in request.POST: group.group_privacy = request.POST['group_privacy']
    if 'scale' in request.POST: group.scale = request.POST['scale']

    if 'image' in request.FILES:
        try:
            file_content = ContentFile(request.FILES['image'].read())
            Image.open(file_content)
            group.setMainImage(file_content)
        except IOError:
            print "Image Upload Error"

    if group.group_privacy == 'S':
        group.in_feed = False
    else:
        group.in_feed = True

    group.save()

    return shortcuts.redirect('/' + str(group.alias) + '/edit/')

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
    from django.template import defaultfilters
    key = request.POST['key']
    if key not in CONTENT_EDITABLE_FIELDS:
        return HttpResponse( json.dumps({'success':True,'value':'Stop trying to break our site'}) )
    content = Content.lg.get_or_none(id=request.POST['c_id'])
    if content and viewer.id == content.getCreator().id:
        save_content = content.downcast()
        setattr( save_content , key , value )
        save_content.save()
        value = defaultfilters.urlize(value)
        value = defaultfilters.linebreaks_filter(value)
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
        action = Action(privacy=getPrivacy(request),relationship=rel)
        action.autoSave()
        comment.on_content.getCreator().notify(action)
        if not comment.on_content == comment.root_content:
            comment.root_content.getCreator().notify(action)
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
#-----------------------------------------------------------------------------------------------------------------------
def vote(request, vals):
    """Likes or dislikes content based on post."""
    user = vals['viewer']
    privacy = getPrivacy(request)
    content = Content.objects.get(id=request.POST['c_id'])
    vote = int(request.POST['vote'])

    value = voteAction(vote,user,content,privacy)

    to_return = { 'my_vote':value, 'status':content.status }
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# Saves a users answer to a question.
#-----------------------------------------------------------------------------------------------------------------------
def answer(request, vals={}):
    """ Saves a users answer to a question."""
    user = vals['viewer']
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = request.POST.get('questionPRI')
    my_response = user.view.responses.filter(question=question)
    if not privacy:
        privacy = getPrivacy(request)
    if 'choice' in request.POST:
        answer_id = request.POST['choice']
        weight = request.POST['weight']
        explanation = request.POST['explanation']
        response = answerAction(user=user, question=question, my_response=my_response,
                privacy=privacy, answer_id=answer_id, weight=weight, explanation=explanation)
        return HttpResponse(simplejson.dumps({'url': response.get_url(),'answer_avg':0}))
    else:
        if my_response:
            response = my_response[0]
            response.delete()
            user.num_answers -= 1
            user.save()
        return HttpResponse("+")


def stubAnswer(request, vals={}):
    user = vals['viewer']
    to_compare_id = request.POST.get('to_compare_id')
    if to_compare_id:
        to_compare = UserProfile.lg.get_or_none(id=to_compare_id)
    else:
        to_compare = None
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = request.POST['privacy']
    a_id = request.POST['a_id']
    weight = request.POST['weight']
    explanation = request.POST['explanation']
    my_response = user.view.responses.filter(question=question)
    response = answerAction(user=user, question=question, my_response=my_response,
        privacy=privacy, answer_id=a_id, weight=weight, explanation=explanation)
    vals['question'] = question
    vals['your_response'] = response
    their_response = getResponseHelper(responses=to_compare.view.responses.all(), question=question)
    vals['their_response'] = their_response
    vals['disagree'] = (their_response and their_response.most_chosen_answer_id != response.most_chosen_answer_id)
    vals['to_compare'] = to_compare
    html = ajaxRender('site/pages/qa/question_stub.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# recalculates comparison between viewer and to_compare, and returns match html in the desired display form
#-----------------------------------------------------------------------------------------------------------------------
def updateMatch(request, vals={}):
    viewer = vals['viewer']
    to_compare_alias = request.POST['to_compare_alias']
    to_compare = aliasToObject(to_compare_alias)
    comparison = to_compare.getComparison(viewer)
    vals['comparison_object'] = comparison
    vals['to_compare'] = to_compare
    vals['comparison'] = comparison.toBreakdown()
    display = request.POST['display']
    if display == 'vertical_breakdown':
        html = ajaxRender('site/pieces/match_breakdown/match_breakdown.html', vals, request)
    elif display == 'horizontal_breakdown':
        vals['horizontal'] = True
        html = ajaxRender('site/pieces/match_breakdown/match_breakdown.html', vals, request)
    elif display == 'sidebar_match':
        html = ajaxRender('site/pages/profile/sidebar_match.html', vals, request)
    elif display == 'has_answered':
        html = ajaxRender('site/pages/profile/has_answered_match.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))


#----------------------------------------------------------------------------------------------------------------------
# Joins group if user is not already a part.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupRequest(request, vals={}):
    """Joins group if user is not already a part."""
    viewer = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()  # Parties have a slightly different joinMember

    response = joinGroupAction(group,viewer,getPrivacy(request))

    return HttpResponse( json.dumps({'response':response}) )
#----------------------------------------------------------------------------------------------------------------------
# Confirms or rejects a user GroupJoined, if GroupJoined was requested.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupResponse(request, vals={}):
    viewer = vals['viewer']
    response = request.POST['response']
    from_user = UserProfile.objects.get(id=request.POST['follow_id'])
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast() # Parties have a slightly different joinMember

    if viewer not in group.admins.all():
        return HttpResponseForbidden("You are not authorized to respond to this group request")

    already = GroupJoined.objects.filter(user=from_user, group=group)
    if already:
        group_joined = already[0]
        if group_joined.confirmed:
            return HttpResponse("This person is already in your group")
        elif group_joined.requested:
            if response == 'Y':
                group.joinMember(from_user, privacy=getPrivacy(request))
                action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="A")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("they're now in your group")
            elif response == 'N':
                group_joined.reject()
                action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="X")
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("you have rejected their join request")
    return HttpResponse("this person has not requested to join you")

#----------------------------------------------------------------------------------------------------------------------
# Confirms or declines a group GroupJoined, if GroupJoined was invited.
#
#-----------------------------------------------------------------------------------------------------------------------
def groupInviteResponse(request, vals={}):
    from_user = vals['viewer'] # Viewer is always recieving/responding to the invite

    if not 'g_id' in request.POST:
        errors_logger.error("Group invite response sent without a group ID to user " + str(from_user.id) + ".")
        return HttpResponse("Group invite response sent without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        errors_logger.error("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to groupInviteResponse")
        return HttpResponse("Group with group ID #" + str(request.POST['g_id']) + " does not exist.")

    if not 'response' in request.POST:
        errors_logger.error("No response supplied to groupInviteResponse for group ID #" + str(group.id) )
    response = request.POST['response']

    # Find any groupJoined objects that exist
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if group_joined: # If there are any

        if group_joined.confirmed:
            errors_logger.error("User #" + str(from_user.id) + " responded to an invite to group #" + str(group.id) + " of which they are already a member")
            return HttpResponse("You have already joined that group")

        if group_joined.invited:
            if response == 'Y':
                group.joinMember(from_user, privacy=getPrivacy(request))
                action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="D")
                action.autoSave()
                for admin in group.admins.all():
                    admin.notify(action)
                return HttpResponse("you have joined this group!")

            elif response == 'N':
                group_joined.decline()
                action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="N")
                action.autoSave()
                for admin in group.admins.all():
                    admin.notify(action)
                return HttpResponse("you have rejected this group invitation")

    errors_logger.error("User #" + str(viewer.id) + " attempted to respond to a nonexistant group invite to group #" + str(group.id) )
    return HttpResponse("you were not invitied to join this group")

#----------------------------------------------------------------------------------------------------------------------
# Invites a set of users to a given group
#
#-----------------------------------------------------------------------------------------------------------------------
def groupInvite(request, vals={}):
    inviter = vals['viewer'] # Viewer is always sending the invite

    if not 'g_id' in request.POST:
        errors_logger.error("Group invite sent without a group ID by user " + str(inviter.id) + ".")
        return HttpResponse("Group invite sent without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        errors_logger.error("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to groupInvite by user #" + str(inviter.id))
        return HttpResponse("Group with group ID #" + str(request.POST['g_id']) + " does not exist.")

    if inviter not in group.admins.all():
        return HttpResponseForbidden("You are not authorized to send group invites for this group")

    if not 'invitees' in request.POST:
        errors_logger.error("Group invite sent without recieving user IDs for group #" + str(group.id) + " by user #" + str(inviter.id))
        return HttpResponse("Group invite sent without recieving user IDs")

    invitees = json.loads(request.POST['invitees'])

    for follow_id in invitees:
        individualGroupInvite(follow_id,group,inviter,request)

    return HttpResponse("invite success")

#----------------------------------------------------------------------------------------------------------------------
# Invites a single user to a given group
# HELPER FUNCTION TO groupInvite().
#-----------------------------------------------------------------------------------------------------------------------
def individualGroupInvite(follow_id, group, inviter, request):
    from_user = UserProfile.lg.get_or_none(id=follow_id)

    if not from_user:
        errors_logger.error("User with user ID #" + str(request.POST['follow_id']) + " does not exist.  Given to groupInvite by user #" + str(inviter.id))
        return False

    # Find any groupJoined objects that exist
    group_joined = GroupJoined.lg.get_or_none(user=from_user, group=group)
    if group_joined: # If there are any

        if group_joined.confirmed:
            errors_logger.error("User #" + str(from_user.id) + " was invited to group #" + str(group.id) + " of which they are already a member")
            return False

        elif group_joined.invited:
            normal_logger.debug("User #" + str(from_user.id) + " was reinvited to join group #" + str(group.id) )
            return False

        elif group_joined.requested:
            group.joinMember(from_user, privacy=getPrivacy(request))
            action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="D")
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

#----------------------------------------------------------------------------------------------------------------------
# Requests to follow inputted user.
#
#-----------------------------------------------------------------------------------------------------------------------
def userFollowRequest(request, vals={}):
    from_user = vals['viewer']
    to_user = UserProfile.objects.get(id=request.POST['p_id'])

    response = userFollowAction(from_user,to_user,getPrivacy(request))

    return HttpResponse( json.dumps({'response':response}) )

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
                action = Action(privacy=getPrivacy(request),relationship=user_follow,modifier='A')
                action.autoSave()
                from_user.notify(action)
                return HttpResponse("they're now following you")
            elif response == 'N':
                user_follow.reject()
                action = Action(privacy=getPrivacy(request),relationship=user_follow,modifier='X')
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
    if not to_user:
        LGException('User ID #' + str(from_user.id) + ' made a stop-follow post request with no to_user ID')
        return HttpResponse( json.dumps({'response':'failed'}) )

    userFollowStopAction(from_user,to_user,getPrivacy(request))

    return HttpResponse( json.dumps({'response':'removed'}) )


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
    viewer = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    group = group.downcast()

    if group.id == getLoveGovGroup().id:
        LGException('User ID #' + str(viewer.id) + ' attempted to leave the LoveGov group')
        return HttpResponse( json.dumps({'response':'fail'}) )

    leaveGroupAction(group,viewer,getPrivacy(request))

    return HttpResponse( json.dumps({'response':'removed'}) )

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


#----------------------------------------------------------------------------------------------------------------------
# Makes a set of users into moderators for a given group
#
#-----------------------------------------------------------------------------------------------------------------------
def removeAdmin(request, vals={}):
    viewer = vals['viewer']

    if not 'g_id' in request.POST:
        errors_logger.error("Admin removal without a group ID by user " + str(viewer.id) + ".")
        return HttpResponse("Admin removal without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        errors_logger.error("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to removeAdmin by user #" + str(viewer.id))
        return HttpResponse("Group with group ID #" + str(request.POST['g_id']) + " does not exist.")

    if viewer not in group.admins.all():
        HttpResponseForbidden("You do not have permission to remove an admin for this group")

    if not 'admin_id' in request.POST:
        errors_logger.error("Group admin removal without user ID for group #" + str(group.id) + " by user #" + str(viewer.id))
        return HttpResponse("Group admin removal without user ID")

    admin_remove = UserProfile.lg.get_or_none(id=request.POST['admin_id'])
    if not admin_remove:
        errors_logger.error("User with user ID #" + str(request.POST['follow_id']) + " does not exist.  Given to addAdmin by user #" + str(viewer.id))
        return HttpResponse("User with given ID does not exist")

    if admin_remove in group.admins.all():
        group.admins.remove(admin_remove)
    return HttpResponse("admin remove success")


#----------------------------------------------------------------------------------------------------------------------
# Makes a set of users into moderators for a given group
#
#-----------------------------------------------------------------------------------------------------------------------
def addAdmins(request, vals={}):
    viewer = vals['viewer'] # Viewer is always sending the invite

    if not 'g_id' in request.POST:
        errors_logger.error("Admin addition without a group ID by user " + str(viewer.id) + ".")
        return HttpResponse("Admin addition without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'])
    if not group:
        errors_logger.error("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to addAdmins by user #" + str(viewer.id))
        return HttpResponse("Group with group ID #" + str(request.POST['g_id']) + " does not exist.")

    if viewer not in group.admins.all():
        HttpResponseForbidden("You do not have permission to add an admin for this group")

    if not 'admins' in request.POST:
        errors_logger.error("Group admin addition without user IDs for group #" + str(group.id) + " by user #" + str(viewer.id))
        return HttpResponse("Group admin addition without user IDs")

    admins = json.loads(request.POST['admins'])

    for admin_id in admins:
        addAdmin(admin_id,group,viewer,request)

    vals['group_admins'] = group.admins.all()
    html = ajaxRender('site/pages/group/admin_list.html',vals,request)

    return HttpResponse(json.dumps({'html':html}))

#----------------------------------------------------------------------------------------------------------------------
# Adds a single user as moderator for a given group
# HELPER FUNCTION TO addAdmins().
#-----------------------------------------------------------------------------------------------------------------------
def addAdmin(admin_id, group, viewer, request):
    new_admin = UserProfile.lg.get_or_none(id=admin_id)

    if not new_admin:
        errors_logger.error("User with user ID #" + str(request.POST['follow_id']) + " does not exist.  Given to addAdmin by user #" + str(viewer.id))
        return False

    group.admins.add(new_admin)
    #TODO ADD ADMIN ACTIONS
#    action = Action(privacy=getPrivacy(request),relationship=group_joined,modifier="D")
#    action.autoSave()
#    from_user.notify(action)
    return True

#----------------------------------------------------------------------------------------------------------------------
# Removes a set of members from a group.
#
#-----------------------------------------------------------------------------------------------------------------------
def removeMembers(request, vals={}):

    viewer = vals['viewer']
    group = Group.lg.get_or_none(id=request.POST['g_id'])

    if viewer not in group.admins.all():
        HttpResponseForbidden("You do not have permission to remove members from this group.")

    if not 'members' in request.POST:
        errors_logger.error("Group member removal without user IDs for group #" + str(group.id) + " by user #" + str(viewer.id))
        return HttpResponse("Group member removal without user IDs")

    members = json.loads(request.POST['members'])

    for member_id in members:
        member = UserProfile.lg.get_or_none(id=member_id)
        if member:
            group.removeMember(member)

    vals['group_members'] = group.members.all()
    html = ajaxRender('site/pages/group/members_list.html',vals,request)

    return HttpResponse(json.dumps({'html':html}))


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
    comparison = object.getComparison(vals['viewer']).toBreakdown()
    vals['comparison'] = comparison
    vals['to_compare'] = object
    html = ajaxRender('site/pieces/comparison_hover_body.html', vals, request)
    to_return = {'html':html}
    return HttpResponse(json.dumps(to_return))

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
    html = ajaxRender('site/pages/match/match-new-box.html',vals,request)
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
    items = contentToFeedItems(content, vals['viewer'])
    vals['items']=items
    vals['display']=feed_display

    if feed_display == 'L':
        html = ajaxRender('site/pages/feed/linear_helper.html', vals, request)
        to_return = {'html':html, 'num':len(content)}
    else:
        cards = []
        for x in items:
            vals['item'] = x[0].downcast()
            vals['my_vote'] = x[1]
            card =  ajaxRender('site/pages/feed/pinterest.html', vals, request)
            cards.append(card)
        to_return = {'cards':json.dumps(cards), 'num':len(content)}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# get feed
#-----------------------------------------------------------------------------------------------------------------------
def getFeed(request, vals):

    feed_ranking = request.POST['feed_rank']
    feed_types = json.loads(request.POST['feed_types'])
    feed_start = int(request.POST['feed_start'])
    path = request.POST['path']
    alias = path.replace("/","")
    viewer = vals['viewer']
    content = getFeedItems(viewer=viewer, alias=alias, feed_ranking=feed_ranking,
        feed_types=feed_types, feed_start=feed_start, num=10)
    feed_items = contentToFeedItems(content, vals['viewer'])
    vals['feed_items'] = feed_items
    html = ajaxRender('site/pages/feed/feed_helper.html', vals, request)
    to_return = {'html':html, 'num_items':len(feed_items)}
    return HttpResponse(json.dumps(to_return))

def contentToFeedItems(content, user):
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

def getQuestions(request, vals):
    viewer = vals['viewer']
    feed_ranking = request.POST['feed_rank']
    question_ranking = request.POST['question_rank']
    feed_start = int(request.POST['feed_start'])
    feed_topic_alias = request.POST.get('feed_topic')
    to_compare_id = request.POST.get('to_compare_id')
    if to_compare_id:
        to_compare = UserProfile.lg.get_or_none(id=to_compare_id)
    else:
        to_compare = None
    if feed_topic_alias:
        feed_topic = Topic.lg.get_or_none(alias=feed_topic_alias)
    else:
        feed_topic = None

    if to_compare:
        question_items = getQuestionComparisons(viewer=viewer, to_compare=to_compare, feed_ranking=feed_ranking,
            question_ranking=question_ranking, feed_topic=feed_topic,
            feed_start=feed_start, num=10)
    else:
        question_items = getQuestionItems(viewer=viewer, feed_ranking=feed_ranking,
            feed_topic=feed_topic, feed_start=feed_start, num=10)
    vals['question_items']= question_items
    vals['to_compare'] = to_compare
    html = ajaxRender('site/pages/qa/question_feed_helper.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_items':len(question_items)}))

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
def updatePage(request, vals={}):

    viewer = vals['viewer']
    to_return = {}

    new_notifications = viewer.getNotifications(new=True)
    to_return['notifications_num'] = new_notifications.count()

    return HttpResponse(json.dumps(to_return))

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
        new_notifications = list(viewer.getNotifications(new=True))
        num_new = len(new_notifications)
        new_notifications = new_notifications[0:NOTIFICATION_INCREMENT+2]
        num_returned = len(new_notifications)
        num_still_new = num_new - num_returned

        old_notifications = None
        diff = NOTIFICATION_INCREMENT - num_returned
        if diff > 0:
            old_notifications = list(viewer.getNotifications(num=diff,old=True))

        for notification in new_notifications:
            notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )

        if old_notifications:
            for notification in old_notifications:
                notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )

    else:
        notifications = viewer.getNotifications(num=NOTIFICATION_INCREMENT,start=num_notifications)
        if not notifications:
            return HttpResponse(json.dumps({'error':'No more notifications'}))
        for notification in notifications:
            notifications_text.append( notification.getVerbose(view_user=viewer,vals=vals) )
        num_notifications += NOTIFICATION_INCREMENT

    vals['dropdown_notifications_text'] = notifications_text
    vals['num_notifications'] = num_notifications
    html = ajaxRender('site/pieces/notifications/notification_snippet.html', vals, request)
    if 'dropdown' in request.POST:
        html = ajaxRender('site/pieces/notifications/notification_dropdown.html', vals, request)
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
        actions_text.append( action.getVerbose(view_user=viewer, vals=vals) )
    vals['actions_text'] = actions_text
    num_actions += NOTIFICATION_INCREMENT
    vals['num_actions'] = num_actions
    html = ajaxRender('site/pieces/notifications/action_snippet.html', vals, request)
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
        actions_text.append( action.getVerbose(view_user=viewer, vals=vals) )
    vals['actions_text'] = actions_text
    num_actions += NOTIFICATION_INCREMENT
    vals['num_actions'] = num_actions
    html = ajaxRender('site/pieces/notifications/action_snippet.html', vals, request)
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
    print "member count: " + str(len(members))
    if len(members) == 0:
        return HttpResponse(json.dumps({'error':'No more members'}))
    vals['get_members'] = members
    num_members += MEMBER_INCREMENT
    vals['num_members'] = num_members
    html = ajaxRender('site/pieces/misc/member-snippet.html', vals, request)
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
    html = ajaxRender('site/snippets/group_snippet.html', vals, request)
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
        html = ajaxRender('site/pages/match/match-tryptic-template.html', vals, request)

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
        html = ajaxRender('site/pages/match/match-social-network.html', vals, request)

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
        html = ajaxRender('site/pages/match/match-social-network.html', vals, request)

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
                share_groups = groups.filter(id__in=group_ids)
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
            html += ajaxRender('site/pages/blog/blog-item.html',{'blogPost':blogPost},request)

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

            html = ajaxRender('site/pages/blog/blog-item.html',vals,request)
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
    html = ajaxRender('site/pages/histogram/avatars_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}

    return HttpResponse(json.dumps(to_return))

def getAllGroupMembers(request, vals={}):

    group = Group.objects.get(id=request.POST['g_id'])
    start = int(request.POST['start'])
    num = int(request.POST['num'])
    members = group.getMembers(start=start, num=num)

    vals['users'] = members
    how_many = len(members)
    html = ajaxRender('site/pages/histogram/avatars_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}

    return HttpResponse(json.dumps(to_return))

def likeThis(request, vals={}):

    html = ajaxRender('site/pages/feed/like_this.html', vals, request)
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
        html = ajaxRender('site/pieces/snippets/content-privacy.html', vals, request)
    to_return = {'html':html, 'error': error}
    print "to_return: "+ str(to_return)
    return HttpResponse(json.dumps(to_return))


def getAggregateNotificationUsers(request, vals={}):
    # Get Notification first
    viewer = vals['viewer']
    n_id = request.POST.get('n_id')

    if not n_id:
        errors_logger.error('No notification supplied for retrieving aggregate notifications users.  User ID = #' + str(viewer.id) )
        return HttpResponse(json.dumps({'html':'An error occurred.  The developers have been notified'}))

    agg_notification = Notification.lg.get_or_none(id=n_id)
    if not agg_notification:
        errors_logger.error('Invalid notification ID given to function getAggregateNotificationsUsers. Invalid ID = #' + str(n_id) + ' and Viewer ID = #' + str(viewer.id))
        return HttpResponse(json.dumps({'html':'An error occurred.  The developers have been notified'}))

    n_action = Action.lg.get_or_none(id=agg_notification.action_id)
    if not n_action:
        errors_logger.error('Invalid action in Notification given to function getAggregateNotificationsUsers. Notification ID = #' + str(n_id) )
        return HttpResponse(json.dumps({'html':'An error occurred.  The developers have been notified'}))

    relationship = Relationship.lg.get_or_none(id=n_action.relationship_id)
    if not relationship:
        errors_logger.error('Invalid relationship in action given to function getAggregateNotificationsUsers. action ID = #' + str(n_action.id) + ' and Notification ID = #' + str(n_id) )
        return HttpResponse(json.dumps({'html':'An error occurred.  The developers have been notified'}))

    vals['agg_notification_type'] = n_action.type
    vals['agg_notification_content'] = relationship.getTo()
    vals['agg_notification_users'] = agg_notification.users.all()
    vals['agg_notification_anon'] = agg_notification.anon_users.count()

    html = ajaxRender('site/pieces/notifications/aggregate-notifications-popup.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))


def getSigners(request, vals={}):
    html = ''
    viewer = vals['viewer']
    error = ''
    petition_id = request.GET.get('petition_id')
    if petition_id:
        if Petition.lg.get_or_none(id=petition_id):
            petition = Petition.lg.get_or_none(id=petition_id)
            vals['signers'] = petition.signers.all()
            html = ajaxRender('site/snippets/petition-signers.html', vals, request)
        else:
            error = 'The given petition identifier is invalid.'
    else:
        error = 'No petition identifier given.'
    to_return = {'html':html, 'error': error}
    response = HttpResponse(json.dumps(to_return))
    response.status_code = 500 if error else 200
    return response

def setFirstLoginStage(request, vals={}):
    viewer = vals['viewer']
    stage = request.POST.get('stage')
    error = ''
    if stage:
        viewer.first_login = stage
        viewer.save()
    else:
        error = 'No first login stage given.'
    to_return = {'error': error}
    response = HttpResponse(json.dumps(to_return))
    response.status_code = 500 if error else 200
    return response

#-----------------------------------------------------------------------------------------------------------------------
# saves the posted incompatability information to the db
#-----------------------------------------------------------------------------------------------------------------------
def logCompatability(request, vals={}):
    incompatible = json.loads(request.POST['incompatible'])
    user = vals.get('viewer')
    CompatabilityLog(incompatible=incompatible, user=user,
        page=getSourcePath(request), ipaddress=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')).autoSave()
    return HttpResponse('compatability logged')

#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all actions. [checks is post]
# post: actionPOST - which actionPOST to call
#-----------------------------------------------------------------------------------------------------------------------
def actionPOST(request, vals={}):
    """Splitter between all actions."""
    if request.user:
        vals['viewer'] = getUserProfile(request)
    if not 'action' in request.REQUEST:
        return HttpResponseBadRequest('No action specified.')
    action = request.REQUEST['action']
    if action not in ACTIONS:
        return HttpResponseBadRequest('The specified action ("%s") is not valid.' % (action))
    elif action in vals['prohibited_actions']:
        return HttpResponseForbidden("You are not permitted to perform the action \"%s\"." % action)
    else:
        action_func = action + '(request, vals)'
        return eval(action_func)


#-----------------------------------------------------------------------------------------------------------------------
# Splitter between all modals
#-----------------------------------------------------------------------------------------------------------------------
def getModal(request,vals={}):
    modal_name = request.POST.get('modal_name')
    modal_html = ''

    if modal_name == "invite_modal":
        pass
    elif modal_name == "group_invite_modal":
        modal_html = "Yay! It works."

    if modal_html:
        return HttpResponse( json.dumps({'modal_html':modal_html}) )
    else:
        raise LGException( "invalid modal name requested: " + str(modal_name) )