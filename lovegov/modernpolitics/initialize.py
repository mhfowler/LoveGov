########################################################################################################################
########################################################################################################################
#
#           Defaults
#
#
########################################################################################################################
########################################################################################################################

# lovegov
import traceback
from bs4 import BeautifulSoup
from django import db
from lovegov.modernpolitics.helpers import *

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def getDefaultImage():
    return UserImage.lg.get_or_none(alias="Default_Image") or initializeDefaultImage()

def getHotFilter():
    return FilterSetting.lg.get_or_none(alias="Hot_Filter") or initializeHotFilter()

def getNewFilter():
    return FilterSetting.lg.get_or_none(alias="New_Filter") or initializeNewFilter()

def getBestFilter():
    return FilterSetting.lg.get_or_none(alias="Best_Filter") or initializeBestFilter()

def getDefaultFilter():
    return getHotFilter()

def getLoveGovGroup():
    return Group.lg.get_or_none(alias="LoveGov_Group") or Group.lg.get_or_none(alias="lovegov-group") or initializeLoveGovGroup()

def getLoveGovGroupView():
    return getLoveGovGroup().group_view.responses.all()

def getLoveGovUser():
    return UserProfile.lg.get_or_none(alias="lovegov") or initializeLoveGovUser()

def getAnonUser():
    return UserProfile.lg.get_or_none(alias="anonymous") or initializeAnonymous()

def getNewFeed():
    return Feed.lg.get_or_none(alias='New_Feed') or initializeFeed('New_feed')

def getHotFeed():
    return Feed.lg.get_or_none(alias='Hot_Feed') or initializeFeed('Hot_Feed')

def getBestFeed():
    return Feed.lg.get_or_none(alias='Best_Feed') or initializeFeed('Best_Feed')

def getTopicImage(topic):
    alias = "topicimage:" + topic.alias
    return UserImage.lg.get_or_none(alias=alias) or initializeTopicImage(topic)

def getGeneralTopic():
    return Topic.lg.get_or_none(alias='general') or initializeGeneralTopic()

def getOtherNetwork():
    return Network.lg.get_or_none(name="other") or initializeOtherNetwork()

def getCongressNetwork():
    return Network.lg.get_or_none(alias="congress") or initializeCongressNetwork()


def getToRegisterNumber():
    num = LGNumber.lg.get_or_none(alias="to_register")
    if not num:
        num = LGNumber(alias="to_register", number=100)
        num.save()
    return num


########################################################################################################################
########################################################################################################################
#    Initialization methods which are not for testing. They are meant to create and modify db in ways that
#   we will actually want on the site.
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# Initialize lovegov settings and other necessary defaults.
# tags: USABLE
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGov():
    initializeDefaultImage()
    initializeLoveGovGroup()
    initializeLoveGovUser()
    initializeTopicImages()
    initializeParties()
    # filters
    initializeBestFilter()
    initializeNewFilter()
    initializeHotFilter()
    # feeds
    initializeFeeds()
    # init pass codes
    initializePassCodes()

#-----------------------------------------------------------------------------------------------------------------------
# Initializes the user lovegov..... this user represents the site as a whole. Any content created by "us" will be attributed
# to user lovegov.
# lovegov's views will be an aggregate of the views of all memebers of the site.
# we control lovegov.
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGovUser():
    if UserProfile.objects.filter(alias="lovegov"):
        print("...lovegov user already initialized.")
    else:
        lovegov = ControllingUser.objects.create_user('lovegov', 'lovegov', 'free')
        lovegov.first_name = 'Love'
        lovegov.last_name = 'Gov'
        user_profile = superUserHelper(lovegov)
        user_profile.alias = "lovegov"
        user_profile.save()
        print "initialized: lovegov user"
        return user_profile


#-----------------------------------------------------------------------------------------------------------------------
# Currently, just makes lovegov worldview equal to aggregate of all users on site. But could also do more later.
#-----------------------------------------------------------------------------------------------------------------------
def initializeLoveGovGroup():
    if Group.objects.filter(alias="LoveGov_Group") or Group.objects.filter(alias="lovegov-group"):
        print("...lovegov group already initialized.")
    else:
        group = Group(title="LoveGov Group", group_type='O', full_text="We are lovegov.", system=True, alias="LoveGov_Group")
        group.autoSave()
        group.saveDefaultCreated()
        # add all users
        for u in UserProfile.objects.filter(ghost=False):
            group.members.add(u)
        print("initialized: lovegov group")
        return group

#-----------------------------------------------------------------------------------------------------------------------
# Initializes a user which represents all anonymous users on the site.
#-----------------------------------------------------------------------------------------------------------------------
def initializeAnonymous():
    if UserProfile.objects.filter(alias="anonymous"):
        print("...anon user already initialized.")
    else:
        from lovegov.modernpolitics.register import createUser
        already = ControllingUser.lg.get_or_none(username="anon")
        if already:
            if already.user_profile:
                already.user_profile.delete()
            already.delete()
        anon = createUser(name="Anonymous", email="anon", password="theANON")
        anon.prohibited_actions = ANONYMOUS_PROHIBITED_ACTIONS
        userprof = anon.user_profile
        userprof.confirmed = True
        userprof.alias = 'anonymous'
        userprof.save()
        print("initialized: anon user")
        return userprof


#-----------------------------------------------------------------------------------------------------------------------
# Initializes a user which represents all anonymous users on the site.
#-----------------------------------------------------------------------------------------------------------------------
def initializeDefaultImage():
    if UserImage.objects.filter(alias="Default_Image"):
        print("...default image already initialized.")
    else:
        default = UserImage(title="Default Image", summary="default.", alias="Default_Image")
        file = open(DEFAULT_IMAGE)
        default.createImage(file, type=".png")
        default.autoSave()
        print("initialized: default image")
        return default

#-----------------------------------------------------------------------------------------------------------------------
# Initializes best filter... for now same as default filter. Bayesian.
#-----------------------------------------------------------------------------------------------------------------------
def initializeBestFilter():
    if FilterSetting.objects.filter(alias="Best_Filter"):
        print("...best filter already initialized.")
    else:
        filter = FilterSetting(alias="Best_Filter")
        filter.save()
        print("initialized: best filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes new filter... only looks at content made in the last 2 weeks, and values recency.
#-----------------------------------------------------------------------------------------------------------------------
def initializeNewFilter():
    if FilterSetting.objects.filter(alias="New_Filter"):
        print("...new filter already initialized.")
    else:
        days = NEWFILTER_DAYS
        algo = 'R'  # reddit
        filter = FilterSetting(days=days, algo=algo, alias="New_Filter")
        filter.save()
        print("initialized: new filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes hot filter... only looks at votes within time period of hot window (most recent week)
#-----------------------------------------------------------------------------------------------------------------------
def initializeHotFilter():
    if FilterSetting.objects.filter(alias="Hot_Filter"):
        print("...hot filter already initialized.")
    else:
        hot_window = HOT_WINDOW
        algo = 'H'  # hot
        filter = FilterSetting(hot_window=hot_window, algo=algo, alias="Hot_Filter")
        filter.save()
        print("initialized: hot filter")
        return filter

#-----------------------------------------------------------------------------------------------------------------------
# Initializes 3 default site-wide feeds.
#-----------------------------------------------------------------------------------------------------------------------
def initializeFeeds():
    initializeFeed("New_Feed")
    initializeFeed("Hot_Feed")
    initializeFeed("Best_Feed")

def initializeFeed(alias):
    if Feed.objects.filter(alias=alias):
        print("..." + alias + " already initialized.")
    else:
        feed = Feed(alias=alias)
        feed.save()
        print("initialized: " + alias + " feed")
        return feed

#-----------------------------------------------------------------------------------------------------------------------
# Initialize images for every topic.
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicImages():
    for x in Topic.objects.all():
        if x.topic_text in MAIN_TOPICS:
            initializeTopicImage(x)
    initializeGeneralTopicImage(getGeneralTopic())

def initializeTopicImage(x):
    if x.topic_text in MAIN_TOPICS:
        # initialize image
        ref = os.path.join(PROJECT_PATH, 'frontend'+x.getImageRef())
        file = open(ref)
        x.image.save(photoKey(".png"), File(file))
        # initialize hover
        hover_ref = 'frontend/static/images/questionIcons/' + x.alias + '/' + x.getPre() + '_hover.png'
        hover_ref = os.path.join(PROJECT_PATH, hover_ref)
        file = open(hover_ref)
        x.hover.save(photoKey(".png"), File(file))
        # initialize selected
        selected_ref = 'frontend/static/images/questionIcons/' + x.alias + '/' + x.getPre() + '_selected.png'
        selected_ref = os.path.join(PROJECT_PATH, selected_ref)
        file = open(selected_ref)
        x.selected.save(photoKey(".png"), File(file))
        # save
        x.save()
        print("initialized: " + x.topic_text + " image")
        return x
    else:
        return None

def initializeGeneralTopic():

    already = Topic.lg.get_or_none(alias="general")
    if already:
        print ("general topic already initialized.")
        return already

    topic = Topic(topic_text="General", alias="general")
    topic.save()

    initializeGeneralTopicImage(topic)

    print "initialized: General Topic"
    return topic

def initializeGeneralTopicImage(topic):

    image_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/icons/topic_icons/for_default.png')
    hover_ref = os.path.join(PROJECT_PATH,'frontend/static/images/icons/topic_icons/for_hover.png')
    selected_ref = os.path.join(PROJECT_PATH,'frontend/static/images/icons/topic_icons/for_selected.png')

    file = open(image_ref)
    topic.image.save(photoKey(".png"), File(file))
    file = open(hover_ref)
    topic.hover.save(photoKey(".png"), File(file))
    file = open(selected_ref)
    topic.selected.save(photoKey(".png"), File(file))
    topic.save()

    print "initialized: General Topic Image"

#-----------------------------------------------------------------------------------------------------------------------
# Initialize mini images for every topic.
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicMiniImages():
    for topic in Topic.objects.all():
        if topic.topic_text in MAIN_TOPICS:
            title = topic.topic_text + "Mini Image"
            alias = "topicminiimage:" + topic.alias
            summary = "A mini image representing " + topic.topic_text + "."
            img = UserImage(title=title, summary=summary, alias=alias)
            ref = os.path.join(PROJECT_PATH, 'alpha' + topic.getMiniImageRef())
            file = open(ref)
            img.createImage(file, type=".png")
            img.autoSave()
            # save mini image
            topic.image_mini.save(photoKey(".png"), File(file))
            # save
            topic.save()
            print("initialized: " + title)

#-----------------------------------------------------------------------------------------------------------------------
# Initialize colors for every topic
#-----------------------------------------------------------------------------------------------------------------------
def initializeTopicColors():
    for topic in Topic.objects.all():
        title = topic.topic_text + " Colors"
        if topic.topic_text is "Economy":
            topic.color = '#92B76C'
            topic.color_light = '#CBE0AF'
        elif topic.topic_text is "Education":
            topic.color = '#9DC5C9'
            topic.color_light = '#C3E7ED'
        elif topic.topic_text is "Energy":
            topic.color = '#F9D180'
            topic.color_light = '#FFF0C5'
        elif topic.topic_text is "Environment":
            topic.color = '#9797C6'
            topic.color_light = '#CACAD8'
        elif topic.topic_text is "Health Care":
            topic.color = '#EA7D95'
            topic.color_light = '#E8B8C6'
        elif topic.topic_text is "National Security":
            topic.color = '#EA947D'
            topic.color_light = '#F9BFB4'
        elif topic.topic_text is "Social Issues":
            topic.color = '#639E9B'
            topic.color_light = '#A3C6C4'
        elif topic.topic_text is "Social Issues":
            topic.color = '#639E9B'
            topic.color_light = '#A3C6C4'
        topic.save()
        print("initialized: " + title)

#-----------------------------------------------------------------------------------------------------------------------
# Initialize network for people with non .edu email extension.
#-----------------------------------------------------------------------------------------------------------------------
def initializeOtherNetwork():
    if Network.objects.filter(name="other"):
        print ("...other network already initialized")
    else:
        network = Network(name="other")
        network.title = "Other Network"
        network.summary = "Network of all people with non recognized emails."
        network.autoSave()
        print ("initialized: Other Network")
        return network

#-----------------------------------------------------------------------------------------------------------------------
# Initialize network for congress
#-----------------------------------------------------------------------------------------------------------------------
def initializeCongressNetwork():
    if Network.objects.filter(alias="congress"):
        print ("...congress network already initialized")
    else:
        network = Network(alias="congress")
        network.title = "Congress"
        network.summary = "all members of Congress."
        network.autoSave()
        # join all members
        congress = ElectedOfficial.objects.all()
        for u in congress:
            network.members.add(u)
            u.networks.add(network)
        print ("initialized: Congress Network")
        return network

#-----------------------------------------------------------------------------------------------------------------------
# Initialize passcodes.
#-----------------------------------------------------------------------------------------------------------------------
def initializePassCodes():
    code = RegisterCode(code_text="politics")
    code.save()
    code = RegisterCode(code_text="brownrisd")
    code.save()

#-----------------------------------------------------------------------------------------------------------------------
# initializes valid emails
#-----------------------------------------------------------------------------------------------------------------------
def initializeValidEmails():
    brownExtension = ValidEmailExtension(extension='brown.edu')
    brownExtension.save()
    clayEmail = ValidEmail(email='rioisk@gmail.com', description="clay's gmail")
    clayEmail.save()
    maxEmail = ValidEmail(email="max_fowler@brown.edu", description="max's email")
    maxEmail.save()

# initializes valid emails
#-----------------------------------------------------------------------------------------------------------------------
def initializeValidRegisterCodes():
    code = RegisterCode(code_text='brownrisd')
    code.save()

########################################################################################################################
########################################################################################################################
# Initialize db with crap
#       - for ease of testing
#
########################################################################################################################
########################################################################################################################
def initializeDB():
    from scripts.alpha import scriptCreatePresidentialCandidates
    from scripts.alpha import scriptCreateCongressAnswers

    # post-processing of migration
    setTopicAlias()
    # initialize defaults
    initializeLoveGov()
    ## ## ## ## ## ## ## ##
    initializeAdmin()
    initializeUsers()
    initializeNormalBob()
    initializeGeorgeBush()
    initializeContent()
    # valid emails
    initializeValidEmails()
    initializeValidRegisterCodes()
    # initialize congress
    if not LOCAL:
        initializeCongress()
        scriptCreatePresidentialCandidates()
        initializeCommittees()
        initializeLegislation()
        initializeLegislationAmendments()
        initializeVotingRecord()
        scriptCreateCongressAnswers()


def setTopicAlias():
    for t in Topic.objects.all():
        t.makeAlias()


def initializeTestFeedData():
    r = random.Random()
    lovegov = getLoveGovUser()
    for i in range(10):
        title = "News " + str(i)
        p = News(title=title, summary="here's some news for ya", link="www.nytimes.com")
        p.autoSave(creator=lovegov, privacy='PUB')
        # add random amount of votes
        ups = r.choice(range(200))
        for l in range(ups):
            p.like(lovegov, 'PUB')
        downs = r.choice(range(200))
        for d in range(downs):
            p.dislike(lovegov, 'PUB')
    for i in range(100):
        title = "Petition " + str(i)
        p = Petition(title=title, full_text="a test petition aww yea")
        p.autoSave(creator=lovegov, privacy='PUB')
        # add random amount of votes
        ups = r.choice(range(200))
        for l in range(ups):
            p.like(lovegov, 'PUB')
        downs = r.choice(range(200))
        for d in range(downs):
            p.dislike(lovegov, 'PUB')


def initializeNormalBob():
    from lovegov.modernpolitics.register import createUser
    normal = createUser(name="Normal Bob", email="normal@gmail.com", password="normal")
    normal.user_profile.confirmed = True
    normal.user_profile.save()
    print "initialized: Normal Bob"

def initializeTopics(using="default"):
    t1 = Topic(topic_text="Economy")
    t1.save(using=using)
    t2 = Topic(topic_text="Taxes", parent_topic=t1)
    t2.save(using=using)
    t3 = Topic(topic_text="Education")
    t3.save(using=using)
    t4 = Topic(topic_text="College", parent_topic=t3)
    t4.save(using=using)
    t5 = Topic(topic_text="School Funding", parent_topic=t3)
    t5.save(using=using)
    t6 = Topic(topic_text="Reform")
    t6.save(using=using)
    t7 = Topic(topic_text="Justice Reform", parent_topic=t6)
    t7.save(using=using)
    t8 = Topic(topic_text="Social Issues")
    t8.save(using=using)
    t9 = Topic(topic_text="Foreign Policy")
    t9.save(using=using)
    t10 = Topic(topic_text="Environment")
    t10.save(using=using)
    t11 = Topic(topic_text="Health Care")
    t11.save(using=using)
    t12 = Topic(topic_text="Energy")
    t12.save(using=using)
    t13 = Topic(topic_text="National Security")
    t13.save(using=using)

def initializeAdmin():
    yoshi = ControllingUser.objects.create_superuser(username="yoshi", email="joshcka_tryba@brown.edu", password="hackthis12")
    greg = ControllingUser.objects.create_superuser(username="greg", email="greg@brown.edu", password="greggers")
    yoshi.first_name = "Joshcka"
    yoshi.last_name = "Tryba"
    greg.first_name = "Greg"
    greg.last_name = "Greg"
    superUserHelper(yoshi)
    superUserHelper(greg)

def initializeUsers():
    # RANDY
    randy = ControllingUser.objects.create_user('randy', 'randy', 'salt')
    randy.first_name = 'Randy'
    randy.last_name = 'Johnson'
    superUserHelper(randy)
    # KATY
    katy = ControllingUser.objects.create_user('katy', 'katy', 'salt')
    katy.first_name = 'Katy'
    katy.last_name = 'Perry'
    superUserHelper(katy)
    # STALIN
    stalin = ControllingUser.objects.create_user('stalin', 'stalin', 'salt')
    stalin.first_name = 'Joseph'
    stalin.last_name = 'Stalin'
    superUserHelper(stalin)
    # CLAY
    clay = ControllingUser.objects.create_user('clayton_dunwell@brown.edu', 'clayton_dunwell@brown.edu', 'texers')
    clay.first_name = 'Clayton'
    clay.last_name = 'Dunwell'
    superUserHelper(clay)

def initializeQ():
    title = 'LoveGov Question'
    question_text = 'Do you love LoveGov?'
    question_type = 'MC'
    a1 = Answer(answer_text="yes",value=5)
    a2 = Answer(answer_text="Lo<3Gov4eva",value=10)
    a1.save()
    a2.save()
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="College")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)
    # # 2
    title = 'Other Question'
    question_text = 'Whatsup?'
    question_type = 'MC'
    a1 = Answer(answer_text="not much",value=5)
    a2 = Answer(answer_text="coding",value=3)
    a1.save()
    a2.save()
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="Education")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)

def initializeGeorgeBush():
    from lovegov.modernpolitics.register import createUser
    normal = createUser(name="George Bush", email="george@gmail.com", password="george")
    normal.user_profile.confirmed = True
    normal.user_profile.save()
    print "initialized: George Bush"

def initializeQuestions():
    # QUESTION 1
    a1 = Answer(answer_text="macaroni",value=1)
    a2 = Answer(answer_text="chicken",value=2)
    a3 = Answer(answer_text="chocolate milk",value=3)
    a4 = Answer(answer_text="jello",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'Food Question'
    question_text = 'Which food would you eat for the rest of your life?'
    question_type = 'MC'
    type = 'Q'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic = Topic.objects.get(topic_text="Economy")
    q1.topics.add(topic)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)
    # QUESTION 2
    a1 = Answer(answer_text="obama",value=1)
    a2 = Answer(answer_text="michael jordan",value=2)
    a3 = Answer(answer_text="kim jung",value=3)
    a4 = Answer(answer_text="lil wayne",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'President Question'
    question_text = 'Who would you vote for president?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Economy")
    topic2 = Topic.objects.get(topic_text="College")
    q1.topics.add(topic1)
    q1.topics.add(topic2)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)
    # QUESTION 3
    a1 = Answer(answer_text="Yes",value=1)
    a2 = Answer(answer_text="No",value=2)
    a3 = Answer(answer_text="Abortion is permissible in rare cases",value=3)
    a1.save()
    a2.save()
    a3.save()
    title = 'Abortion Question'
    question_text = 'Do you considered yourself pro-life?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Social Issues")
    q1.topics.add(topic1)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    # QUESTION 4
    a1 = Answer(answer_text="Yes, significantly",value=1)
    a2 = Answer(answer_text="Yes",value=2)
    a3 = Answer(answer_text="No",value=3)
    a4 = Answer(answer_text="No, and increase spending",value=4)
    a1.save()
    a2.save()
    a3.save()
    a4.save()
    title = 'Military Spending Question'
    question_text = 'Would you like to see the government reduce military spending?'
    question_type = 'MC'
    q1 = Question(title=title,question_text=question_text,question_type=question_type,official=True,type=type)
    q1.save()
    topic1 = Topic.objects.get(topic_text="Reform")
    q1.topics.add(topic1)
    q1.answers.add(a1)
    q1.answers.add(a2)
    q1.answers.add(a3)
    q1.answers.add(a4)


def initializeContent():
    topic = Topic.objects.get(topic_text="Health Care")
    topic2 = Topic.objects.get(topic_text="National Security")
    p1 = Petition(type="P", title="IMPEACH BUSH", summary="impeach bush summary", full_text="We should get rid of President Bush because blah blah blah")
    p2 = Petition(type="P", title="STOP PROP 9", summary="prop 9 summary", full_text="BLAH BLAH BLAH BLAH BLAH BLAH")
    p3 = Petition(type="P", title="BAN GAY MARRIAGE", summary="gay marriage summary", full_text="BAN GAY MARRIAGE FULL TEXT")
    p4 = Petition(type="P", title="REPEAL H.R. 123", summary="REPEAL H.R. 123 summary", full_text="REPEAL H.R. 123 FULL TEXT")
    p1.save()
    p2.save()
    p3.save()
    p4.save()
    p1.setMainTopic(topic)
    p2.setMainTopic(topic2)
    p3.setMainTopic(topic2)
    randy = UserProfile.objects.get(username='randy')
    p1.autoSave(creator=randy,privacy='PUB')
    p2.autoSave(creator=randy,privacy='PUB')
    p3.autoSave(creator=randy,privacy='PUB')
    p4.autoSave(creator=randy,privacy='PUB')
    n1 = News(type="N", title="Legislation to affect....", summary="Legislation to affect....summary", link="www.cnn.com")
    n2 = News(type="N", title="LoveGov launches", summary="changed politics forever", link="www.lovegov.com")
    n1.save()
    n2.save()
    n1.setMainTopic(topic)
    n2.setMainTopic(topic2)

    testGroup = Group(type="G", title="SUPER GROUP", summary="group summary", group_type="O", full_text="great group")

    testGroup.autoSave()
    testGroup.topics.add(topic)

def testAddNewContent():
    p1 = Petition(type="P", title="NEW PETITION", summary="new petition summary", full_text="this is the new petition full text")
    p1.save()

def initializeDebate():
    moderator = UserProfile.objects.get(username='stalin')
    now = datetime.datetime.now()
    newDebate = Debate(type="D", title="Health Care Debate", summary="Watch as Maximus Fowler and Clayton Dunwell duke it out", active=True, debate_when=now, moderator=moderator)
    newDebate.save()
    topic = Topic.objects.get(topic_text="Health Care")
    newDebate.topics.add(topic)
    modrelationship = Debaters(side="M", user=moderator, content=newDebate, relationship_type="I", privacy='PUB')
    modrelationship.save()
    debater1 = UserProfile.objects.get(username='stalin')
    debater2 = UserProfile.objects.get(username='katy')
    rel1 = Debaters(side="L", user=debater1, content=newDebate, relationship_type="I", privacy='PUB')
    rel2 = Debaters(side="R", user=debater2, content=newDebate, relationship_type="I", privacy='PUB')
    rel1.save()
    rel2.save()


def initializePersistentDebate():
    debate = Persistent(title="Star Wars Debate", summary="Who shot first?")
    topic = Topic.objects.get(topic_text="Health Care")
    debate.moderator = UserProfile.objects.get(username='stalin')
    debate.affirmative = UserProfile.objects.get(username='randy')
    debate.negative = UserProfile.objects.get(username='katy')
    debate.affirmative_confirmed = True
    debate.type = 'Y'
    debate.debate_type = 'C'
    debate.resolution = "Greedo shot first."
    debate.turns_total = 4
    debate.save()
    debate.topics.add(topic)

#-----------------------------------------------------------------------------------------------------------------------
# Counts the number of files in a path
#-----------------------------------------------------------------------------------------------------------------------
def filecount(path):
    count = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)): count += 1
    return count

#-----------------------------------------------------------------------------------------------------------------------
# Parses a string into a Date object (formatted YYYY-MM-DD)
#-----------------------------------------------------------------------------------------------------------------------
def parseDate(date):
    splitDate = str(date).split('-')
    return datetime.date(year=int(splitDate[0]), month=int(splitDate[1]), day=int(splitDate[2]))

#-----------------------------------------------------------------------------------------------------------------------
# Begins Congress Initialization
#-----------------------------------------------------------------------------------------------------------------------
def initializeCongress():
    for num in range(112,111,-1):
        print num
        # Get/open current XML file
        filepath = '/data/govtrack/' + str(num) + "/people.xml"
        image_root = '/data/govtrack/image/'
        parsedXML = BeautifulSoup(open(filepath))
        initializeCongressFile(parsedXML,image_root)

#-----------------------------------------------------------------------------------------------------------------------
# Initializes a single Congress File
#-----------------------------------------------------------------------------------------------------------------------
def initializeCongressFile(parsedXML,image_root):
    session_number = int(parsedXML.people['session'])
    congress_tag = Tag.lg.get_or_none(name='congress')
    if not congress_tag:
        congress_tag = Tag(name='congress')
        congress_tag.save()

    current_session = CongressSession.lg.get_or_none(session=session_number)
    if not current_session:
        current_session = CongressSession(session=session_number)
        current_session.save()

    # For each person at this congress
    for personXML in parsedXML.people.findChildren('person',recursive=False):

        person = initializeXMLCongressman(personXML,image_root=image_root)

        # Get their role
        role = personXML.role

        # Get their role info
        role_type = role['type']
        role_tag = None
        if role_type == 'sen':
            role_tag = 'senator'
        elif role_type == 'rep':
            role_tag = 'representative'
        else:
            print "[WARNING]: role type " + role_type + " is not recognized for " + name.encode('utf-8','ignore')
            continue # Skip this guy, can't make an Office without a tag

        role_state = role['state']
        role_district = role['district']

        # Find the tag related to this role
        current_tag = Tag.lg.get_or_none(name=role_tag)
        if not current_tag:
            current_tag = Tag(name=role_tag)
            current_tag.save()

        # Find the office related to
        office = current_tag.tag_set.filter(location__state=role_state,location__district=role_district)
        if office:
            office = office[0]
        if not office: # If it doesn't exist, make that office
            loc = PhysicalAddress(district=role_district, state=role_state)
            loc.save()
            office = Office(location=loc)
            office.autoSave()
            office.tags.add(current_tag)
            office.tags.add(congress_tag)


        # Take the start and end dates
        start_date = parseDate(role['startdate'])
        end_date = parseDate(role['enddate'])

        # See if this Office Held already exists.
        office_held = OfficeHeld.lg.get_or_none(user=person,office=office,start_date=start_date,end_date=end_date)
        if not office_held: # If it  doesn't, create it
            office_held = OfficeHeld(user=person,office=office,start_date=start_date,end_date=end_date)
            if (datetime.date.today() - end_date).days >= 0:
                office_held.current = True
            office_held.autoSave()

        office_held.congress_sessions.add(current_session)

        # Finally,
        person.offices_held.add(office_held)


#-----------------------------------------------------------------------------------------------------------------------
# Initializes a single congressman
#-----------------------------------------------------------------------------------------------------------------------
def initializeXMLCongressman(personXML,image_root=''):
    from lovegov.modernpolitics.register import createUser
    user_prof = None

    # name = first + " " + last
    fname = personXML['firstname'].encode('utf-8','ignore')
    lname = personXML['lastname'].encode('utf-8','ignore')
    name = fname+ " " +lname

    # get birthday
    birthday = None
    if personXML.has_key('birthday'):
        birthday = parseDate(personXML['birthday'])

    # Try to find this person by govtrack id
    govtrack_id = personXML.get('id')
    if govtrack_id:
        user_prof = UserProfile.lg.get_or_none( govtrack_id=govtrack_id )
    # Otherwise search by name and birthday
    if not user_prof:
        user_prof = UserProfile.lg.get_or_none( first_name=fname , last_name=lname , dob=birthday )

    # Otherwise make a new person
    if not user_prof:
        password = "congress"
        email = name.replace(" ","-") + "-" + str(personXML['id'])

        print "initializing " + name
        congressControl = createUser(name,email,password)
        user_prof = congressControl.user_profile
        user_prof.ghost = True

    # ========= UPDATE USER PROFILE ========= #
    # --------------------------------------- #
    user_prof.first_name = personXML['firstname']
    user_prof.last_name = personXML['lastname']
    user_prof.politician = True
    user_prof.elected_official = True

    if personXML.has_key('id'):
        user_prof.govtrack_id = personXML['id']
    if personXML.has_key('middlename'):
        user_prof.middle_name = personXML['middlename']
    if personXML.has_key('nickname'):
        user_prof.nick_name = personXML['nickname']
    if personXML.has_key('birthday'):
        user_prof.dob = parseDate(personXML['birthday'])
    if personXML.has_key('gender'):
        user_prof.gender = personXML['gender']
    if personXML.has_key('twitterid'):
        user_prof.twitter_user_id = personXML['twitterid']
    if personXML.has_key('facebookgraphid'):
        user_prof.facebook_id = personXML['facebookgraphid']

    if personXML.role.has_key('party'):
        party = personXML.role['party'].lower()
        for (party_char,party_name) in PARTY_TYPE:
            if party == party_name:
                cur_party = Party.lg.get_or_none(party_type=party_char)
                if cur_party:
                    user_prof.parties.add(cur_party)
                else:
                    print "[WARNING]: party " + party_name + " is not initialized.  Cannot add " + name.encode('utf-8','ignore')

    image_path = image_root + str(govtrack_id) + ".jpeg"
    try:
        user_prof.setProfileImage(file(image_path))
    except:
        print "[WARNING]: no image for elected official " + name.encode('utf-8','ignore') + " at " + image_path

    print dir(user_prof)

    user_prof.confirmed = True
    user_prof.save()

    return user_prof

#-----------------------------------------------------------------------------------------------------------------------
# Initialize all committee files and all committees
#-----------------------------------------------------------------------------------------------------------------------
def initializeCommittees():
    for num in range(112,108,-1):
        congress_session = CongressSession.lg.get_or_none(session=session_number) or CongressSession(session=session_number)
        filePath = '/data/govtrack/' + str(num) + '/committees.xml'
        fileXML = open(filePath)
        parsedXML = BeautifulSoup(fileXML)

        for committeeXML in parsedXML.committees.findChildren('committee',recursive=False):
            committee = initializeCommittee(committeeXML,congress_session)

            for subXML in committeeXML.findChildren('subcommittee',recursive=False):
                initializeSubCommittee(subXML,congress_session,committee)


#-----------------------------------------------------------------------------------------------------------------------
# Initialize one committee
#-----------------------------------------------------------------------------------------------------------------------
def initializeCommittee(committeeXML,session):
    name = committeeXML.get('displayname')
    if name:
        name = name.encode("utf-8",'ignore')

    type = committeeXML.get('type')
    if type == 'house':
        type = 'H'
    elif type == 'senate':
        type = 'S'
    elif type == 'joint':
        type = 'J'
    else:
        print '[WARNING]: Committee type ' + type + ' not recognized in committee ' + name
        return None

    code = committeeXML.get('code')

    # Find this committee
    committee = Committee.lg.get_or_none(title=name,committee_type=type,code=code)
    if not committee:
        committee = Committee(title=name,committee_type=type,code=code)
        committee.autoSave()

    for memberXML in committeeXML.findChildren('member',recursive=False):
        member = UserProfile.lg.get_or_none( govtrack_id=memberXML.get('id') )
        if member:
            committee.joinMember( member , session , memberXML.get('role') )

    return committee

#-----------------------------------------------------------------------------------------------------------------------
# Initialize one sub-committee
#-----------------------------------------------------------------------------------------------------------------------
def initializeSubCommittee(committeeXML,session,parent):
    name = committeeXML.get('displayname')
    if name:
        name = name.encode("utf-8",'ignore')

    type = None
    if parent.committee_type == 'H':
        type = 'HS'
    elif parent.committee_type == 'S':
        type = 'SS'
    elif parent.committee_type == 'J':
        type = 'JS'
    else:
        print '[WARNING]: Committee type ' + parent.committee_type + ' not recognized in committee ' + name
        return None

    code = committeeXML.get('code')

    committee = Committee.lg.get_or_none(title=name,committee_type=type,code=code,parent=parent)
    if not committee:
        committee = Committee(title=name,committee_type=type,code=code,parent=parent)
        committee.autoSave()

    for memberXML in committeeXML.findChildren('member',recursive=False):
        member = UserProfile.lg.get_or_none( govtrack_id=memberXML.get('id') )
        if member:
            committee.joinMember( member , session , memberXML.get('role') )

    return committee


#-----------------------------------------------------------------------------------------------------------------------
# Initialize each of the legislation files
# RETURN: a list of tuples of unparsed legislation file paths and error messages
#-----------------------------------------------------------------------------------------------------------------------
def initializeLegislation():
    missed_files = []
    print "[IMPORTANT]: The return of this function is a list of errors represented as tuples of the format (filepath,error_message).\n" \
          "[IMPORTANT]: If you would like to see this result, make sure you have assigned a variable to hold the return of this function"

    count = 0

    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills/"
        fileListing = os.listdir(filePath)

        for infile in fileListing:
            count += 1
            db.reset_queries()

            fileXML = open(filePath + infile)
            parsedXML = BeautifulSoup(fileXML)
            result = parseLegislation(parsedXML)

            if result is not '':
                print "[ERROR]: " + result + '.  Bill was not initialized'
                missed_files.append((filePath + infile,result))

            if count%100 is 0:
                print str(count) + " files checked"

    return missed_files


#-----------------------------------------------------------------------------------------------------------------------
# Initialize one legislation object
# RETURN: an error message string.  Returns an empty string on success
#-----------------------------------------------------------------------------------------------------------------------
def parseLegislation(XML):
    # If there's no bill or state for some reason, you can't parse the bill
    if not XML.bill:
        return 'Missing bill tag'
    if not XML.state:
        return 'Missing state tag'

    # Get this congress session
    session_num = XML.bill.get('session')
    if not session_num:
        return 'Missing congress session'
    session = CongressSession.lg.get_or_none(session=session_num)
    if not session:
        session = CongressSession(session=session_num)
        session.save()

    # Get identifying bill features
    type = XML.bill.get('type')
    number = int(XML.bill.get('number'))
    introduced = parseDate(XML.introduced.get('datetime'))
    if not type or not number or not introduced:
        return 'Missing bill type, number, or introduced tag'

    # Check for bill existence and get bill
    legislation = Legislation.lg.get_or_none( congress_session=session , bill_number=number , bill_type=type , bill_introduced=introduced )
    if not legislation:
        legislation = Legislation( congress_session=session , bill_type=type , bill_number=number , bill_introduced=introduced )

    # Update basic bill info
    updated = parseDateTime(XML.bill.get('updated'))
    last_updated = legislation.bill_updated

    # If we don't know what update this is, or this is the most recent update
    if not last_updated or not updated or (last_updated - updated).total_seconds() <= 0:
        if updated:
            legislation.bill_updated = updated
        legislation.state_date = parseDateTime(XML.state.get('datetime'))
        legislation.state_text = XML.state.text
        legislation.bill_summary = XML.summary.text

        # Find and add bill sponsor
        sponsor_id = XML.sponsor.get('id')
        if sponsor_id:
            sponsor = UserProfile.lg.get_or_none(govtrack_id=sponsor_id)
            if sponsor:
                legislation.sponsor = sponsor

    # Parses all title tags
    if XML.titles:
        for title in XML.titles.findChildren('title',recursive=False):
            type = title.get('type')
            if type is 'official':
                legislation.full_title = title.text
            elif type is 'short':
                legislation.title = title.text

    # Parses all cosponsors
    if XML.cosponsors:
        for cosponsorXML in XML.cosponsors.findChildren('cosponsor',recursive=False):
            # Check for cosponsor ID
            cosponsor_id = cosponsorXML.get('id')
            if not cosponsor_id:
                continue
            # Check for the actual cosponsor's profile
            cosponsor = UserProfile.lg.get_or_none(govtrack_id=cosponsor_id)
            if not cosponsor:
                continue
            # Check for the LegislationCosponsor relationship
            legislation_cosponsor = LegislationCosponsor.lg.get_or_none(cosponsor=cosponsor,legislation=legislation)
            if not legislation_cosponsor:
                legislation_cosponsor = LegislationCosponsor(cosponsor=cosponsor,legislation=legislation)

            # Check for and set the date joined
            cosponsor_date = cosponsorXML.get('joined')
            if cosponsor_date:
                legislation_cosponsor.date = cosponsor_date

            # Save that shit
            legislation_cosponsor.save()

    # Parses all actions (and sub actions)
    for actionXML in XML.actions.findChildren(recursive=False):
        # Get basic action data
        name = actionXML.name
        new_legislation_action = None

        # If action
        if name is 'action':
            new_legislation_action = LegislationAction()
        elif name is 'calendar':
            new_legislation_action = LegislationCalendar()
        elif name is 'vote':
            new_legislation_action = LegislationVote()
        elif name is 'vote-aux':
            new_legislation_action = LegislationVote()
        elif name is 'topresident':
            new_legislation_action = LegislationToPresident()
        elif name is 'signed':
            new_legislation_action = LegislationSigned()
        elif name is 'enacted':
            new_legislation_action = LegislationAction()

        if not new_legislation_action:
            continue

        new_legislation_action.parseGovtrack(actionXML,legislation=legislation)

    for committeeXML in XML.committees.findChildren('committee',recursive=False):
        committee = none

        code = committeeXML.get('code')
        if code:
            committee = Committee.lg.get_or_none(code=code)

        subcommittee_name = committeeXML.get('subcommittee')
        if not committee and subcommittee_name:
            committee = Committee.lg.get_or_none(title=sub_committee_name)

        title = committeeXML.get('name')
        if not committee and title:
            committee = Committee.lg.get_or_none(title=title)

        if committee:
            legislation.committees.add(committee)

    for termXML in XML.subjects.findChildren('term',recursive=False):
        name = termXML.get('name')
        if name:
            subject = LegislationSubject.lg.get_or_none(name=name)
            if not subject:
                subject = LegislationSubject(name=name)
                subject.save()
            legislation.bill_subjects.add(subject)

    # Save the legislation
    legislation.save()
    return ''

#-----------------------------------------------------------------------------------------------------------------------
# Counts the number of govtrack legislation files there are
#-----------------------------------------------------------------------------------------------------------------------
def countLegislation():
    count = 0
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills/"
        count += filecount(filePath)
    return count


#-----------------------------------------------------------------------------------------------------------------------
# Initialize each of the legislation amendment files
# RETURN: a list of tuples of unparsed legislation amendment file paths and error messages
#-----------------------------------------------------------------------------------------------------------------------
def initializeLegislationAmendments():
    missed_files = []
    print "[IMPORTANT]: The return of this function is a list of errors represented as tuples of the format (filepath,error_message).\n"\
          "[IMPORTANT]: If you would like to see this result, make sure you have assigned a variable to hold the return of this function"

    count = 0
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills.amdt/"
        fileListing = os.listdir(filePath)

        for infile in fileListing:
            count += 1
            db.reset_queries()

            fileXML = open(filePath + infile)
            parsedXML = BeautifulSoup(fileXML)
            result = parseLegislationAmendment(parsedXML)

            if result is not '':
                print "[ERROR]: " + result + '.  Amendment was not initialized'
                missed_files.append((filePath + infile,result))

            if count%100 is 0:
                print str(count) + " files checked"

    return missed_files


#-----------------------------------------------------------------------------------------------------------------------
# Initialize one legislation amendment object
# RETURN: an error message string.  Returns an empty string on success
#-----------------------------------------------------------------------------------------------------------------------
def parseLegislationAmendment(XML):
    # Basic tag check
    if not XML.amendment:
        return 'Missing amendment tag'
    if not XML.amends:
        return 'Missing amends tag'

    # Get this session number
    session_num = XML.amendment.get('session')
    if not session_num:
        return 'Missing session in amendment tag'
    # and get the session
    session = CongressSession.lg.get_or_none(session=session_num)
    if not session:
        session = CongressSession(session=session_num)
        session.save()
    # Then get the type and number
    type = XML.amendment.get('chamber')
    number = XML.amendment.get('number')
    if not type or not number:
        return 'Missing chamber or number in amendment tag'

    #Get legislation identifiers
    bill_type = XML.amends.get('type')
    bill_number = XML.amends.get('number')
    if not bill_type or bill_number:
        return 'Missing type or number in amends tag'
    # Find legislation
    legislation = Legislation.lg.get_or_none(bill_type=bill_type,bill_number=bill_number,session=session)
    if not legislation:
        return 'Missing legislation with ID ' + str(session_num) + '-' + bill_type + bill_number

    # Find or initialize the amendment
    amendment = LegislationAmendment.lg.get_or_none(session=session,type=type,number=number)
    if not amendment:
        amendment = LegislationAmendment(session=session,type=type,number=number,legislation=legislation)

    # Get update dates
    updated = None
    if XML.amendment.has_key('updated'):
        updated = parseDateTime(XML.amendment['updated'])
    last_updated = None
    if amendment.updated:
        last_updated = amendment.updated

    # If we don't know what update this is, or this is the most recent update
    if not last_updated or not updated or (last_updated - updated).total_seconds() <= 0:
        # Update all fields!
        if updated:
            amendment.updated = updated

        if XML.amends.has_key('sequence'):
            amendment.sequence = XML.amends['sequence']

        if XML.status:
            if XML.status.has_key('datetime'):
                self.status_datetime = parseDateTime(XML.status['datetime'])
            self.status_text = XML.status.text

        if XML.sponsor and XML.sponsor.has_key('id'):
            sponsor = UserProfile.lg.get_or_none(govtrack_id=int(XML.sponsor['id']))
            if sponsor:
                amendment.sponsor = sponsor

        if XML.offered and XML.offered.has_key('datetime'):
            self.offered_datetime = parseDateTime(XML.offered['datetime'])

        if XML.description:
            self.description = XML.description.text
        if XML.purpose:
            self.purpose = XML.purpose.text

    # Parses all actions (and sub actions)
    for actionXML in XML.actions.findChildren(recursive=False):
        # Get basic action data
        name = actionXML.name
        new_amendment_action = None

        if name is 'action':
            new_amendment_action = LegislationAction()
        elif name is 'calendar':
            new_amendment_action = LegislationCalendar()
        elif name is 'vote':
            new_amendment_action = LegislationVote()
        elif name is 'vote-aux':
            new_amendment_action = LegislationVote()
        elif name is 'topresident':
            new_amendment_action = LegislationToPresident()
        elif name is 'signed':
            new_amendment_action = LegislationSigned()
        elif name is 'enacted':
            new_amendment_action = LegislationAction()

        if not new_amendment_action:
            continue

        new_amendment_action.parseGovtrack(actionXML,amendment=amendment)

    amendment.save()
    return ''


#-----------------------------------------------------------------------------------------------------------------------
# Counts the number of govtrack legislation amendment files there are
#-----------------------------------------------------------------------------------------------------------------------
def countXMLAmendments():
    count = 0
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/bills.amdt/"
        fileListing = os.listdir(filePath)
        fileCount = filecount(filePath)
        for infile in fileListing:
            db.reset_queries()
            if ".xml" in infile:
                count += 1
            else:
                pass
    return count

#-----------------------------------------------------------------------------------------------------------------------
# Initializes Voting Record files
#-----------------------------------------------------------------------------------------------------------------------
def initializeVotingRecord():
    missed_files = []
    print "[IMPORTANT]: The return of this function is a list of errors represented as tuples of the format (filepath,error_message).\n"\
          "[IMPORTANT]: If you would like to see this result, make sure you have assigned a variable to hold the return of this function"

    count = 0
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/rolls/"
        fileListing = os.listdir(filePath)

        for infile in fileListing:
            count += 1
            db.reset_queries()

            fileXML = open(filePath + infile)
            parsedXML = BeautifulSoup(fileXML)
            result = parseLegislationAmendment(parsedXML)

            if result is not '':
                print "[ERROR]: " + result + '.  CongressRoll was not initialized'
                missed_files.append((filePath + infile,result))

            if count%500 is 0:
                print str(count) + " files checked"

    return missed_files


#-----------------------------------------------------------------------------------------------------------------------
# Parses a CongressRoll
#-----------------------------------------------------------------------------------------------------------------------
def parseCongressRoll(XML):
    # Get identifying aspects
    where = XML.roll.get('where')
    session_number = XML.roll.get('session')
    roll_number = XML.roll.get('roll')
    if not where or not roll_number or not session_number:
        return 'Missing house location (where), session number, or roll number'

    if not XML.roll.has_key('datetime'):
        return 'Missing datetime'
    datetime = parseDateTime(XML.roll['datetime'])

    # Get session
    session = CongressSessions.lg.get_or_none(session=session_number)
    if not session:
        session = CongressSession(session=session_number)
        session.save()

    # Initialize or find congress roll
    congress_roll = CongressRoll.lg.get_or_none(session=session,where=where,roll_number=roll_number,datetime=datetime)
    if not congress_roll:
        congress_roll = CongressRoll(session=session,where=where,roll_number=roll_number,datetime=datetime)

    # Get the bill for this roll
    if XML.bill:
        bill_session_num = XML.bill.get('session')

        if bill_session_num:
            bill_session = CongressSession.lg.get_or_none(session=bill_session_num)
            if not bill_session:
                bill_session = CongressSession(session=bill_session_num)
                bill_session.save()

            bill_type = XML.bill.get('type')
            bill_number = XML.bill.get('number')

            if bill_type and bill_number and bill_session:
                legislation = Legislation.lg.get_or_none(bill_type=bill_type,bill_number=bill_number,congress_session=bill_session)
                if legislation:
                    congress_roll.legislation = legislation

    # Get the amendment for this roll
    if XML.amendment:
        amendment_session_num = XML.amendment.get('session')

        if amendment_session_num:
            amendment_session = CongressSession.lg.get_or_none(session=amendment_session_num)
            if not amendment_session:
                amendment_session = CongressSession(sbession=amendment_session_num)
                amendment_session.save()

            amendment_type = None
            amendment_number = None
            unparsed_type = XML.amendment.get('number')
            if unparsed_type:
                i = 0
                while unparsed_type[i].isdigit():
                    i += 1
                amendment_type = unparsed_type[:i]
                amendment_number = unparsed_type[i:]

            if amendment_type and amendment_number and amendment_session:
                amendment = LegislationAmendment.lg.get_or_none(amendment_type=amendment_type,amendment_number=amendment_number,congress_session=amendment_session)
                if amendment:
                    congress_roll.amendment = amendment

    updated = None
    if XML.roll.has_key('updated'):
        updated = parseDateTime(XML.roll['updated'])
    last_updated = congress_roll.updated

    # Update things if this is not an older version
    if not last_updated or not updated or (last_updated - updated).total_seconds() <= 0:
        if updated:
            congress_roll.updated = updated
        if XML.roll.has_key('source'):
            congress_roll.source = XML.roll['source']
        if XML.roll.has_key('aye'):
            congress_roll.aye = int(XML.roll['aye'])
        if XML.roll.has_key('nay'):
            congress_roll.nay = int(XML.roll['nay'])
        if XML.roll.has_key('nv'):
            congress_roll.nv = int(XML.roll['nv'])
        if XML.roll.has_key('present'):
            congress_roll.present = int(XML.roll['present'])
        if XML.roll.has_key('category'):
            congress_roll.category = XML.category.text
        if XML.roll.has_key('type'):
            congress_roll.type = XML.type.text
        if XML.roll.has_key('question'):
            congress_roll.question = XML.question.text
        if XML.roll.has_key('required'):
            congress_roll.required = XML.required.text
        if XML.roll.has_key('result'):
            congress_roll.result = XML.result.text

    congress_roll.save()

    for voterXML in XML.roll.findChildren('voter'):
        voter_id = voterXML.get('id')
        if not voter_id:
            print "[WARNING]: Voter tag without ID.  Vote not parsed.  Congress Roll #" + str(roll_number)
            continue

        voter = UserProfile.lg.get_or_none(govtrack_id=voter_id)
        if not voter:
            print "[WARNING]: Voter not found in database.  Vote not parsed.  Congress Roll #" + str(roll_number) + " and Voter ID #" + str(voter_id)
            continue

        key = voterXML.get('vote')
        value = voterXML.get('value')
        # If only key or value is instantiated
        if bool(key) != bool(value):
            # Replace the other value with the corresponding value
            for (k,v) in GOVTRACK_VOTES:
                if key is k:
                    value = v
                elif value is v:
                    key = k

        if not key and not value:
            print "[WARNING]: Voter tag without vote or value.  Vote not parsed.  Congress Roll #" + str(roll_number) + " and Voter ID #" + str(voter_id)
            continue

        vote = CongressVote.lg.get_or_none(roll=congress_roll,key=key,value=value,voter=voter)
        if not vote:
            vote = CongressVote(roll=congress_roll,key=key,value=value,voter=voter)
            vote.save()



#-------------------------------------------------------------------------------------------------------------------
# A Function that counts all the voting record files
#-------------------------------------------------------------------------------------------------------------------
def countVotingRecords():
    count = 0
    for num in range(109,113):
        filePath = '/data/govtrack/' + str(num) + "/rolls/"
        count += filecount(filePath)
    return count


#-------------------------------------------------------------------------------------------------------------------
# Wrapper for create user helper which makes a superuser.
#-------------------------------------------------------------------------------------------------------------------
def superUserHelper(control):
    from lovegov.modernpolitics.register import createUserHelper
    name = control.first_name + " " + control.last_name
    user_profile = createUserHelper(control=control, name=name)
    user_profile.confirmed = True
    user_profile.developer = True
    user_profile.save()
    control.user_profile = user_profile
    control.save()
    return user_profile


#-----------------------------------------------------------------------------------------------------------------------
# Checks each party and creates one if it doesn't exist
#-----------------------------------------------------------------------------------------------------------------------
def initializeParties():
    for type in PARTY_TYPE:
        print 'Finding ' + type[1] + ' party'
        already = Party.lg.get_or_none(party_type=type[0])

        if not already:
            print 'Party not found, creating ' + type[1] + ' party'

            party = Party(alias=type[1],party_type=type[0])
            party.title = type[1].capitalize() + " Party"
            party.autoSave()

            ref = 'frontend/static/images/party_labels/' + type[1] + '.png'
            full_ref = os.path.join(PROJECT_PATH, ref)
            file = open(full_ref)
            party.party_label.save(photoKey(".png"), File(file))


def initFirstLogin():
    for p in UserProfile.objects.all():
        if p.alias=="anonymous":
            p.first_login = FIRST_LOGIN_LAST_STAGE
        else:
            p.first_login = 0
        p.save()
