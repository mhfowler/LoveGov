########################################################################################################################
########################################################################################################################
#
#           Actions
#
#
########################################################################################################################
########################################################################################################################

from lovegov.modernpolitics.modals import *
from django.core.files.base import ContentFile

#-----------------------------------------------------------------------------------------------------------------------
# register from login page via form
#-----------------------------------------------------------------------------------------------------------------------
def newRegister(request,vals={}):

    # get params from post
    valid = True
    name = request.POST['name']
    email = request.POST['email']
    email2 = request.POST['email2']
    password = request.POST['password']
    day = request.POST['day']
    month = request.POST['month']
    year = request.POST['year']
    zip = request.POST['zip']
    privacy = int(request.POST['privacy'])
    form_type = request.POST['form_type']

    # validate form
    if not email:
        vals['email_error'] = 'This field is required.'
        valid = False
    if not email2:
        vals['email2_error'] = 'This field is required.'
        valid = False
    if email and email2:
        if email != email2:
            vals['email_error'] = "Both emails must be the same."
        else:
            splitted = email.split("@")
            if len(splitted)!=2:
                vals['email_error'] = "Please enter a valid email address."
                valid = False
            elif not checkUnique(email):
                vals['email_error'] = "Someone already registered with this email."
                valid = False

    if not password and not form_type=="twitter_register":     # password is not required if it is twitter registration
        vals['password_error'] = 'This field is required.'
        valid = False

    if not (day and month and year):
        vals['dob_error'] = 'Day, month and year of birth are required.'
        valid = False
    else:
        try:
            day = int(day)
            month = int(month)
            year = int(year)
            if (year > 2012):
                vals['dob_error'] = "You must already be born to register."
                valid = False
            elif (year < 1900):
                vals['dob_error'] = "Year must be above 1900."
                valid = False
            elif (day>31 or day<0):
                vals['dob_error'] = "Please enter a day between 1 and 31."
                valid = False
            elif (month>12 or month <0):
                vals['dob_error'] = "Please enter a month between 1 and 12."
                valid = False
        except:
            vals['dob_error'] = "Day, month and year of birth must be numbers."
            valid = False

    if not privacy:
        vals['privacy_error'] = 'click'
        valid = False

    if not name:
        vals['name_error'] = "This field is required."
        valid = False
    else:
        splitted = name.split()
        if len(splitted) < 2:
            vals['name_error'] = "You must enter a first and last name."
            valid = False

    # if twitter registration, check for twitter stuff in request
    if form_type=="twitter_register":
        from lovegov.modernpolitics.twitter import tatHelper
        tat = tatHelper(request)
        if tat:                                                 # ready to twitter register
            twitter_user_id = tat['user_id']
            already = UserProfile.lg.get_or_none(twitter_user_id = twitter_user_id)
            if already:
                vals['twitter_error'] = "There is already a user registered with your twitter id. Try signing in again."
                valid=False
        else:
            vals['twitter_error'] = "You are not authenticated with twitter. Try clicking the twitter button again."

    # if form is not valid, then rerender the form and return it (to replace the old form)
    if not valid:
        vals['name'] = name
        vals['email'] = email
        vals['email2'] = email2
        vals['day'] = day
        vals['month'] = month
        vals['year'] = year
        vals['zip'] = zip
        vals['privacy'] = privacy
        vals['form_type'] = form_type
        html = ajaxRender('site/pages/login/new_register_form.html', vals, request)
        return HttpResponse(json.dumps({'html':html}))

    # if form is valid register the user
    else:

        # if no inputted password, generate random password (for twitter registration)
        if not password:
            password = generateRandomPassword(10)

        # create user profile form form data
        user_profile = registerHelper(name=name, email=email, password=password, day=day, month=month, year=year, zip=zip)

        # send a confirmation email based on type of registration
        if form_type=='twitter_register':
            user_profile.twitter_user_id = tat['user_id']
            user_profile.twitter_screen_name = tat['screen_name']
            user_profile.save()
            vals['name'] = user_profile.get_name()
            vals['email'] = user_profile.email
            vals['password'] = password
            vals['confirmation_link'] = user_profile.confirmation_link
            sendTemplateEmail(subject="Welcome to LoveGov", template="twitterRegister.html", dictionary=vals, email_sender='info@lovegov.com', email_recipient=email)
        else:
            confirmation_link = user_profile.confirmation_link
            vals = {'firstname':user_profile.first_name,'link':confirmation_link}
            sendTemplateEmail("LoveGov Confirmation E-Mail","confirmLink.html",vals,"info@lovegov.com",user_profile.email)

        # return success, causes redirect to success page on client side
        return HttpResponse(json.dumps({"success":True, 'email':email, 'name':name}))

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

            for num in range(len(image_refs)):
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

            html = ajaxRender('site/pieces/news-link-autogen.html', vals, request)
            return HttpResponse(json.dumps({'html':html}))
        else:
            return HttpResponseBadRequest("Something went wrong.")
    except:
        return HttpResponseBadRequest("Something went wrong parsing the page.")

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
    groups = SearchQuerySet().models(Group).filter(content=term,hidden=False)

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
    html = ajaxRender('site/frame/searchbar/autocomplete.html', vals, request)
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
        action = CreatedAction(privacy=getPrivacy(request),content=c)
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
def signPetition(request, vals={}):
    from lovegov.frontend.views_helpers import valsPetition
    viewer = vals['viewer']
    privacy = getPrivacy(request)
    p_id = int(request.POST['p_id'])
    error = None
    if privacy == 'PUB':
        petition = Petition.lg.get_or_none(id=p_id)
        if not petition:
            return HttpResponse("This petition does not exist")
        if petition.finalized:
            if petition.sign(viewer):
                pass
            else:
                LGException(viewer.get_name() +  "|have already signed this petition|" + petition.get_name())
        else:
            LGException(viewer.get_name() +  "|has not been finalized|" + petition.get_name())
    else:
        error = "You must be in public mode to sign a petition."
    if not error:
        valsPetition(viewer, petition, vals)
        signers_sidebar = ajaxRender('site/pages/content_detail/signers_sidebar.html', vals, request)
        sign_area = ajaxRender('site/pages/content_detail/petition_sign_area.html', vals, request)
    else:
        signers_sidebar = sign_area = error
    return HttpResponse(json.dumps({'signers_sidebar':signers_sidebar,'sign_area':sign_area}))

def finalizePetition(request, vals={}):
    from lovegov.frontend.views_helpers import valsPetition
    viewer = vals['viewer']
    p_id = int(request.POST['p_id'])
    petition = Petition.objects.get(id=p_id)
    creator = petition.getCreator()
    if viewer==creator:
        petition.finalize()
    valsPetition(viewer, petition, vals)
    signers_sidebar = ajaxRender('site/pages/content_detail/signers_sidebar.html', vals, request)
    sign_area = ajaxRender('site/pages/content_detail/petition_sign_area.html', vals, request)
    return HttpResponse(json.dumps({'signers_sidebar':signers_sidebar,'sign_area':sign_area}))

#-----------------------------------------------------------------------------------------------------------------------
# run for or stop running for an election
#-----------------------------------------------------------------------------------------------------------------------
def runForElection(request, vals={}):
    from lovegov.frontend.views_helpers import valsElection
    e_id = request.POST['e_id']
    election = Election.objects.get(id=e_id)
    run = int(request.POST['run'])
    viewer = vals['viewer']
    election = runForElectionAction(viewer, election, run)
    vals['info'] = valsElection(viewer, election, {})
    html = ajaxRender('site/pages/elections/run_for_button.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# changes address for a user
#-----------------------------------------------------------------------------------------------------------------------
def submitAddress(request, vals={}):

    viewer = vals['viewer']
    try:
        location = postLocationHelper(request)
        viewer.setNewLocation(location)
        viewer.joinLocationGroups()
    except:
        return HttpResponse(json.dumps({'success':-1}))

    return HttpResponse(json.dumps({'success':1}))


def submitTempAddress(request, vals={}):
    viewer = vals['viewer']
    try:
        location = postLocationHelper(request)
        viewer.setNewTempLocation(location)
    except:
        return HttpResponse(json.dumps({'success':-1}))

    return HttpResponse(json.dumps({'success':1}))


# returns a new location based on inputted parameters
def postLocationHelper(request):
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    zip = request.POST.get('zip')
    location = PhysicalAddress()
    location.save()
    location = locationHelper(address=address, city=city, state=state, zip=zip, location=location)
    return location

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
        try:
            if 'age' in request.POST: viewer.age = int(request.POST['age'])
        except:
            pass

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
            if str(party_type[1])+"_party" in request.POST:
                party = Party.lg.get_or_none( party_type=party_type[0] )
                party.joinMember(viewer)
                all_parties.remove(party)

        for party in all_parties:
            party.removeMember(viewer)

        viewer.bio = request.POST['bio']
        viewer.save()
        return shortcuts.redirect('/settings/profile/')

    return shortcuts.redirect('/settings/')

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
    from django.template import defaultfilters
    viewer = vals['viewer']

    if not 'val' in request.POST or not 'key' in request.POST:
        LGException( "Edit profile request sent without either value, key, or content ID.  Sent by ID #" + str(viewer.id) )
        return HttpResponseBadRequest( 'Edit profile request missing vital information.' )

    value = request.POST['val']
    key = request.POST['key']

    if key not in USERPROFILE_EDITABLE_FIELDS:
        LGException( "Edit profile request sent for not editable field.  Sent by ID #" + str(viewer.id) + " on content ID #" + str(content.id) )
        return HttpResponseBadRequest( 'Invalid profile edit request.  Stop trying to break out site' )

    setattr( viewer , key , value )
    viewer.save()

    value = defaultfilters.urlize(value)
    value = defaultfilters.linebreaksbr(value)

    return HttpResponse( json.dumps({'value':value}) )

#-----------------------------------------------------------------------------------------------------------------------
# INLINE Edits user profile information
#-----------------------------------------------------------------------------------------------------------------------
def editContent(request, vals={}):
    from django.template import defaultfilters
    viewer = vals['viewer']

    if not 'val' in request.POST or not 'key' in request.POST or not 'c_id' in request.POST:
        LGException( "Edit content request sent without either value, key, or content ID.  Sent by ID #" + str(viewer.id) )
        return HttpResponseBadRequest( 'Edit content request missing vital information.' )

    value = request.POST['val']
    key = request.POST['key']

    content = Content.lg.get_or_none(id=request.POST['c_id'])
    if not content:
        LGException( "Edit content request sent with invalid content ID #" + str(request.POST['c_id']) )
        return HttpResponseBadRequest( 'Edit content request sent with invalid content ID' )

    if key not in CONTENT_EDITABLE_FIELDS:
        LGException( "Edit content request sent for not editable field.  Sent by ID #" + str(viewer.id) + " on content ID #" + str(content.id) )
        return HttpResponseBadRequest( 'Invalid content edit request.  Stop trying to break out site' )

    downcast_content = content.downcast()

    authorized = False
    ## Check if this user is authorized ##
    if downcast_content.type == "G" and viewer in downcast_content.admins.all():
        authorized = True
    elif viewer.id == downcast_content.getCreator().id:
        authorized = True

    if not authorized:
        LGException( "Edit content request sent by unauthorized user ID #" + str(viewer.id) + " on content ID #" + str(content.id) )
        return HttpResponseForbidden( 'You are not authorized to edit this field.' )

    setattr( downcast_content , key , value )
    downcast_content.save()

    value = defaultfilters.urlize(value)
    value = defaultfilters.linebreaksbr(value)

    return HttpResponse( json.dumps({'value':value}) )

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
        deleted = DeletedAction(user=user, content=content, privacy=getPrivacy(request))
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
        # save action and send notification
        action = CreatedAction(user=user,privacy=getPrivacy(request),content=comment)
        action.autoSave()
        comment.on_content.getCreator().notify(action)
        if not comment.on_content == comment.root_content:
            comment.root_content.getCreator().notify(action)
        depth = int(request.POST.get('depth', 0))
        from lovegov.frontend.views_helpers import renderComment 
        html = '<div class="threaddiv">'
        html += renderComment(request, vals, comment, depth)
        html += '</div>'
        return HttpResponse(html)
    else:
        if request.is_ajax():
            to_return = {'errors':[]}
            for e in comment_form.errors:
                to_return['errors'] = to_return['errors'].append(e)
            return HttpResponse(simplejson.dumps(to_return))
        else:
            vals = {'message':'Comment post failed'}
            return renderToResponseCSRF('usable/message.html',vals,request)

def appendComment(request, vals={}):
    user = vals['viewer']
    privacy = getPrivacy(request)
    c_id = request.POST.get('c_id', None)
    text = request.POST.get('comment', None)
    if c_id:
        comment = Comment.lg.get_or_none(id=c_id)
        if comment:
            if text:
                appended_text = comment.text + '\n' + text
                comment.text = appended_text
                comment.save()
                from django.template import defaultfilters
                appended_text = defaultfilters.linebreaks_filter(appended_text)
                appended_text = defaultfilters.urlize(appended_text)
                return HttpResponse(appended_text)
    return HttpResponseBadRequest("Something was wrong with the request.")

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
    if not privacy:
        privacy = getPrivacy(request)
    if 'choice' in request.POST:
        answer_id = request.POST['choice']
        weight = request.POST['weight']
        explanation = request.POST['explanation']
        response = answerAction(user=user, question=question, privacy=privacy, answer_id=answer_id, weight=weight, explanation=explanation )
        return HttpResponse(simplejson.dumps({'url': response.get_url(),'answer_avg':0}))
    else:
        my_response = user.view.responses.filter(question=question)
        if my_response:
            response = my_response[0]
            response.delete()
            user.num_answers -= 1
            user.save()
        return HttpResponse("+")

def stubAnswer(request, vals={}):
    user = vals['viewer']
    to_compare_id = request.POST.get('to_compare_id')
    if to_compare_id and to_compare_id != 'null':
        to_compare = UserProfile.lg.get_or_none(id=to_compare_id)
    else:
        to_compare = None
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = request.POST['privacy']
    a_id = request.POST['a_id']
    weight = request.POST['weight']
    explanation = request.POST['explanation']
    if explanation == 'explain your answer':
        explanation = ""
    your_response = answerAction(user=user, question=question,privacy=privacy, answer_id=a_id, weight=weight, explanation=explanation)
    vals['question'] = question
    vals['your_response'] = your_response
    responses = []
    if to_compare:
        their_response = getResponseHelper(responses=to_compare.view.responses.all(), question=question)
        if their_response:
            responses.append(their_response)
    responses.append(your_response)
    vals['compare_responses'] = responses
    vals['default_display'] = request.POST.get('default_display')
    html = ajaxRender('site/pages/qa/question_stub.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

def saveAnswer(request, vals={}):
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = request.POST.get("privacy")
    if not privacy:
        privacy = getPrivacy(request)
    a_id = request.POST['a_id']
    weight = int(request.POST['weight'])
    viewer = vals['viewer']
    your_response = answerAction(user=viewer, question=question,privacy=privacy, answer_id=a_id, weight=weight)
    vals['question'] = question
    vals['your_response'] = your_response
    vals['default_display'] = request.POST.get('default_display')

    responses = []
    # get scorecard response if it is there
    scorecard_id = request.POST.get('scorecard_id')
    if scorecard_id:
        scorecard = Scorecard.objects.get(id=scorecard_id)
        scorecard_response = getResponseHelper(responses=scorecard.scorecard_view.responses.all(), question=question)
        if scorecard_response:
            responses.append({'response':scorecard_response,'responder':scorecard})
    # get to_compare response if it is there
    to_compare_id = request.POST.get('to_compare_id')
    if to_compare_id and to_compare_id != 'null':
        to_compare = UserProfile.lg.get_or_none(id=to_compare_id)
        their_response = getResponseHelper(responses=to_compare.view.responses.all(), question=question)
        if their_response:
            responses.append({'response':their_response,'responder':to_compare})
    responses.append({'response':your_response,'responder':viewer})
    vals['compare_responses'] = responses

    html = ajaxRender('site/pages/qa/question_stub.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

def saveScorecardAnswer(request, vals):
    question = Question.objects.get(id=request.POST['q_id'])
    a_id = request.POST['a_id']
    user = vals['viewer']
    scorecard = Scorecard.objects.get(id=request.POST['scorecard_id'])
    if scorecard.getPermissionToEdit(user):
        if question in scorecard.poll.questions.all():
            scorecard_response = scorecardAnswerAction(user=user, scorecard=scorecard, question=question,answer_id=a_id)
            vals['question'] = question
            vals['your_response'] = scorecard_response
            vals['default_display'] = request.POST.get('default_display')
            responses = []
            vals['compare_responses'] = responses
            html = ajaxRender('site/pages/qa/question_stub.html', vals, request)
            return HttpResponse(json.dumps({'html':html}))
        else:
            LGException("user " + str(user.id) + " trying to answer question for scorecard which isn't on scorecard poll")
            return HttpResponse("didn't work")
    else:
        LGException("user " + str(user.id) + " trying to edit scorecard which they are not allowed to." + str(scorecard.id))
        return HttpResponse("didnt' work")

def saveAnswerInFeed(request, vals):
    question = Question.objects.get(id=request.POST['q_id'])
    privacy = request.POST.get("privacy")
    if not privacy:
        privacy = getPrivacy(request)
    a_id = request.POST['a_id']
    viewer = vals['viewer']
    your_response = answerAction(user=viewer, question=question,privacy=privacy, answer_id=a_id)
    return HttpResponse("saved")

def changeAnswerPrivacy(request, vals):

    viewer = vals['viewer']
    q_id = request.POST['q_id']
    r_id = request.POST.get("r_id")
    if r_id:
        response = Response.objects.get(id=r_id)
    else:
        question = Question.objects.get(id=q_id)
        response = answerAction(user=viewer, question=question,privacy=getPrivacy(request), answer_id=-1)
    if viewer == response.creator:
        if response.getPublic():
            response.setPrivate()
            privacy = "PRI"
        else:
            response.setPublic()
            privacy = "PUB"
        vals['your_response'] = response
        vals['anonymous'] = response.getPrivate()
        vals['q_id'] = q_id
        html = ajaxRender('site/pages/qa/answer_privacy.html', vals, request)
        return HttpResponse(json.dumps({'html':html, 'privacy':privacy}))
    else:
        LGException("trying to change privacy of response that was not their own. u_id:" + str(viewer.id))
        return HttpResponse("didn't work")

def editExplanation(request, vals):

    viewer = vals['viewer']
    explanation = request.POST['explanation']
    q_id = request.POST['q_id']
    r_id = request.POST.get("r_id")
    if r_id:
        response = Response.objects.get(id=r_id)
    else:
        question = Question.objects.get(id=q_id)
        response = answerAction(user=viewer, question=question,privacy=getPrivacy(request), answer_id=-1)
    if viewer == response.creator:
        response.explanation = explanation
        response.save()
        return HttpResponse(json.dumps({'explanation':explanation}))
    else:
        LGException("trying to edit explanation of response that was not their own. u_id:" + str(viewer.id))
        return HttpResponse("didn't work")

#-----------------------------------------------------------------------------------------------------------------------
# recalculates comparison between viewer and to_compare, and returns match html in the desired display form
#-----------------------------------------------------------------------------------------------------------------------
def updateMatch(request, vals={}):
    viewer = vals['viewer']
    to_compare_alias = request.POST['to_compare_alias']
    to_compare = aliasToObject(to_compare_alias)
    display = request.POST['display']
    vals['to_compare'] = to_compare
    if display == 'comparison_web':
        comparison, web_json = to_compare.getComparisonJSON(viewer)
        vals['web_json'] = web_json
    else:
        comparison = to_compare.getComparison(viewer)
        vals['comparison_object'] = comparison
        vals['comparison'] = comparison.toBreakdown()
    if display == 'vertical_breakdown':
        html = ajaxRender('site/pieces/match_breakdown/match_breakdown.html', vals, request)
    elif display == 'horizontal_breakdown':
        vals['horizontal'] = True
        html = ajaxRender('site/pieces/match_breakdown/match_breakdown.html', vals, request)
    elif display == 'sidebar_match':
        html = ajaxRender('site/pages/profile/sidebar_match.html', vals, request)
    elif display == 'has_answered':
        html = ajaxRender('site/pages/profile/has_answered_match.html', vals, request)
    elif display == 'comparison_web':
        html = ajaxRender('site/pages/qa/comparison_web.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# rerenders an html piece and returns it (with new db stuff from some other venue)
#-----------------------------------------------------------------------------------------------------------------------
def updateStats(request, vals={}):
    viewer = vals['viewer']
    object = request.POST['object']
    if object == 'poll_stats':
        from lovegov.frontend.views_helpers import getQuestionStats
        p_id = request.POST['p_id']
        poll = Poll.lg.get_or_none(id=p_id)
        getQuestionStats(vals, poll)
        html = ajaxRender('site/pages/qa/poll_progress_by_topic.html', vals, request)
    elif object == 'you_agree_with':
        from lovegov.frontend.views_helpers import getGroupTuples
        question = Question.objects.get(id=request.POST['q_id'])
        response = viewer.view.responses.filter(question=question)
        if response:
            response = response[0]
        vals['response'] = response
        vals['question'] = question
        if response:
            vals['group_tuples'] = getGroupTuples(viewer, question, response)
            html = ajaxRender('site/pages/qa/you_agree_with_stats.html', vals, request)
        else:
            html = "<p> answer to see how many people agree with you. </p>"
    elif object == 'poll_progress':
        from lovegov.frontend.views_helpers import getPollProgress
        poll = Poll.objects.get(id=request.POST['p_id'])
        poll_progress = getPollProgress(viewer, poll)
        vals['poll'] = poll
        vals['poll_progress'] = poll_progress
        html = ajaxRender('site/pages/qa/poll_progress.html', vals, request)
    elif object == 'petition_bar':
        petition = Petition.objects.get(id=request.POST['p_id'])
        vals['petition'] = petition
        html = ajaxRender('site/pages/content_detail/petition_bar.html', vals, request)
    elif object == 'profile_stats':
        profile = UserProfile.objects.get(id=request.POST['p_id'])
        vals['profile'] = profile
        html = ajaxRender('site/pages/profile/profile_stats.html', vals, request)
    elif object == 'election_leaderboard':
        from lovegov.frontend.views_helpers import valsElection
        election = Election.objects.get(id=request.POST['e_id'])
        vals['info'] = valsElection(viewer, election, {})
        html = ajaxRender('site/pages/elections/election_leaderboard.html', vals, request)
    elif object == 'like_minded_counter':
        html = ajaxRender('site/pages/groups/like_minded_counter.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#----------------------------------------------------------------------------------------------------------------------
# gets html for next poll question
#-----------------------------------------------------------------------------------------------------------------------
def getNextPollQuestion(request, vals={}):
    viewer = vals['viewer']
    p_id = int(request.POST['p_id'])
    which = int(request.POST['which'])
    direction = request.POST['direction']
    if direction == 'R':
        next = which+1
    else:
        next = which-1
    poll = Poll.objects.get(id=p_id)
    questions = poll.questions.all()
    num_questions = questions.count()
    if next < 0 : next = (num_questions-1)
    elif next > (num_questions-1): next=0
    question = questions[next]
    vals['question'] = question
    vals['poll'] = poll
    vals['which'] = next
    response = viewer.getResponseToQuestion(question)
    vals['your_response'] = response
    html = ajaxRender('site/pages/content_detail/poll_sample.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#----------------------------------------------------------------------------------------------------------------------
# Joins group if user is not already a part.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupRequest(request, vals={}):
    """Joins group if user is not already a part."""
    viewer = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'], system=False)
    group = group.downcast()  # Parties have a slightly different joinMember

    joinGroupAction(group,viewer,getPrivacy(request))

    from lovegov.frontend.views_helpers import valsGroupButtons
    vals['info'] = valsGroupButtons(viewer, group, {})
    vals['group'] = group
    html = ajaxRender('site/pages/group/group_join_button.html', vals, request)
    return HttpResponse( json.dumps({'html':html}) )

#----------------------------------------------------------------------------------------------------------------------
# Confirms or rejects a user GroupJoined, if GroupJoined was requested.
#
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupResponse(request, vals={}):
    viewer = vals['viewer']

    from_user = UserProfile.objects.get(id=request.POST['follow_id'])
    group = Group.objects.get(id=request.POST['g_id'], system=False)
    group = group.downcast() # Parties have a slightly different joinMember

    if viewer not in group.admins.all():
        LGException( "User ID #" + str(viewer.id) + " attempted to respond to a join request for group ID #" + str(group.id) )
        return HttpResponseForbidden("You are not authorized to respond to this group request")

    if not 'response' in request.POST:
        LGException("No response supplied to joinGroupResponse for group ID #" + str(group.id) )
        return HttpResponseBadRequest("Group request response sent without response text.")

    response = request.POST['response']

    result = joinGroupResponseAction(group,from_user,response,viewer,getPrivacy(request))

    return HttpResponse( json.dumps({ 'success':result }) )

#----------------------------------------------------------------------------------------------------------------------
# Confirms or declines a group GroupJoined, if GroupJoined was invited.
#
#-----------------------------------------------------------------------------------------------------------------------
def groupInviteResponse(request, vals={}):
    from_user = vals['viewer'] # Viewer is always recieving/responding to the invite

    if not 'g_id' in request.POST:
        LGException("Group invite response sent without a group ID to user " + str(from_user.id) + ".")
        return HttpResponseBadRequest("Group invite response sent without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'], system=False)
    if not group:
        LGException("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to groupInviteResponse")
        return HttpResponseBadRequest("Group invite response sent with invalid group ID.")

    if not 'response' in request.POST:
        LGException("No response supplied to groupInviteResponse for group ID #" + str(group.id) )
        return HttpResponseBadRequest("Group invite response sent without response text.")

    response = request.POST['response']

    result = groupInviteResponseAction(group,from_user,response,getPrivacy(request))

    return HttpResponse( json.dumps({ 'success':result }) )

#----------------------------------------------------------------------------------------------------------------------
# Invites a set of users to a given group
#
#-----------------------------------------------------------------------------------------------------------------------
def groupInvite(request, vals={}):
    inviter = vals['viewer'] # Viewer is always sending the invite

    if not 'g_id' in request.POST:
        LGException("Group invite sent without a group ID by user " + str(inviter.id) + ".")
        return HttpResponseBadRequest("Group invite sent without a group ID")

    group = Group.lg.get_or_none(id=request.POST['g_id'], system=False)
    if not group:
        LGException("Group with group ID #" + str(request.POST['g_id']) + " does not exist.  Given to groupInvite by user #" + str(inviter.id))
        return HttpResponseBadRequest("Group invite sent with invalid group ID.")

    if inviter not in group.admins.all():
        return HttpResponseForbidden("You are not authorized to send group invites for this group")

    if not 'invitees' in request.POST:
        LGException("Group invite sent without recieving user IDs for group #" + str(group.id) + " by user #" + str(inviter.id))
        return HttpResponseBadRequest("Group invite sent without recieving user ID(s)")

    invitees = json.loads(request.POST['invitees'])

    for follow_id in invitees:
        from_user = UserProfile.lg.get_or_none(id=follow_id)

        if not from_user:
            LGException("User with user ID #" + str(request.POST['follow_id']) + " does not exist.  Given to groupInvite by user ID #" + str(inviter.id))
            continue

        groupInviteAction(from_user,group,inviter,getPrivacy(request))

    return HttpResponse("invite success")

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

    response = request.POST.get('response')
    if not response:
        LGException( "User ID #" + str(to_user.id) + " submitted a user follow response with response" )
        return HttpResponseBadRequest("No response in user follow response.")

    from_id = request.POST.get('p_id')
    if not from_id:
        LGException( "User ID #" + str(to_user.id) + " submitted a user follow response with no user ID" )
        return HttpResponseBadRequest("No user id in user follow response.")

    from_user = UserProfile.lg.get_or_none(id=from_id)
    if not from_user:
        LGException( "User ID #" + str(to_user.id) + " submitted a user follow response with invalid user ID #" + str(from_id)  )
        return HttpResponseBadRequest("Invalid user id in user follow response.")

    response = userFollowResponseAction(from_user,to_user,response,getPrivacy(request))

    return HttpResponse( json.dumps({'response':response}) ) # RETURN NOT CURRENTLY BEING USED


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

#-----------------------------------------------------------------------------------------------------------------------
# supports or unsupports a politician based on posted value of 'support'
#-----------------------------------------------------------------------------------------------------------------------
def supportPolitician(request, vals={}):
    viewer = vals['viewer']
    p_id = request.POST['p_id']
    politician = UserProfile.lg.get_or_none(id=p_id, politician=True)
    if not politician:
        LGException(viewer.get_name() + " tried to support a user who was not a politician|" + str(p_id))
        return HttpResponse("not politician.")
    support = request.POST['support']
    vals['politician'] = politician
    support_bool = False
    if support == 'true':
        support_bool = True
    supportAction(viewer, politician, support_bool, getPrivacy(request))
    vals['is_user_supporting'] = support_bool
    html = ajaxRender('site/pages/profile/support_button.html',vals,request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# follows or unfollows a group based on value of follow
#-----------------------------------------------------------------------------------------------------------------------
def followGroup(request, vals={}):
    viewer = vals['viewer']
    g_id = request.POST['g_id']
    group = Group.lg.get_or_none(id=g_id)
    follow = request.POST['follow']
    vals['group'] = group
    follow_bool = False
    if follow == 'true':
        follow_bool = True
    followGroupAction(viewer, group, follow_bool, getPrivacy(request))
    vals['is_user_following'] = follow_bool
    html = ajaxRender('site/pages/group/group_follow_button.html',vals,request)
    to_return = {'html':html, 'href':group.get_url(), 'group_type':group.group_type}
    if follow_bool:
        vals['x'] = group
        navlink = ajaxRender('site/pages/home/navbar_snippet.html', vals, request)
        to_return['navlink_html'] = navlink
    return HttpResponse(json.dumps(to_return))

#----------------------------------------------------------------------------------------------------------------------
# Invites inputted user to join group.
#-----------------------------------------------------------------------------------------------------------------------
def joinGroupInvite(request, vals={}):
    """Invites inputted to join group, if inviting user is admin."""
    user = vals['viewer']
    to_invite = UserProfile.objects.get(id=request.POST['invited_id'])
    group = Group.objects.get(id=request.POST['g_id'], system=False)
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

    if group.system:
        LGException('User ID #' + str(viewer.id) + ' attempted to leave system group,' + str(group.id))
        return HttpResponse( json.dumps({'response':'fail'}) )

    leaveGroupAction(group,viewer,getPrivacy(request))

    from lovegov.frontend.views_helpers import valsGroupButtons
    vals['info'] = valsGroupButtons(viewer, group, {})
    vals['group'] = group
    html = ajaxRender('site/pages/group/group_join_button.html', vals, request)
    return HttpResponse( json.dumps({'html':html}) )

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

def hoverWebComparison(request, vals={}):
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
    html = ajaxRender('site/pages/match/match-new-box.html',vals,request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# reloads html for thread
#-----------------------------------------------------------------------------------------------------------------------
def ajaxThread(request, vals={}):
    from lovegov.frontend.views import makeThread
    content = Content.objects.get(id=request.POST['c_id'])
    user = vals['viewer']
    limit = int(request.POST.get('limit', 500))
    start = int(request.POST.get('start', 0))
    thread, top_count = makeThread(request, content, user, vals=vals, start=start, limit=limit)
    to_return = {'html':thread, 'top_count': top_count}
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

    # if no items, return a random picture of a politician
    num_items = len(feed_items)
    if not num_items:
        p = random.choice(UserProfile.objects.filter(politician=True))
        vals['politician'] = p
        everything_loaded = ajaxRender('site/pages/microcopy/everything_loaded.html', vals, request)
    else:
        everything_loaded = ""

    to_return = {'html':html, 'num_items':num_items, 'everything_loaded':everything_loaded}
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
    p_id = request.POST.get('p_id')
    scorecard_id = request.POST.get('scorecard_id')
    if p_id:
        poll = Poll.objects.get(id=p_id)
    else:
        poll = None
    if scorecard_id:
        scorecard = Scorecard.objects.get(id=scorecard_id)
    else:
        scorecard = None
    only_unanswered_string = request.POST['only_unanswered']
    only_unanswered = only_unanswered_string == 'true'
    if to_compare_id and to_compare_id != 'null':
        to_compare = UserProfile.lg.get_or_none(id=to_compare_id)
    else:
        to_compare = None
    if feed_topic_alias:
        feed_topic = Topic.lg.get_or_none(alias=feed_topic_alias)
    else:
        feed_topic = None
    if to_compare:
        question_items = getQuestionComparisons(viewer=viewer, to_compare=to_compare, feed_ranking=feed_ranking,
            question_ranking=question_ranking, feed_topic=feed_topic, scorecard=scorecard, feed_start=feed_start, num=10)
    else:
        question_items = getQuestionItems(viewer=viewer, feed_ranking=feed_ranking,
            feed_topic=feed_topic,  poll=poll, scorecard=scorecard,
            only_unanswered=only_unanswered, feed_start=feed_start, num=10)
    vals['question_items']= question_items
    vals['to_compare'] = to_compare
    vals['default_display'] = request.POST.get('default_display')

    html = ajaxRender('site/pages/qa/feed_helper_questions.html', vals, request)
    return HttpResponse(json.dumps({'html':html, 'num_items':len(question_items)}))

#-----------------------------------------------------------------------------------------------------------------------
# get groups
#-----------------------------------------------------------------------------------------------------------------------
def getGroups(request, vals={}):
    from lovegov.frontend.views_helpers import valsGroup
    viewer = vals['viewer']
    groups = Group.objects.filter(hidden=False).order_by("-num_members")

    # filter by location
    state = request.POST['state']
    city = request.POST['city']
    if city and state and state != 'all':
        groups = groups.filter(location__state=state, location__city=city)
    elif state and state != 'all':
        groups = groups.filter(location__state=state)

    feed_start = int(request.POST['feed_start'])
    groups = groups[feed_start:feed_start+5]

    vals['groups'] = groups
    groups_info = []
    for count,g in enumerate(groups):
        group_vals = {}
        valsGroup(viewer, g, group_vals)
        groups_info.append({'group':g, 'info':group_vals, 'num':feed_start+count+1})
    vals['groups_info'] = groups_info

    html = ajaxRender('site/pages/browse/feed_helper_browse_groups.html', vals, request)
    return HttpResponse(json.dumps({'html':html, 'num_items':len(groups)}))

#-----------------------------------------------------------------------------------------------------------------------
# get elections
#-----------------------------------------------------------------------------------------------------------------------
def getElections(request, vals={}):
    from lovegov.frontend.views_helpers import valsElection
    viewer = vals['viewer']
    elections = Election.objects.order_by("-num_members")
    feed_start = int(request.POST['feed_start'])
    elections = elections

    # filter by location
    state = request.POST['state']
    city = request.POST['city']
    if city and state and state != 'all':
        elections = elections.filter(location__state=state, location__city=city)
    elif state and state != 'all':
        elections = elections.filter(location__state=state)


    # paginate
    elections = elections[feed_start:feed_start+5]

    vals['elections'] = elections
    elections_info = []
    for count,e in enumerate(elections):
        group_vals = {}
        valsElection(viewer, e, group_vals)
        elections_info.append({'group':e, 'info':group_vals, 'num':feed_start+count+1})
    vals['elections_info'] = elections_info

    html = ajaxRender('site/pages/browse/feed_helper_browse_elections.html', vals, request)
    return HttpResponse(json.dumps({'html':html, 'num_items':len(elections_info)}))

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
            notifications_text.append( notification.getVerbose(viewer=viewer,vals=vals) )

        if old_notifications:
            for notification in old_notifications:
                notifications_text.append( notification.getVerbose(viewer=viewer,vals=vals) )

    else:
        notifications = viewer.getNotifications(num=NOTIFICATION_INCREMENT,start=num_notifications)
        if not notifications:
            return HttpResponse(json.dumps({'error':'No more notifications'}))
        for notification in notifications:
            notifications_text.append( notification.getVerbose(viewer=viewer,vals=vals) )
        num_notifications += NOTIFICATION_INCREMENT

    vals['dropdown_notifications_text'] = notifications_text
    vals['num_notifications'] = num_notifications
    html = ajaxRender('site/frame/notifications/notification_snippet.html', vals, request)
    if 'dropdown' in request.POST:
        html = ajaxRender('site/frame/notifications/notification_dropdown.html', vals, request)
    return HttpResponse(json.dumps({'html':html,'num_notifications':num_notifications,'num_still_new':num_still_new}))

#-----------------------------------------------------------------------------------------------------------------------
# gets user activity feed
#-----------------------------------------------------------------------------------------------------------------------
def getUserActivity(request, vals={}):
    # Get Actions
    viewer = vals['viewer']

    if not 'p_id' in request.POST:
        LGException( 'User ID #' + str(viewer.id) + " requested user activity without submitting a user ID" )
        return HttpResponseBadRequest("User activity requested without a user ID")

    user_prof = UserProfile.lg.get_or_none(id=request.POST['p_id'])
    if not user_prof:
        LGException( 'User ID #' + str(viewer.id) + " requested the user activity of an invalid user ID #" + str(request.POST['p_id']) )
        return HttpResponseBadRequest("User activity requested from an invalid user ID")

    num_actions = 0
    if 'feed_start' in request.POST:
        num_actions = int(request.POST['feed_start'])

    actions = user_prof.getActivity(num=NOTIFICATION_INCREMENT,start=num_actions)

    num_actions += len(actions)

    actions_text = []
    for action in actions:
        action_text = action.getVerbose(viewer=viewer, vals=vals)
        actions_text.append(action_text)

    vals['actions_text'] = actions_text

    html = ajaxRender('site/pieces/actions/action_snippet.html', vals, request)
    return HttpResponse( json.dumps({'html':html,'feed_start':num_actions,'num_items':len(actions)}) )


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
        actions_text.append( action.getVerbose(viewer=viewer, vals=vals) )
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
    increment = int(request.POST.get('increment') or MEMBER_INCREMENT)
    print num_members
    members = group.getMembers(num=increment,start=num_members)
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
def getUsersByUID(request, vals={}):

    viewer = vals['viewer']
    u_ids = json.loads(request.POST['u_ids'])
    members = UserProfile.objects.filter(id__in=u_ids).order_by('id')
    display = request.POST['display']
    vals['display'] = display

    vals['users'] = members
    how_many = len(members)
    if display=='strip':
        for u in members:
            u.comparison = u.getComparison(viewer)
    html = ajaxRender('site/pieces/render_users_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}

    return HttpResponse(json.dumps(to_return))


def getGroupMembersForDisplay(request, vals={}):

    viewer = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    start = int(request.POST['start'])
    num = int(request.POST['num'])
    display = request.POST['display']
    vals['display'] = display
    members = group.getMembers(start=start, num=num)

    vals['users'] = members
    how_many = len(members)
    if display=='strip':
        for u in members:
            u.comparison = u.getComparison(viewer)
    html = ajaxRender('site/pieces/render_users_helper.html', vals, request)
    to_return = {'html':html, 'num':how_many}
    return HttpResponse(json.dumps(to_return))

#-----------------------------------------------------------------------------------------------------------------------
# misc
#-----------------------------------------------------------------------------------------------------------------------
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
# saves a link click on some news
#-----------------------------------------------------------------------------------------------------------------------
def logLinkClick(request, vals):
    news = News.objects.get(id=request.POST['n_id'])
    news.link_clicks += 1
    news.save()
    return HttpResponse("saved")

#-----------------------------------------------------------------------------------------------------------------------
# Creates a piece of content, e.g. from the create modal
#-----------------------------------------------------------------------------------------------------------------------
def createContent(request, vals={}):
    # Get possible values from post request
    section = request.POST.get('sectionType')
    title = request.POST.get('title')
    full_text = request.POST.get('full_text')
    post_to = request.POST.get('post_to')
    group = None
    if post_to:
        group = Group.lg.get_or_none(id=post_to)
    post_as = request.POST.get('post_as')
    image = request.POST.get('content-image')
    link = request.POST.get('link')
    screenshot = request.POST.get('screenshot')
    viewer = vals['viewer']
    questions = request.POST.get('questions')
    topic_alias = request.POST.get('topic')
    topic = Topic.lg.get_or_none(alias=topic_alias)
    poll_id = request.POST.get('poll')
    gendate = request.POST.get('gendate')
    state = request.POST.get('state')
    city = request.POST.get('city')
    if poll_id:
        poll = Poll.lg.get_or_none(id=poll_id)
    if questions: questions = json.loads(questions)
    if post_as == 'user':
        privacy = 'PUB'
    elif post_as == 'anonymous':
        privacy = 'PRI'
    else:
        privacy = 'PUB'
    redirect = ''
    if section=='discussion':
        if title and full_text:
            newc = Discussion(user_post=full_text, title=title, in_feed=True, in_search=True, in_calc=True,
                                        posted_to=group)
            newc.autoSave(creator=viewer, privacy=privacy)
            try:
                if 'content-image' in request.FILES:
                    file_content = ContentFile(request.FILES['content-image'].read())
                    Image.open(file_content)
                    newc.setMainImage(file_content)
            except IOError:
                return HttpResponseBadRequest("Image Upload Error")
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='petition':
        if title and full_text:
            newc = Petition(full_text=full_text, title=title, in_feed=True, in_search=True, in_calc=True,
                                        posted_to=group)
            newc.autoSave(creator=viewer, privacy=privacy)
            try:
                if 'content-image' in request.FILES:
                    file_content = ContentFile(request.FILES['content-image'].read())
                    Image.open(file_content)
                    newc.setMainImage(file_content)
            except IOError:
                return HttpResponseBadRequest("Image Upload Error")
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='news':
        if link:
            newc = News(link=link)
            ref = str(screenshot)
            if ref != 'undefined':
                newc.saveScreenShot(ref)
            newc.autoSave(creator=viewer, privacy=privacy)
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='poll':
        if title and full_text:
            newc = Poll(description=full_text, summary=full_text, title=title, in_feed=True, in_search=True, in_calc=True,
                posted_to=group)
            newc.autoSave()
            for q in questions:
                newQ = Question(question_text=q['question'], title=q['question'], source=q['source'], official=False)
                newQ.save()
                for a in q['answers']:
                    newA = Answer(answer_text=a, value=-1)
                    newA.save()
                    newQ.addAnswer(newA)
                newQ.save()
                newc.addQuestion(newQ)
            newc.autoSave(creator=viewer, privacy=privacy)
            try:
                if 'content-image' in request.FILES:
                    file_content = ContentFile(request.FILES['content-image'].read())
                    Image.open(file_content)
                    newc.setMainImage(file_content)
            except IOError:
                return HttpResponseBadRequest("Image Upload Error")
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='group':
        if title and full_text:
            newc = Group(title=title, full_text=full_text, in_feed=True, in_search=True, in_calc=True)
            newc.autoSave(creator=viewer, privacy=privacy)
            try:
                if 'content-image' in request.FILES:
                    file_content = ContentFile(request.FILES['content-image'].read())
                    Image.open(file_content)
                    newc.setMainImage(file_content)
            except IOError:
                return HttpResponseBadRequest("Image Upload Error")
            if state:
                newPhyAddr = PhysicalAddress(state=state,city=city)
                newPhyAddr.save()
            newc.location = newPhyAddr
            newc.save()
            newc.joinMember(viewer)
            newc.addAdmin(viewer)
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='scorecard':
        if title and full_text:
            newc = Scorecard(title=title, full_text=full_text, in_feed=True, in_search=True, in_calc=True,
                group=group, poll=poll)
            newc.autoSave(creator=viewer, privacy=privacy)
            redirect = newc.getEditURL()
        else:
            return HttpResponseBadRequest("A required field was not included.")
    elif section=='election':
        if title and full_text and gendate:
            try:
                from dateutil import parser
                valid_datetime = parser.parse(gendate)
            except ValueError:
                return HttpResponseBadRequest("Could not parse election date.")
            from datetime import datetime
            newc = Election(title=title, full_text=full_text, in_feed=True, in_search=True, in_calc=True,
                    election_date=valid_datetime)
            newc.autoSave(creator=viewer, privacy=privacy)
            if state:
                newPhyAddr = PhysicalAddress(state=state,city=city)
                newPhyAddr.save()
            newc.joinMember(viewer)
            newc.addAdmin(viewer)
        else:
            return HttpResponseBadRequest("A required field was not included.")
    else:
        return HttpResponseBadRequest("The specified type of content is not valid.")


    newc.setMainTopic(topic)

    action = CreatedAction(content=newc,user=viewer,)

    if not redirect:
        redirect = newc.getUrl()

    return HttpResponseRedirect(redirect);

#-----------------------------------------------------------------------------------------------------------------------
# asks a politicain to join the website
#-----------------------------------------------------------------------------------------------------------------------
def askToJoin(request, vals={}):

    viewer = vals['viewer']
    politician = UserProfile.objects.get(ghost=True, id=request.POST['p_id'])

    already = AskedAction.lg.get_or_none(user=viewer, politician=politician)
    if not already:
        asked = AskedAction(user=viewer, politician=politician)
        asked.autoSave()
    return HttpResponse("asked to join")

#-----------------------------------------------------------------------------------------------------------------------
# stores that this person wanted to claim a politician profile
#-----------------------------------------------------------------------------------------------------------------------
def claimProfile(request, vals={}):

    viewer = vals['viewer']
    politician = UserProfile.objects.get(ghost=True, id=request.POST['p_id'])
    email = request.POST['email']

    if email:
        claim = ClaimProfile(user=viewer, politician=politician, email=email)
        claim.autoSave()

    return HttpResponse("asked to claim profile")

#-----------------------------------------------------------------------------------------------------------------------
# sends a message to politician
#-----------------------------------------------------------------------------------------------------------------------
def messagePolitician(request, vals={}):

    viewer = vals['viewer']
    message = request.POST['message']
    politician = UserProfile.objects.get(politician=True, id=request.POST['p_id'])
    phone_number = request.POST['phone_number']

    messaged = MessagedAction(user=viewer, message=message, politician=politician, phone_number=phone_number)
    messaged.autoSave()

    return HttpResponse("success")

#-----------------------------------------------------------------------------------------------------------------------
# gets fb friend snippet html for invite sidebar
#-----------------------------------------------------------------------------------------------------------------------
def getFBInviteFriends(request, vals={}):
    from lovegov.frontend.views_helpers import valsFBFriends
    valsFBFriends(request, vals)
    html =  ajaxRender('site/pages/friends/fb_invite_friends_helper.html', vals, request)
    return HttpResponse(json.dumps({'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# calculate like minded group members
#-----------------------------------------------------------------------------------------------------------------------
def findLikeMinded(request, vals={}):
    viewer = vals['viewer']
    new_members, num_processed = viewer.findLikeMinded()
    vals['display'] = 'avatar'
    vals['users'] = new_members
    html = ajaxRender('site/pieces/render_users_helper.html', vals, request)
    return HttpResponse(json.dumps({"num_new_members":len(new_members), 'num_processed':num_processed, 'html':html}))

#-----------------------------------------------------------------------------------------------------------------------
# calculate like minded group members
#-----------------------------------------------------------------------------------------------------------------------
def clearLikeMinded(request, vals={}):
    viewer = vals['viewer']
    viewer.clearLikeMinded()
    return HttpResponse("cleared")

#-----------------------------------------------------------------------------------------------------------------------
# pin a piece of content to a group
#-----------------------------------------------------------------------------------------------------------------------
def pinContent(request, vals={}):
    viewer = vals['viewer']
    group = Group.objects.get(id=request.POST['g_id'])
    content = Content.objects.get(id=request.POST['c_id'])
    pin = int(request.POST['pin'])
    if pin==1:
        pinContentAction(viewer=viewer, content=content, group=group, privacy=getPrivacy(request))
    else:
        unpinContentAction(viewer=viewer, content=content, group=group, privacy=getPrivacy(request))
    vals['content'] = content
    vals['group'] = group
    success_link = ajaxRender('site/pages/content_detail/pin_content_success.html', vals, request)
    return HttpResponse(json.dumps({'html':success_link}))

#-----------------------------------------------------------------------------------------------------------------------
# edit a petitions full text
#-----------------------------------------------------------------------------------------------------------------------
def editPetitionFullText(request, vals={}):
    petition = Petition.objects.get(id=request.POST['p_id'])
    viewer = vals['viewer']
    if viewer == petition.creator and not petition.finalized:
        full_text = request.POST['full_text']
        petition.full_text = full_text
        petition.save()
        action = EditedAction(user=viewer, content=petition, privacy = getPrivacy(request))
        action.autoSave()
        return HttpResponse(json.dumps({'value':full_text}))
    else:
        LGException( "User editing petition and is finalized or is not owner #" + str(viewer.id) )
        return HttpResponse("didnt work")

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
    ## Get the basics ##
    viewer = vals['viewer']
    modal_name = request.POST.get('modal_name')
    modal_html = ''

    ## Modal Switch ##
    ##################

    ## Invite Modal ##
    if modal_name == "group_requests_modal":
        # Get group ID
        if 'g_id' in request.POST:
            g_id = request.POST['g_id']
        else: # If there's no group ID, exception
            LGException( "Group requests modal requested without group ID by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Group requests requested without a group ID" )
            # and Group
        group = Group.lg.get_or_none(id=g_id)
        # If there's no group matching that ID, raise an exception
        if not group:
            LGException( "Group requests modal requested for invalid group ID #" + str(g_id) + " by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Group requests requested with an invalid group ID" )
        modal_html = getGroupRequestsModal(group,viewer,request,vals)


    ## Group Invite Modal ## Where a user invites someone to their group
    elif modal_name == "group_invite_modal":
        # Get group ID
        if 'g_id' in request.POST:
            g_id = request.POST['g_id']
        else: # If there's no group ID, exception
            LGException( "group invite modal requested without group ID by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Group invite modal requested without a group ID" )
        # and Group
        group = Group.lg.get_or_none(id=g_id)
        # If there's no group matching that ID, raise an exception
        if not group:
            LGException( "group invite modal requested for invalid group ID #" + str(g_id) + " by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Group invite modal requested with an invalid group ID" )

        modal_html = getGroupInviteModal(group,viewer,request,vals)


    ## Group Invited Modal ## Where a user see's his or her gropu invites
    elif modal_name == "group_invited_modal":
        modal_html = getGroupInvitedModal(viewer,request,vals)


    ## Group Invite Modal ##
    elif modal_name == "follow_requests_modal":
        modal_html = getFollowRequestsModal(viewer,request,vals)


    ## Facebook Share Modal ##
    elif modal_name == "facebook_share_modal":
        fb_name = request.POST.get('fb_name')
        fb_share_id = request.POST.get('fb_share_id')

        if not fb_share_id:
            LGException( "Facebook Share modal requested without facebook share ID by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Facebook Share modal requested without facebook share ID" )

        modal_html = getFacebookShareModal(fb_share_id,fb_name,request,vals)

    ## create modal ##
    elif modal_name == "create_modal":
       modal_html = getCreateModal(request,vals)

    ## message politician modal ##
    elif modal_name == "message_politician":
        politician = UserProfile.objects.get(id=request.POST['p_id'])
        modal_html = getMessagePoliticianModal(politician, request,vals)

    ## Pin Content Modal ##
    elif modal_name == "pin_content_modal":
        c_id = request.POST.get('c_id')

        if not c_id:
            LGException( "Pin content modal requested without content ID by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Pin content modal requested without content ID" )

        content = Content.lg.get_or_none( id=c_id )

        if not content:
            LGException( "Pin content modal requested with invalid content ID #" + str(c_id) + " by user ID #" + str(viewer.id) )
            return HttpResponseBadRequest( "Pin content modal requested with invalid content ID" )

        modal_html = getPinContentModal(content,viewer,request,vals)


    ## get full group description ##
    elif modal_name == 'group_description':
        g_id = request.POST['g_id']
        group = Group.objects.get(id=g_id)
        modal_html = getGroupDescriptionModal(group,request,vals)

    ## see all signers ##
    elif modal_name == 'see_all_signers_modal':
        p_id = request.POST['p_id']
        petition = Petition.objects.get(id=p_id)
        modal_html = getPetitionSignersModal(petition, request, vals)


    ## If a modal was successfully made, return it ##
    if modal_html:
        return HttpResponse( json.dumps({'modal_html':modal_html}) )
    ## Otherwise raise an exception with an invalid modal name ##
    else:
        LGException( "invalid modal name requested: " + str(modal_name) )
        return HttpResponseBadRequest( "Invalid modal requested" )
