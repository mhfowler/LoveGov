from lovegov.modernpolitics.initialize import *

## recalculate who normal users all ##
def recalculateNormalUsers():
    ghosts = UserProfile.objects.filter(ghost=True)
    for g in ghosts:
        g.normal = False
        g.save()
    lg = getLoveGovUser()
    lg.normal = False
    lg.save()
    anon = getAnonUser()
    anon.normal = False
    anon.save()
    trial = getTrialUser()
    trial.normal = False
    trial.save()

## recalculate official question order ##
def recalculateOfficialQuestionOrder():

    q = Question.objects.get(id=171412)     # water policy
    q.official_order = 1
    q.save()

    q = Question.objects.get(id=170853)     # health insurance
    q.official_order = 2
    q.save()

    q = Question.objects.get(id=38)         # offshore drilling
    q.official_order = 3
    q.save()

    q = Question.objects.get(id=39)         # search
    q.official_order = 4
    q.save()

    q = Question.objects.get(id=46)         # energy efficient technologies for our automobiles
    q.official_order = 5
    q.save()

    q = Question.objects.get(id=30)         # funding for its conservation projects
    q.official_order = 6
    q.save()

    q = Question.objects.get(id=18)         # economic stimulus package
    q.official_order = 7
    q.save()

    q = Question.objects.get(id=26)         # advocacy organizations
    q.official_order = 8
    q.save()

    q = Question.objects.get(id=9)          # the Obama Administration's healthcare reform
    q.official_order = 9
    q.save()

    q = Question.objects.get(id=4)          # abortion
    q.official_order = 10
    q.save()

## delete all ghost responses ##
def deleteAllGhostResponses():
    ghosts = UserProfile.objects.filter(ghost=True)
    responses = Response.objects.filter(creator__in=ghosts)
    count = 0
    total = responses.count()
    print "total: " + str(total)
    started_when = datetime.datetime.now()
    for x in responses:
        x.delete()
        if not count % 100:
            print count
            printSecondsRemaining(started_when, count, total)
        count +=1

def printSecondsRemaining(started_when, completed, total):
    if completed:
        now = datetime.datetime.now()
        seconds_passed = (now - started_when).total_seconds()
        total_seconds = seconds_passed * total / float(completed)
        seconds_to_go = total_seconds - seconds_passed
        print "seconds to go: " + str(seconds_to_go)

## recalculate which congress rolls are important ##
def recalculateCongressRollImportance():
    count = 0
    rolls = CongressRoll.objects.all()
    print "total: " + str(rolls.count())
    num_important = 0
    for x in rolls:
        if x.setImportant():
            num_important += 1
        if not count % 20:
            print count
        count +=1
    print "# important: " + str(num_important)

## recalculate amendment titles ##
def recalculateAmendmentTitles():
    for l in LegislationAmendment.objects.all():
        l.title = l.description
        l.save()

## print ids for greg ##
def printQAids():
    questions = Question.objects.filter(official=True)
    for q in questions:
        print "-----------------------"
        print enc(str(q.id) + ": " + q.title)
        for a in q.answers.all():
            print enc("-$-$-$- " + str(a.id) + ": " + a.answer_text)

### recalculate location identifiers ###
def recalculateLocationIdentifiers():
    count = 0
    addresses = PhysicalAddress.objects.all()
    print "to do: " + str(len(addresses))
    for l in addresses:
        l.setIdentifier()
        count += 1
        if not count%20:
            print count

def recalculateContentLocationsByPostedTo():
    count = 0
    content = Content.objects.filter(in_feed=True)
    for c in content:
        if c.posted_to:
            g = c.posted_to
            if g.location:
                location = g.location
                c.setLocationByCityAndState(city=location.city, state=location.state)
                print c.get_name()
        count += 1
        if not count%20:
            print count

def recalculateQuestionPostedToByPoll():
    for q in Question.objects.all():
        p = q.top_poll
        if p:
            q.posted_to = p.posted_to
            q.save()
            print q.get_name()

### recalculate stale ###
def recalculateStaleContent():
    for u in UserProfile.objects.filter(ghost=False):
        print u.get_name()
        u.recalculateStaleContent()

### recalculate top polls for questions ###
def recalculateTopPolls():
    for q in Question.objects.all():
        q.updateTopPoll()
        print "+II+ " + q.get_name()

### recalculate anon user stuff ###
def recalculateAnonUserStuff():
    anon = getAnonUser()

    removeAllGroups(anon)

#    for p in Party.objects.all():
#        p.joinMember(anon)
#
#    anon.autoSubscribe()
#
#    e = Election.lg.get_or_none(alias="massachusetts_us_senate")
#    if e: followGroupAction(anon, e, True, "PRI")

    anon.location = None
    anon.bio = "If you're just visiting, " \
               "and haven't decided to join our community yet, then you are logged in as the anonymous user. "\
                "Until you register, you can browse what's happening on LoveGov but you can't post, answer questions " \
                "or vote on content. " \
               "We require registration to help avoid spam, bots and destructive activity. "\
                "\n" \
                "If you wish to continue using the site as anonymous after you sign up, you can always switch to anonymous mode. " \
                "When you are in anonymous mode, anything you do will appear to other users as though the anonymous user did it. " \
                "Just because you don't feel comfortable tying your activity to your personal identity doesn't mean your voice " \
                "shouldn't be heard. The anonymous user represents the views and activity of everyone using LoveGov anonymously. "

    anon.save()


def removeAllGroups(user):
    from lovegov.modernpolitics.actions import followGroupAction
    for g in user.getRealGroups():
        g.removeMember(user)
    for g in user.getSubscriptions():
        followGroupAction(user, g, False, "PRI")


### recalculate user aliases ###
def recalculateUserAliases():
    for u in UserProfile.objects.all():
        alias = u.makeAlias()
        print alias

### recalculate prohibited actions ###
def recalculateProhibitedActions():
    for c in ControllingUser.objects.all():
        p = c.getUserProfile()
        if p:
            if p.alias=="anonymous":
                c.prohibited_actions = ANONYMOUS_PROHIBITED_ACTIONS
            else:
                c.prohibited_actions = DEFAULT_PROHIBITED_ACTIONS
        c.save()

### recalculate creators ###
def recalculateCreators():
    c = Content.objects.all()
    anon = getAnonUser()
    print "total: ", str(c.count())
    count = 0
    changed = 0
    for x in c:
        if not count % 20:
            print str(count)
        creator = x.getCreator()
        if creator:
            u = UserProfile.lg.get_or_none(id=creator.id)
        else:
            u = None
        if not u:
            print "CHANGING CREATOR for ", x.get_name()
            x.creator = anon
            x.save()
            changed += 1
        count += 1
    print "TOTAL CHANGED: ", str(changed)

## recalculate group stats ##
def recalculateNumMembers():
    for x in Group.objects.all():
        print x.get_name()
        x.countMembers()

def recalculateGroupAliases():
    count = 0
    for g in Group.objects.all().reverse():
        g.makeAlias()
        print g.alias + " " + str(count)
        count += 1
    lg = Group.lg.get_or_none(system=True, title="LoveGov")
    if not lg:
        lg = getLoveGovGroup()
    lg.alias = "lovegov_group"
    lg.save()


##### RECALCULTE CONTENT STATS #####
def recalculatePetitions():
    for p in Petition.objects.all():
        print p.title
        signed = Signed.objects.filter(content=p)
        p.current = signed.count()
        p.save()
        for x in p.signers.all():
            print "resign: " + x.get_name()
            already = Signed.lg.get_or_none(user=x, content=p)
            if not already:
                p.signers.remove(x)
                p.sign(x)

        level = 0
        while p.current >= PETITION_LEVELS[level]:
            level += 1
        p.p_level = level
        p.goal = PETITION_LEVELS[level]
        p.save()

def recalculateQuestions():
    count = 0
    for q in Question.objects.all():
        q.recalculateNumResponses()
        count += 1
        if not count%20:
            print count

def recalculateInFeed():
    c = Content.objects.filter(in_feed=True)
    count = 0
    for x in c:
        x.in_feed = False
        x.save()
        count += 1
        if not count%20:
            print count
    in_feed = Content.objects.filter(type__in=FEED_CONTENT_TYPES)
    for x in in_feed:
        x.in_feed = True
        x.save()
        print "+II+ is in feed: " + x.get_name()

def recalculateAllContentStats():
    c = Content.objects.filter(in_feed=True)
    for x in c:
        print "+II+ calculating stats: " + x.get_name()
        x.calculateAllStats()

## user stats ##
def recalculateAllUserStats():
    users = UserProfile.objects.all()
    for user in users:
        print "Calculating Stats For " + user.get_name()
        user.calculateAllStats()

def recalculateExplanations():
    allresponses = Response.objects.all()
    for response in allresponses:
        if response.explanation:
            print "Adding explanation by "+response.creator.get_name()
            explanation = response.explanation
            response.addExplanation(explanation)


### recalculate everything ####
def recalculateEverything():
    recalculateProhibitedActions()
    recalculateCreators()
    recalculateNumMembers()
    recalculateGroupAliases()

    recalculateInFeed()
    recalculatePetitions()
    recalculateQuestions()
    recalculateAllContentStats()
    recalculateAllUserStats()









#################################   CLEAN   #####################################################

def cleanWorldViews():

    q = Question.objects.all()
    num_q = q.count()
    print "num Q:" + str(num_q)

    deleted = 0
    u = UserProfile.objects.filter(num_answers__gt=num_q)
    print str(u.count()) + " users with TOO MANY answers"
    for x in u:
        print x.get_name()
        responses_count = {}
        responses = x.view.responses.all()
        for r in responses:
            q_id = r.question.id
            if not q_id in responses_count:
                responses_count[q_id] = 1
            else:
                responses_count[q_id] += 1
        for k,v in responses_count.items():
            if v > 1:
                dup_responses = responses.filter(question_id=k)
                non_answer = dup_responses.filter(most_chosen_answer=None)
                if non_answer:
                    print "there were non answers for " + x.get_name()
                    for h in non_answer:
                        h.delete()
                else:
                    for to_delete in dup_responses[1:]:
                        deleted += 1
                        to_delete.delete()

    print "responses deleted: " + str(deleted)












#### FOLLOW GROUPS #####
def recalculateAllFollowGroups():
    users = UserProfile.objects.filter(ghost=False)
    for user in users:
        print "Calculating Follow Groups For " + user.get_name()
        user.calculateFollowersAndFollowing()

def createAllFollowGroups():
    users = UserProfile.objects.all()
    for user in users:
        print "Creating for " + user.get_name()
        user.createFollowMeGroup()
        user.createIFollowGroup()


########################################################################################################################


### recalculate specific or deprecated ###

def recalculateAllVotes():
    content = Content.objects.all()
    for c in content:
        print "Calculating Votes For " + c.get_name()
        c.calculateVotes()

def recalculateAllComments():
    content = Content.objects.filter(type__in=HAS_HOT_SCORE)
    for c in content:
        print "Calculating Comments for " + c.get_name()
        c.calculateNumComments()

## ran sep 4
def recalculateUserUpVotes():
    for u in UserProfile.objects.all():
        score = u.calculateUpVotes()
        print "+II+ calculated " + u.get_name() + ": " + str(score)

def recalculateTopics():
    mt_ids = getMainTopics().values_list('id', flat=True)
    c = Content.objects.exclude(main_topic_id__in=mt_ids)
    count = 0
    for x in c:
        x.setMainTopic()
        if (count%20==0):
            print count
        count += 1


# set parent topics to none and delete all topics which are not main topics
def purgeTopics():
    for t in Topic.objects.all():
        t.parent_topic = None
        t.save()
    for t in Topic.objects.all():
        if t not in getMainTopics():
            print "Deleting topic "+t.topic_text
            t.delete()






#### set text for content #####
def setLoveGovPollText():

    text = "We wrote these questions based on recent legislation. " \
           "Take the LoveGov poll to see how you match up with your Congressmen and other users. "

    lgpoll = getLoveGovPoll()
    lgpoll.summary = text
    lgpoll.description = text
    lgpoll.save()

def setCongressText():

    text = "Follow this group to keep track of legislation and other happenings" \
           "by your federal representatives and senators."

    congress = getCongressGroup()
    congress.full_text = text
    congress.summary = text
    congress.save()

def setLoveGovUserText():

    text = "LoveGov is a robot, and its " \
           "views are the aggregate of all of the people of LoveGov. For every question " \
           "its response is the most commonly chosen response to that question. " \
           "LoveGov updates its responses every hour, so if your views have not been " \
           "taken into account yet, they will be soon. "

    lg = getLoveGovUser()
    lg.bio = text
    lg.save()


def setStateGroupText(state_group):

    key = state_group.location.state
    state_name = STATES_DICT.get(key)

    text = "This is the central place for everything relevant to " + state_name + ". " \
           "Use this group to find out what is going on and generate awareness for your cause: " \
           "share the important news/legislation, have discussions, and poll your state on the key issues. "

    state_group.full_text = text
    state_group.summary = text
    state_group.save()


def setCityGroupText(city_group):

    text = "This is an auto-generated group for people from " + city_group.getLocationVerbose(verbose=True) + ". " \
           "Use this group to stay up to date, share news, have discussions" \
           " and poll the community to find out where everyone stands. " \
           "If you have something specific you are working on, this is the place to generate awareness."

    city_group.full_text = text
    city_group.summary = text
    city_group.save()


def setEducationText(network):

    text = "This is an auto-generated group for students and alumni from " + network.get_name() + ". " \
           "Students, groups, and alumni should use this to coordinate your efforts, " \
           "generate awareness for your initiatives, and recruit more members. " \
           "Share important news, have discussions, and create & answer polls so you can find out where people stand."

    network.full_text = text
    network.summary = text
    network.save()


def setNetworkText(network):

    text = "This is an auto-generated group. " \
           "Share important news, have discussions, and create & answer polls so you can find out where people stand."

    network.full_text = text
    network.summary = text
    network.save()


def setPartyText(party):

    text = "This is a group auto-generated for a mainstream political party. " \
           "Join to show your true colors, or just follow to stay informed."

    party.full_text = text
    party.summary = text
    party.save()


def recalculateAutoGenDescriptions():

    setCongressText()

    for n in Network.objects.all():
        setNetworkText(n)
        print n.get_name()

    for c in TownGroup.objects.all():
        setCityGroupText(c)
        print c.get_name()

    for s in StateGroup.objects.all():
        setStateGroupText(s)
        print s.get_name()

    for p in Party.objects.all():
        setPartyText(p)
        print p.get_name()

    setLoveGovPollText()

    setStateGroupTitles()
    setTownGroupTitles()


def setStateGroupTitles():
    print "setting state group titles"
    for s in StateGroup.objects.all():
        s.title = s.makeTitle()
        s.save()
        print s.get_name()

def setTownGroupTitles():
    print "setting town group titles"
    for t in TownGroup.objects.all():
        t.title = t.makeTitle()
        t.save()
        print t.get_name()


#### POLITCIIAN STUFF ####
def calculateResponseAnswers():
    count = 0
    for response in Response.objects.all():
        if (not response.most_chosen_answer) and response.question:
            for answer in response.question.answers.all():
                if response.answer_val != -1 and answer.value == response.answer_val:
                    response.most_chosen_answer = answer
                    response.save()
                    count += 1
                    print count



def calculatePoliticianTitles():
    for p in UserProfile.objects.filter(politician=True):
        offices_held = p.relationships.filter(relationship_type="OH")

        if not offices_held:
            p.political_title = "Politician"
            p.save()

        else:
            title = ''

            offices_held = map( lambda x : x.downcast() , offices_held )
            offices_held.sort(reverse=True)
            recent_office = offices_held[0].office

            for t in recent_office.tags.all():
                if t.name == 'senator':
                    title = "Senator"
                elif t.name == 'representative':
                    title = "Representative"

            if title:
#                loc = ''
#                loc += recent_office.location.state
#                if recent_office.location.district != -1:
#                    loc += "-" + str(recent_office.location.district)
#
#                if loc:
#                    title += " [" + loc + "]"

                p.political_title = title
                p.save()


def removeDeprecatedPoliticians():
    print "Tags:"
    print "======================"
    print "+II+ = Information"
    print "+EE+ = Error"
    print "+WW+ = Warning"
    print "======================"
    # For all politicians (with govtrack ids)
    for p in UserProfile.objects.filter(politician=True,ghost=True):
        # Find anyone with that same alias
        dups = UserProfile.objects.filter(alias=p.alias)
        for person in dups:
            # Any person who also has that alias
            if not person.politician and not person.ghost:
                # Is most likely a deprecated politician
                print "+II+ Deleting " + person.get_name() + " - Num duplicates: " + str(len(dups))
                person.delete()

    # Do it again! except with name
    for p in UserProfile.objects.filter(politician=True,ghost=True):
        # Find anyone with that same name
        dups = UserProfile.objects.filter(first_name=p.first_name,last_name=p.last_name)
        for person in dups:
            # Any person who also has that name
            if not person.politician and not person.ghost:
                # Is most likely a deprecated politician
                print "+II+ Deleting " + person.get_name() + " - Num duplicates: " + str(len(dups))
                person.delete()


def resetGroupSystemBooleans():
    print "SETTING ALL NETWORKS TO AUTOGEN=True and SYSTEM=False"
    for n in Network.objects.all():
        print "resetting, " + n.get_name()
        n.autogen = True
        n.system = False
        n.save()
    print "SETTING ALL SYSTEM GROUPS TO ALSO BE HIDDEN"
    for g in Group.objects.filter(system=True):
        g.hidden = True
        g.save()
    print "SETTING CONGRESS NETWORK TO SYSTEM=True Hidden=False"
    c = getCongressNetwork()
    c.system = True
    c.hidden = False
    c.save()
    for c in Committee.objects.all():
        c.system = True
        c.save()

def updatePartyImages():
    initializeParties()
    for type in PARTY_TYPE:
        print 'Updating ' + type[1] + ' party'
        party = Party.lg.get_or_none(party_type=type[0])

        ref = 'frontend/static/images/party_labels/' + type[1] + '.png'
        full_ref = os.path.join(PROJECT_PATH, ref)
        file = open(full_ref)
        party.party_label.save(photoKey(".png"), File(file))


def updatePoliticianImages():

#    romney = UserProfile.objects.get(first_name="Mitt",last_name="Romney", politician=True)
#    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/romney.jpeg')
#    im = open(im_ref)
#    romney.setProfileImage(im)
#
#    elizabeth = UserProfile.objects.get(first_name="Elizabeth", last_name="Warren", politician=True)
#    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/warren.jpeg')
#    im = open(im_ref)
#    elizabeth.setProfileImage(im)
#
#    cicilline = UserProfile.objects.get(first_name="David", last_name="Cicilline", politician=True)
#    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/cicilline.jpeg')
#    im = open(im_ref)
#    cicilline.setProfileImage(im)

    johnson = UserProfile.objects.get(first_name="Gary", last_name="Johnson", politician=True)
    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/johnson.jpeg')
    im = open(im_ref)
    johnson.setProfileImage(im)

    stein = UserProfile.objects.get(first_name="Jillian", last_name="Stein", politician=True)
    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/stein.jpeg')
    im = open(im_ref)
    stein.setProfileImage(im)
