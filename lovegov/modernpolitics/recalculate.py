from lovegov.modernpolitics.initialize import *

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

    romney = Politician.objects.get(first_name="Mitt",last_name="Romney")
    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/romney.jpeg')
    im = open(im_ref)
    romney.setProfileImage(im)

    elizabeth = Politician.objects.get(first_name="Elizabeth", last_name="Warren")
    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/warren.jpeg')
    im = open(im_ref)
    elizabeth.setProfileImage(im)

    cicilline = ElectedOfficial.objects.get(first_name="David", last_name="Cicilline")
    im_ref = os.path.join(PROJECT_PATH, 'frontend/static/images/presidentialCandidates/cicilline.jpeg')
    im = open(im_ref)
    cicilline.setProfileImage(im)


def recalculateAllUserStats():
    users = UserProfile.objects.all()
    for user in users:
        print "Calculating Stats For " + user.get_name()
        user.userStatsRecalculate()


def recalculateAllFollowGroups():
    users = UserProfile.objects.filter(ghost=False)
    for user in users:
        print "Calculating Follow Groups For " + user.get_name()
        user.userFollowRecalculate()


def recalculateAllVotes():
    content = Content.objects.all()
    for c in content:
        print "Calculating Votes For " + c.get_name()
        c.recalculateVotes()


def recalculateAllComments():
    commentable = ['P','N','Q']
    content = Content.objects.filter(type__in=commentable)

    for c in content:
        print "Calculating Comments for " + c.get_name()
        c.contentCommentsRecalculate()


def createAllFollowGroups():
    users = UserProfile.objects.all()
    for user in users:
        print "Creating for " + user.get_name()
        user.createFollowMeGroup()
        user.createIFollowGroup()


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


def recalculateEverything():
    print "Recalculating Stats..."
    recalculateAllUserStats()
    print "Recalculating Follow Groups..."
    recalculateAllFollowGroups()
    print "Recalculating Votes..."
    recalculateAllVotes()
    print "Recalculating Comments..."
    recalculateAllComments()


def recalculateProhibitedActions():
    for c in ControllingUser.objects.all():
        p = c.getUserProfile()
        if p:
            if p.alias=="anonymous":
                c.prohibited_actions = ANONYMOUS_PROHIBITED_ACTIONS
            else:
                c.prohibited_actions = DEFAULT_PROHIBITED_ACTIONS
        c.save()


def recalculateInFeed():
    c = Content.objects.filter(in_feed=True)
    for x in c:
        x.in_feed = False
        x.save()
    p = Petition.objects.all()
    for x in p:
        x.in_feed = True
        x.save()
    n = News.objects.all()
    for x in n:
        x.in_feed = True
        x.save()
    g = UserGroup.objects.all()
    for x in g:
        if x.group_privacy != "S":
            x.in_feed = True
            x.save()


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
        u = UserProfile.lg.get_or_none(id=creator.id)
        if not u:
            print "CHANGING CREATOR for ", x.get_name()
            x.creator = anon
            x.save()
            changed += 1
        count += 1
    print "TOTAL CHANGED: ", str(changed)


def recalculateNumMembers():
    for x in Group.objects.all():
        print x.get_name()
        x.countMembers()


def calculateResponseAnswers():
    count = 0
    for response in Response.objects.all():
        if (not response.most_chosen_answer) and response.question:
            for answer in response.question.answers.all():
                if response.answer_val != -1 and answer.value == response.answer_val:
                    response.answer = answer
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
                loc = ''
                loc += recent_office.location.state
                if recent_office.location.district != -1:
                    loc += "-" + str(recent_office.location.district)

                if loc:
                    title += " [" + loc + "]"

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