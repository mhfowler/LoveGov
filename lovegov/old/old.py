
#=======================================================================================================================
# Form for registering.
#=======================================================================================================================
class SimpleRegisterForm(forms.Form):
    name = RegisterNameField()
    email = RegisterEmailField()
    password = RegisterPasswordField()
    #-------------------------------------------------------------------------------------------------------------------
    # Checks valid email, and adds errors if necessary and sends us request email.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        # custom clean
        if self.cleaned_data.has_key('email'):
            emailList = ValidEmail.objects.filter(email=self.cleaned_data['email'])
            extension = (str(self.cleaned_data['email']).split('@'))[1]
            emailExtension = ValidEmailExtension.objects.filter(extension=extension)
            # if not valid extension or on list give error message and send request to join email
            if not (emailList or emailExtension):
                error_msg = u"This email isn't in our Beta records. We are currently testing the site with a limited number of users. We will let you know when you can join!"
                self._errors['email'] = self.error_class([error_msg])
                # save email
                save_email = EmailList(email=self.cleaned_data['email'])
                save_email.save()
            else:
                if emailList:
                    self.confirmedEmail = True  # THIS IS BAD ASSUMPTION will change
                if emailExtension:
                    self.confirmedEmail = False
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Saves new user and emails confirmation link appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def save(self):
        data = self.cleaned_data    # for ease of reference
        control = backend.createUserHelper(name=data['name'], email=data['email'], password=data['password'])
        # set authentication backend (not facebook)
        control.backend = 'django.contrib.auth.backends.ModelBackend'
        control.save()
        userProfile = control.user_profile
        if self.confirmedEmail:
            userProfile.confirmed = True
            userProfile.save()
            return control
        else:
            userProfile.confirmed = False
            userProfile.save()
            backend.sendConfirmationEmail(userProfile=userProfile)
            return None











#=======================================================================================================================
# Form for registering a new user.
#
#
#=======================================================================================================================
class RegisterForm(forms.Form):
    name = RegisterNameField()
    dob = RegisterBirthField()
    email = RegisterEmailField()
    email2 = RegisterEmailField()
    password = RegisterPasswordField()
    password2 = RegisterPasswordField()
    security_q = RegisterSecurityQField()
    security_a = RegisterSecurityAField()

    #-------------------------------------------------------------------------------------------------------------------
    # Validates form data and returns cleaned data with any errors.
    #-------------------------------------------------------------------------------------------------------------------
    def clean(self):
        self.checkValidEmail()
        self.checkMatchingFields("email","email2")
        self.checkMatchingFields("password","password2")
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if two fields match in the submitted data and returns appropriate error message.
    #-------------------------------------------------------------------------------------------------------------------
    def checkMatchingFields(self, field1, field2):
        if self.cleaned_data.has_key(field1) and self.cleaned_data.has_key(field2):
            field1_data = self.cleaned_data.get(field1)
            field2_data = self.cleaned_data.get(field2)
            if field1_data != field2_data:
                error_msg = u"Please enter the same " + field1 + u" in both " + field1 + u" fields"
                self._errors[field1] = self.error_class([error_msg])
                self._errors[field2] = self.error_class([error_msg])
                del self.cleaned_data[field1]
                del self.cleaned_data[field2]
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if the email entered is a valid Brown e-mail
    #-------------------------------------------------------------------------------------------------------------------
    def checkValidEmail(self):
        if self.cleaned_data.has_key('email') and self.cleaned_data.has_key('email2'):
            extension = (str(self.cleaned_data['email']).split('@'))[1]
            emailExtension = ValidEmailExtension.objects.filter(extension=extension)
            emailFromList = ValidEmail.objects.filter(email=self.cleaned_data.get('email'))
            if emailExtension.count()==0 and emailFromList.count()==0:
                error_msg = u"Please enter an e-mail flagged for beta testing"
                self._errors['email'] = self.error_class([error_msg])
                self._errors['email2'] = self.error_class([error_msg])
                del self.cleaned_data["email"]
                del self.cleaned_data["email2"]
        return self.cleaned_data

    #-------------------------------------------------------------------------------------------------------------------
    # saves a user form form, using default values appropriately.
    # - new_data (form data)
    #-------------------------------------------------------------------------------------------------------------------
    def save(self, new_data):
        # create new UserProfile object with entered email and password
        userProfile = UserProfile.objects.create_user(new_data['email'],'email', new_data['password'])
        # split name into first and last
        names = str.split(new_data['name'])
        userProfile.first_name = names[0]
        if len(names)==2:
            userProfile.last_name = names[1]
        userProfile.is_active = True
        userProfile.save()
        # reference to id of newly created profile
        newid = userProfile.id
        # create user's basic info record
        newBasicInfo = BasicInfo(id=newid)
        birthdate = new_data['dob_year'] + "-" + new_data['dob_month'] + '-' + new_data['dob_day']
        newBasicInfo.dob = birthdate
        newBasicInfo.save()
        #create user's profile page record
        newProfilePage = ProfilePage(person=userProfile)
        newProfilePage.save()
        # create users worldview...
        world_view = WorldView()
        world_view.save()
        userProfile.view_id = world_view.id
        # synchronize id's for all user records
        userProfile.basicinfo_id = newid
        # save random confirmation link (and email to user)
        userProfile.confirmation_link = str(random.randint(1,999999))           # TODO: make cryptographically safe
        userProfile.save()
        return userProfile



########################################################################################################################
########################################################################################################################
#
# Create-Content Forms
#
########################################################################################################################
########################################################################################################################

#=======================================================================================================================
# Content Form
#   - Abstract Form for all Content forms
#
#=======================================================================================================================
class ContentForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')

#=======================================================================================================================
# Petition Form
#
#
#=======================================================================================================================
class PetitionForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        to_return.active = True
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['petition'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['petition'])

#=======================================================================================================================
# Event Form
#
#
#=======================================================================================================================
class EventForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text', 'datetime_of_event', 'topics', 'type')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['event'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['event'])
    datetime_of_event = SelectDateTimeField()

#=======================================================================================================================
# News form.
#
#
#=======================================================================================================================
class NewsForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = News
        fields = ('link', 'title', 'summary', 'topics', 'type')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['news'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['news'])

#=======================================================================================================================
# Group form.
#
#
#=======================================================================================================================
class GroupForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Group
        fields = ('title', 'group_type', 'summary','full_text', 'topics','type')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        to_return.save()
        creator = UserProfile.objects.get(id=request.user.id)
        to_return.admins.add(creator)
        to_return.members.add(creator)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['group'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['group'])

#=======================================================================================================================
# Debate form.
#
#
#=======================================================================================================================
class DebateForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = Debate
        fields = ('title', 'summary','debate_when')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['debate'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['debate'])

#=======================================================================================================================
# Album form.
#
#
#=======================================================================================================================
class UserImageForm(ContentForm):
    # PRIVATE CLASSES
    class Meta:
        model = UserImage
        fields = ('title', 'summary','topics')
        # METHODS
    def complete(self,request):
        to_return = self.save(commit=False)
        file_content = ContentFile(request.FILES['image'].read())
        to_return.createImage(file_content)
        return to_return
        # FIELDS
    topics = SelectTopicsField(content_type=TYPE_DICT['image'])
    type = forms.CharField(widget=forms.HiddenInput(), initial=TYPE_DICT['image'])
    image = forms.FileField()


#=======================================================================================================================
# Upload Forms
#
#
#=======================================================================================================================
class UploadFileForm(forms.Form):
    image = forms.FileField()
class UploadImageForm(forms.Form):
    image = forms.ImageField()


########################################################################################################################
# Create-Content-Simple Forms
#
#
########################################################################################################################

class PetitionForm_simple(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='P')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

class EventForm_simple(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'summary', 'full_text', 'topics', 'type')
    date_of_event = forms.DateTimeField()
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='E')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

class NewsForm_simple(forms.ModelForm):
    class Meta:
        model = News
        fields = ('title', 'summary', 'link', 'topics', 'type')
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=widgets.CheckboxSelectMultiple)
    type = forms.CharField(widget=forms.HiddenInput(), initial='N')
    def complete(self,request):
        to_return = self.save(commit=False)
        return to_return

#=======================================================================================================================
# BasicInfo form
#
#
#=======================================================================================================================
class BasicInfoForm(forms.ModelForm):
    class Meta:
        model = BasicInfo
    dob = forms.DateField(required=False,initial=datetime.datetime.now().date())



    # old

########################################################################################################################
########################################################################################################################
# These classes are used to generate the feed.  Accesses.py uses these classes.
#
# Class ScoreType
#   - stores total score for each topic
#   - stores subscores based on content type
#
# Class OldFeed
#   - calculates from UserContentRelationship the probability weights for each topic based on the user's actions
#   - (example: Topic 1 Weight = Topic 1 Score / Total Score of all topics)
#   - calculates the content type in a similar fashion as above
#   - generates a (topic, type) tuple
#   - retrieves latest 10 UserContentRelationships matching the generated (topic, type) tuple
#   - calculates probability weights from value of these 10 matches
#   - selects with weighted probabilities the Content to deliver to the feed
########################################################################################################################
########################################################################################################################

CONTENT_TYPE = ('E', 'P', 'N', 'L', 'Q', 'R', 'G', 'C', 'I', 'A', 'Z', 'D')

TOPICS = list(Topic.objects.all().values_list('topic_text', flat=True))

########################################################################################################################


# cache questions
class QUESTIONS:
    objects = Question.objects.all()

# cache topics
class TOPICS:
    objects = Topic.objects.all()


FEED_CONTENT = ['E', 'P', 'N']

RELATIONSHIP_CHOICES = (
    ('L','likes'),
    ('D','dislikes'),
    ('?', 'complicated'),
    ('C','created'),
    ('S', 'shared'),
    ('F','following'),
    ("I", 'involved')
    )

def getRelationshipValue(relationship):
    if relationship == 'L':
        return 1.0
    elif relationship == 'D':
        return -1.0
    elif relationship == 'C':
        return 10.0
    elif relationship == 'S':
        return 5.0
    elif relationship == 'F':
        return 5.0
    else:
        return 1.0


class ScoreType:
    def __init__(self):
        self.totalScore = 0.0
        self.typeScores = {}
        for type in CONTENT_TYPE:
            self.typeScores[type] = 0.0

    ###### PRIVATE METHODS ######

    # adds the value to the appropriate type
    def addScore(self, type, value):
        self.typeScores[type] += value
        self.totalScore += value

    # normalizes the total score to [0,1]
    def normalizeTotalScore(self, scoreSum):
        if self.totalScore > 0.0:
            self.totalScore = self.totalScore / scoreSum

    # normalizes the type scores to [0,1]
    def normalizeTypeScores(self):
        if self.totalScore > 0.0:
            for score in self.typeScores.iterkeys():
                self.typeScores[score] = self.typeScores[score] / self.totalScore

    # gets the total score
    def getTotalScore(self):
        return self.totalScore

    # gets the type score
    def getTypeScore(self,type):
        return self.typeScores[type]

    # returns random type with weighted probabilities
    def getRandomType(self):
        r = random.random()
        for type in self.typeScores.iterkeys():
            score = self.typeScores[type]
            if score > r:
                return type
            else:
                r = r - score

class OldFeed:
    def __init__(self, user):
        self.scoreSum = 0.0
        self.relations = Relationship.objects.filter(user=user)
        self.topicDict = {}
        for topic in TOPICS:
            self.topicDict[topic] = ScoreType()

    ###### PUBLIC METHODS ######

    def calculateScores(self):
        for uc in self.relations:
            topics = list(uc.content.topics.all().values_list('topic_text', flat=True))
            # get topics for comments
            if uc.content.type == 'C':
                topics = list(uc.content.downcast().topics.all().values_list('topic_text', flat=True))
                # get topics of question content if response
            if uc.content.type == 'R':
                topics = list(uc.content.downcast().question.topics.all().values_list('topic_text', flat=True))
            type = uc.content.type
            relationship = uc.relationship_type
            for t in topics:
                value = getRelationshipValue(relationship)
                self.topicDict[t].addScore(type,value)
                self.scoreSum += value
        for score in self.topicDict.itervalues():
            score.normalizeTypeScores()
            score.normalizeTotalScore(self.scoreSum)

    def getTopicTypeMatches(self):
        criteria = self.__getRandomTopicAndType()
        queryset = Relationship.objects.filter(content__type__contains=criteria[1], content__topics__topic_text__contains=criteria[0])
        values = list(queryset.order_by('when')[:10].values_list('content', flat=True))
        # Turn list of values into one big Q objects
        queryset = reduce(lambda q,value: q|Q(id=value), values, Q())
        # Gets recent relevant content
        content = Content.objects.filter(queryset)
        # Choose content to return from weighted status probabilities
        return self.__getReturnContent(content)

    ###### PRIVATE METHODS ######

    def __getReturnContent(self, content):
        total = 0.0
        for c in content:
            total += c.status
        for c in content:
            c.status = float(c.status) / total
        r = random.random()
        for c in content:
            score = c.status
            if score > r:
                return c
            else:
                r = r - score

    def __getRandomTopicAndType(self):
        randomTopic = self.__getRandomTopic()
        randomType = self.topicDict[randomTopic].getRandomType()
        # returns (topic, type) tuple
        return randomTopic, randomType

    def __getRandomTopic(self):
        r = random.random()
        for topic in self.topicDict.iterkeys():
            score = self.topicDict[topic].getTotalScore()
            if score > r:
                return topic
            else:
                r = r - score



def updateTopicFeeds():
    main_topics = Topic.objects.filter(topic_text__in=constants.MAIN_TOPICS)
    for t in main_topics:
        topic_feed = getTopicFeed(t)
        if topic_feed:
            filter = getHotFilter()
            content = t.getContent()
            updateFeedHelper(a_feed=topic_feed, filter_setting=filter, content=content)

def initializeTopicFeed(topic):
    alias = "topicfeed:" + topic.alias
    topic_feed = Feed(alias=alias)
    topic_feed.save()
    print ("initialized: " + alias)
    return topic_feed


def initializeGeneralTopic():
    topic = Topic(topic_text="General", alias="general")
    topic.save()
    initializeTopicForum(topic)
    initializeTopicImage(topic)
    return topic

#-----------------------------------------------------------------------------------------------------------------------
# Updates QuestionDiscussed models (an optimization for storing which questions are most discussed).
#-----------------------------------------------------------------------------------------------------------------------
def updateQuestionDiscussed():
    question_discussed = QuestionDiscussed.objects.all()
    for q in Question.objects.all():
        f = question_discussed.filter(question=q)
        if f:
            qd = f[0]
            qd.num_comments = q.getNumComments()
        else:
            qd = QuestionDiscussed(question=q, num_comments=q.getNumComments())
        qd.save()


#-----------------------------------------------------------------------------------------------------------------------
# Takes in a user, and adds all items in his feed to history, then updates feed (so feed has all new stuff)
# args: user (user to be updated)
# tags: USABLE
# frequency: everyday/whenever-called-by-user
#-----------------------------------------------------------------------------------------------------------------------
def refreshFeed_simple(user):
    for x in user.my_feed.all():
        user.my_history.add(x.content)



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
    lgfeed.updateUserFeed(user)
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
# Adds content to profile page of user.
#-----------------------------------------------------------------------------------------------------------------------
def addContent(request, user, content):
    user.getProfilePage().addContent(content)
    return HttpResponse("added")

#-----------------------------------------------------------------------------------------------------------------------
# Adds politician to profile page of user.
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
# Sets linkfrom cooke to be posted piece of content.
#
#-----------------------------------------------------------------------------------------------------------------------
def linkfrom(request, dict={}):
    """Links content from linkfrom cookie to content in post"""
    response = HttpResponse("linkfrom set")
    response.set_cookie('linkfrom',value=request.POST['c_id'])
    return response

#-----------------------------------------------------------------------------------------------------------------------
# Links content from linkfrom cookie to content in post
#
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


    elif tag == 'rank':
    print "*** UPDATING CONTENT RANK ***"
    lgfeed.updateRank()
elif tag == 'allcomparisons':
print "*** UPDATING VIEW COMPARISONS ***"
lgcompare.updateViewComparisons()
elif tag == 'usercomparisons':
print "*** UPDATING VIEW COMPARISONS ***"
lgcompare.updateUserComparisons()


elif tag == 'contentlinks':
print "*** UPDATING CONTENT LINKS ***"
lgcompare.updateAllContentLinks(debug=True)
elif tag == 'userfeeds':
print "*** UPDATING USER FEEDS ***"
lgfeed.updateUserFeeds()

elif tag == 'lovegovfeeds':
print "*** UPDATING LOVEGOV FEEDS ***"
lgfeed.updateLoveGovFeeds()
elif tag == 'alpha':
print "*** ALPHA UPDATE ***"
scheduled_logger.debug("** alpha update **")
lgcompare.updateLoveGovResponses()
elif tag == 'topicfeeds':
print "*** UPDATING TOPIC FEEDS ***"
scheduled_logger.debug("** updating site feeds **")
lgfeed.updateTopicFeeds()
elif tag == 'betafeeds':
scriptUpdate(tag="sitefeeds")
scriptUpdate(tag="topicfeeds")



########################################################################################################################
########################################################################################################################
#   Live debates.
#
#
########################################################################################################################
########################################################################################################################
MESSAGE_TYPE_CHOICES = (
    ('S','system'),
    ('A','actionPOST'),
    ('M', 'message'),
    ('J','join'),
    ('L','leave'),
    ('N','notification')
    )

SIDE = (
    ('L','left'),
    ('R','right'),
    ('M', 'moderator'),
    ('S', 'spectator')
    )

class DebateManager(models.Manager):

    def get_room(self, parent_type, parent_id):
        return self.get(belongs_to_type=parent_type, belongs_to_id=parent_id)


class Debate(Content):
    moderator = models.ForeignKey(UserProfile, related_name="moderator")
    full_descript = models.TextField(max_length=10000)
    debate_when = models.DateTimeField()
    objects = DebateManager() # custom manager

    def say(self, type, sender, message):
        m = DebateMessage(self, type, sender, message)
        m.save()
        return m

    def messages(self, after=None):
        m = DebateMessage.objects.filter(room=self)
        if after:
            m = m.filter(pk__gt=after)
        return m

    def join(self, user, side, privacy):
        debater = Debaters.objects.get(content=self, user=user)
        # case for newcomer to debate
        if debater is None:
            timestamp = datetime.datetime.now()
            debater = Debaters(user=user, content=self, side=side, when=timestamp, relationship="I", privacy=privacy)
            debater.save()
        # case for updating sides
        else:
            debater.side = side
            debater.privacy = privacy
            debater.save()

    def startDebate(self, user):
        if self.moderator == user:
            self.active = True
            return True
        else:
            return False

    def endDebate(self, user):
        if self.moderator == user:
            self.active = False
            return True
        else:
            return False

    def __unicode__(self):
        return 'Chat for %s %d' % (self.belongs_to_type, self.belongs_to_id)

class Debaters(UCRelationship):
    # FIELDS
    side = models.CharField(max_length=1,choices=SIDE)


class DebateMessage(Content):
    room = models.ForeignKey(Debate)
    sender = models.ForeignKey(UserProfile)
    message_type = models.CharField(max_length=1, choices=MESSAGE_TYPE_CHOICES)
    debate_side = models.CharField(max_length=1, choices=SIDE)
    message = models.CharField(max_length=3000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.type in ['s','m','n']:
            return u'*** %s' % self.message
        elif self.type == 'j':
            return '*** %s has joined...' % self.sender
        elif self.type == 'l':
            return '*** %s has left...' % self.sender
        elif self.type == 'a':
            return '*** %s %s' % (self.sender, self.message)
        return ''