
########################################################################################################################
################################################# GEOGRAPHICAL DATA ####################################################

class US_State(LGModel):
    name = models.CharField(max_length=50)

class US_Counties(LGModel):
    name = models.CharField(max_length=50)
    state = models.OneToOneField(US_State)

class US_ConDistr(LGModel):
    number = models.IntegerField()
    state = models.OneToOneField(US_State)


########################################################################################################################
########################################################################################################################


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







########################################################################################################################
########################################################################################################################
#   Lovegov settings.
#
########################################################################################################################
#####################################################################################################################
class LoveGov(LGModel):
    default = models.BooleanField()             # for getting THEONE
    average_votes = models.IntegerField(default=1)       # the average number of votes on a piece of in_search content
    average_rating = models.IntegerField(default=50)      # the average rating of a piece of content in in_search
    lovegov_user = models.ForeignKey(UserProfile, null=True, related_name="lovegovuser")
    lovegov_group = models.ForeignKey(Group, null=True, related_name="anonuser")
    anon_user = models.ForeignKey(UserProfile, null=True) # user who represents anonymous users
    default_image = models.ForeignKey(UserImage, null=True)
    default_filter = models.ForeignKey(FilterSetting, null=True, related_name="defaultfilter")
    best_filter = models.ForeignKey(FilterSetting, null=True, related_name="bestfilter")
    new_filter = models.ForeignKey(FilterSetting, null=True, related_name="newfilter")
    hot_filter = models.ForeignKey(FilterSetting, null=True, related_name="hotfilter")
    worldview = models.ForeignKey(WorldView, null=True)

    def update(self):
        self.calcAverageVotes()
        self.calcAverageRating()

    def calcAverageVotes(self):
        total_content = Content.objects.filter(in_search=True).count()
        total_votes = Voted.objects.all().count()
        self.average_votes = max(int(total_votes / total_content), 1)
        self.save()

    def calcAverageRating(self):
        all_content = Content.objects.filter(in_search=True)
        count = 0
        sum = 0
        for c in all_content:
            rating = c.getRating()
            sum += rating
            count += 1
        self.average_rating = int((sum/count)*10)
        self.save()



#=======================================================================================================================
# Each setting has a name and value, for any given setting, there should be only one default=True
# this model is in addition to LoveGov, to make it easy to add settings after launch.. without
# necessarily having to migrate
#=======================================================================================================================
class LoveGovSetting(LGModel):
    default = models.BooleanField()
    setting = models.CharField(max_length=30)           # unique identifier
    value = models.CharField(max_length=50)
