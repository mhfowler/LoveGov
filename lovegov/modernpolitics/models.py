########################################################################################################################
########################################################################################################################
#
#           Models
#
#
########################################################################################################################
########################################################################################################################

# django
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.core.files import File
from django.http import *
from django.db.models import Q
from django.template.loader import render_to_string
from django import shortcuts

# python
import random
import thread
import json
from datetime import timedelta
from datetime import datetime

# lovegov
from lovegov.modernpolitics import custom_fields
from lovegov.modernpolitics import send_email
from lovegov.local_manage import LOCAL
from lovegov.modernpolitics.constants import *

import logging


logger = logging.getLogger('filelogger')
scheduled_logger = logging.getLogger('scheduledlogger')

#-----------------------------------------------------------------------------------------------------------------------
# Useful manager for all our models.
#-----------------------------------------------------------------------------------------------------------------------
class LGManager(models.Manager):
    """Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

#-----------------------------------------------------------------------------------------------------------------------
# Our model
#-----------------------------------------------------------------------------------------------------------------------
class LGModel(models.Model):
    lg = LGManager()
    objects = models.Manager()
    class Meta:
        abstract = True

#=======================================================================================================================
# Abstract class for all models which should be governed by privacy constraints.
#
#=======================================================================================================================
class Privacy(LGModel):
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='PUB')
    creator = models.ForeignKey("UserProfile", default=154)             # 154 is lovegov user
    class Meta:
        abstract = True
    #-------------------------------------------------------------------------------------------------------------------
    # Returns boolean, as to whether user has permission to view this.
    #-------------------------------------------------------------------------------------------------------------------
    def getPermission(self, user):
        if self.privacy == 'PUB':
            return True
        elif self.privacy == 'PRI':
            if user == self.creator:
                return True
            else:
                return False

    #-------------------------------------------------------------------------------------------------------------------
    # Returns user who created this.
    #-------------------------------------------------------------------------------------------------------------------
    def getCreator(self):
        try:
            creator = self.creator
        except UserProfile.DoesNotExist:
            from modernpolitics.backend import getLoveGovUser
            return getLoveGovUser() 
        return creator

    #-------------------------------------------------------------------------------------------------------------------
    # Return boolean based on privacy.
    #-------------------------------------------------------------------------------------------------------------------
    def getPrivate(self):
        return self.privacy == 'PRI'

    def getPublic(self):
        return self.privacy == 'PUB'

#=======================================================================================================================
# physical address
#=======================================================================================================================
class UserPhysicalAddress(LGModel):
    user = models.IntegerField()
    address_string = models.CharField(max_length=500, null=True)
    zip = models.CharField(max_length=20, null=True)
    longitude = models.DecimalField(max_digits=30, decimal_places=15)
    latitude = models.DecimalField(max_digits=30, decimal_places=15)
    state = models.CharField(max_length=2)
    district = models.IntegerField()


class PhysicalAddress(LGModel):
    address_string = models.CharField(max_length=500, null=True)
    zip = models.CharField(max_length=20, null=True)
    longitude = models.DecimalField(max_digits=30, decimal_places=15)
    latitude = models.DecimalField(max_digits=30, decimal_places=15)
    state = models.CharField(max_length=2)
    district = models.IntegerField()

#=======================================================================================================================
# Abstract tuple for representing what location and scale content is applicable to.
#=======================================================================================================================
class LocationLevel(models.Model):
    location = models.ForeignKey(PhysicalAddress, null=True)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, default='W')
    class Meta:
        abstract = True

#=======================================================================================================================
# Topic
#
#
#=======================================================================================================================
class Topic(LGModel):
    # unique identifier
    alias = models.CharField(max_length=30, default="default")
    # actual topic stuff
    topic_text = models.CharField(max_length=50)
    parent_topic = models.ForeignKey("self", null=True)
    forum = models.ForeignKey("Forum", null=True)                        # foreign key to forum
    # fields for images
    image = models.ImageField(null=True, upload_to="defaults/")
    hover = models.ImageField(null=True, upload_to="defaults/")
    selected = models.ImageField(null=True, upload_to="defaults/")

    def __unicode__(self):
        return self.topic_text

    def getColors(self):
        return {'color':self.color,'color_light':self.color_light}

    def getQuestions(self):
        ids = []
        for q in Question.objects.filter(official=True):
            if q.getMainTopic() == self:
                ids.append(q.id)
        return Question.objects.filter(id__in=ids).order_by("-rank")

    def getContent(self):
        ids = []
        for c in Content.objects.filter(Q(type='P') | Q(type='N')):
            if c.getMainTopic() == self:
                ids.append(c.id)
        return Content.objects.filter(id__in=ids)

    def getPre(self):
        return self.alias[0:3]

    def getForum(self):
        if self.forum_id == -1:
            return None
        else:
            forum = Forum.objects.get(id=self.forum_id)
            return forum

    def getImageRef(self):
        return MAIN_TOPICS_IMG[self.topic_text]

    def getMiniImageRef(self):
        return MAIN_TOPICS_MINI_IMG[self.topic_text]

    def getUserImage(self):
        from modernpolitics.backend import getTopicImage
        return getTopicImage(self)

    def get_url(self):
        return '/topic/' + self.alias + '/'

    def makeAlias(self):
        words = self.topic_text.split()
        alias = ""
        for w in words:
            alias += str.lower(str(w))
        self.alias = alias
        self.save()


#=======================================================================================================================
# Content
#
#=======================================================================================================================
class Content(Privacy, LocationLevel):
    # unique identifier
    alias = models.CharField(max_length=1000, default="default")
    # optimizations for excluding some types of content
    in_feed = models.BooleanField(default=False)
    in_search = models.BooleanField(default=True)
    in_calc = models.BooleanField(default=True)
    # FIELDS
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    topics = models.ManyToManyField(Topic)
    main_topic = models.ForeignKey(Topic, null=True, related_name="maintopic")
    title = models.CharField(max_length=500)
    summary = models.TextField(max_length=500, blank=True, null=True)
    created_when = models.DateTimeField(auto_now_add=True)
    main_image = models.ForeignKey("UserImage", null=True)
    active = models.BooleanField(default=True)
    calculated_view = models.ForeignKey("WorldView", null=True)     # foreign key to worldview
    # RANK, VOTES
    status = models.IntegerField(default=STATUS_CREATION)
    rank = models.DecimalField(default="0.0", max_digits=4, decimal_places=2)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)

    #-------------------------------------------------------------------------------------------------------------------
    # Gets url for viewing detail of this content.
    #-------------------------------------------------------------------------------------------------------------------
    def get_url(self):
        if self.type=='P':
            return '/petition/' + str(self.id) + '/'
        elif self.type=='N':
            return '/news/' + str(self.id) + '/'
        elif self.type=='Q':
            return '/question/' + str(self.id) + '/'
        elif self.type=='F':
            return '/topic/' + self.getMainTopic().alias + '/'
        elif self.type=='G':
            return '/group/' + str(self.id) + '/'
        elif self.type=='C':
            return self.downcast().root_content.getUrl()
        elif self.type=='R':
            return self.downcast().question.getUrl()
        else:
            return '/display/' + str(self.id) + '/'

    def getUrl(self):
        return self.get_url()

    #-------------------------------------------------------------------------------------------------------------------
    # Gets name of content for display.
    #-------------------------------------------------------------------------------------------------------------------
    def getName(self):
        return self.title
    def get_name(self):
        return self.getName()

    def getTitle(self):
        return self.title


    #-------------------------------------------------------------------------------------------------------------------
    # Gets main topic of content.
    #-------------------------------------------------------------------------------------------------------------------
    def getMainTopic(self):
        mt = self.main_topic
        if mt:
            return mt
        else:
            topics = self.topics.all()
            if topics:
                return topics[0]
            else:
                return Topic.objects.get(topic_text="Energy")

    #-------------------------------------------------------------------------------------------------------------------
    # Sets main_topic field.
    #-------------------------------------------------------------------------------------------------------------------
    def setMainTopic(self, topic=None):
        if not topic:
            self.main_topic = self.getMainTopic()
            self.save()
        else:
            self.main_topic = topic
            self.save()
            self.topics.add(topic)

    #-------------------------------------------------------------------------------------------------------------------
    # Get vote rating of content.
    #-------------------------------------------------------------------------------------------------------------------
    def getRating(self):
        votes = self.upvotes + (self.downvotes* DOWNVOTE_DAMPEN)
        if votes:
            rating = self.upvotes / votes
            return rating
        else: return 0

    #-------------------------------------------------------------------------------------------------------------------
    # Get querty set of all users who either agree or upvoted this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getSupporters(self):
        votes = Voted.objects.filter(content=self)
        supporter_ids = votes.filter(value=1).values_list('user', flat=True)
        supporters = UserProfile.objects.filter(id__in=supporter_ids)
        return supporters

    #-------------------------------------------------------------------------------------------------------------------
    # Sets image to inputted file.
    #-------------------------------------------------------------------------------------------------------------------
    def setMainImage(self, file):
        title = self.title + ' Image'
        summary = self.summary
        img = UserImage(title=title, summary=summary)
        img.createImage(File(file))
        creator = self.getCreator()
        img.autoSave(creator=creator, privacy=self.privacy)
        # add topics
        for t in self.topics.all():
            img.topics.add(t)
            # point self.image to new image
        self.main_image_id = img.id
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns UserImage associated with this content
    #-------------------------------------------------------------------------------------------------------------------
    def getMainImage(self):
        if self.main_image:
            image = UserImage.lg.get_or_none(id=self.main_image_id)
            if image:
                return image
            else:
                return self.getMainTopic().getUserImage()
        else:
            return self.getMainTopic().getUserImage()

    def getImage(self):
        return self.getMainImage().image

    #-------------------------------------------------------------------------------------------------------------------
    # Returns WorldView associated with this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getCalculatedView(self):
        view = WorldView.objects.filter(id=self.calculated_view_id)
        if view:
            return view[0]
        else:
            return None


    #-------------------------------------------------------------------------------------------------------------------
    # Saves a creation relationship for this content, with inputted creator and privacy.
    #-------------------------------------------------------------------------------------------------------------------
    def saveCreated(self, creator, privacy):
        self.creator = creator
        self.privacy = privacy
        self.save()
        # deprecate
        relationship = Created(user=creator,content=self,privacy=privacy)
        relationship.autoSave()
        # follow what you create by default
        follow = Followed(user=creator, content=self, privacy=privacy)
        follow.autoSave()
        logger.debug("created " + self.title)

    #-------------------------------------------------------------------------------------------------------------------
    # Saves a creation relationship for this content, with inputted creator and privacy.
    #-------------------------------------------------------------------------------------------------------------------
    def saveEdited(self, privacy):
        created = Created.objects.filter(content=self)[0]
        created.privacy = privacy
        created.save()
        self.privacy = privacy
        self.save()
        edited = Edited(user=created.user, content=self, privacy=privacy)
        edited.autoSave()

    #-------------------------------------------------------------------------------------------------------------------
    # Saves default created relationship... created by lovegov.
    #-------------------------------------------------------------------------------------------------------------------
    def saveDefaultCreated(self):
        from modernpolitics.backend import getLoveGovUser
        lovegov_user = getLoveGovUser()
        if lovegov_user:
            creator = lovegov_user
            self.saveCreated(creator=creator, privacy='PUB')

    #-------------------------------------------------------------------------------------------------------------------
    # Updates creation relationship for this content, with inputted creator and privacy. why would we do this?
    #-------------------------------------------------------------------------------------------------------------------
    def updateCreated(self, creator, privacy):
        when = datetime.datetime.now()
        relationship = Created.objects.filter(user=creator, content=self)[0]
        relationship.when = when
        relationship.privacy=privacy
        relationship.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Edits inputted field of content with inputted value.
    #-------------------------------------------------------------------------------------------------------------------
    def edit(self,field,value):
        if field == "title":
            self.title=value
        elif field == "summary":
            self.summary=value
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Downcasts content to appropriate child model.
    #-------------------------------------------------------------------------------------------------------------------
    def downcast(self):
        type = self.type
        if type == 'N':
            object = self.news
        elif type == 'P':
            object = self.petition
        elif type == 'E':
            object = self.event
        elif type == 'C':
            object = self.comment
        elif type == 'Q':
            object = self.question
        elif type == 'R':
            object = self.response.userresponse
        elif type == 'I':
            object = self.userimage
        elif type == 'G':
            object = self.group
        elif type == 'D':
            object = self.debate
        elif type == 'Y':
            object = self.persistent
        elif type == 'Z':
            object = self.response.aggregateresponse
        elif type == 'M':
            object = self.motion
        elif type == 'F':
            object = self.forum
        else: object = self
        return object

    #-------------------------------------------------------------------------------------------------------------------
    # Returns correct template file based on type of content.
    #-------------------------------------------------------------------------------------------------------------------
    def getTemplate(self):
        type = self.type
        if type == 'N':
            template = 'usable/display_news.html'
        elif type == 'P':
            template = 'usable/display_petition.html'
        elif type == 'E':
            template = 'usable/display_event.html'
        elif type == 'C':
            template = 'usable/display_comment.html'
        elif type == 'Q':
            template = 'usable/display_question.html'
        elif type == 'R':
            template = 'usable/display_response.html'
        elif type == 'I':
            template = 'usable/display_image.html'
        elif type == 'Y':
            template = 'usable/display_persistent_debate.html'
        elif type == 'Z':
            template = 'usable/display_aggregate.html'
        elif type == 'M':
            template = 'usable/display_motion.html'
        else: template = None
        return template

    #-------------------------------------------------------------------------------------------------------------------
    # Returns correct edit form for content, and populates it with post data if request is inputted
    #-------------------------------------------------------------------------------------------------------------------
    def getEditForm(self, request=None):
        type = self.type
        form = None
        if request:
            if type == 'N':
                form = forms.EditNewsForm(request.POST, instance=self)
            elif type == 'E':
                form = forms.EditEventForm(request.POST, instance=self)
            elif type == 'G':
                form = forms.EditGroupForm(request.POST, instance=self)
            elif type == 'P':
                form = forms.EditPetitionForm(request.POST, instance=self)
            elif type == 'M':
                form = forms.EditMotionForm(request.POST, instance=self)
        else:
            if type == 'N':
                form = forms.EditNewsForm(instance=self)
            elif type == 'E':
                form = forms.EditEventForm(instance=self)
            elif type == 'G':
                form = forms.EditGroupForm(instance=self)
            elif type == 'P':
                form = forms.EditPetitionForm(instance=self)
            elif type == 'M':
                form = forms.EditMotionForm(instance=self)
        return form

    #-------------------------------------------------------------------------------------------------------------------
    # Get creator name if viewing user has permission.
    #-------------------------------------------------------------------------------------------------------------------
    def getCreatorDisplayName(self, user, url=None):
        if self.getPublic():
            return self.getCreator().get_name()
        else:
            creator = self.getCreator()
            anon = creator.getAnonDisplay(url)
            if creator == user:
                anon += " (You)"
            return anon

    def getDisplayNameQuick(self):
        if self.privacy == 'PUB':
            return self.getCreator().get_name()
        else:
            return 'Anonymous'

    #-------------------------------------------------------------------------------------------------------------------
    # Get created relationship.
    #-------------------------------------------------------------------------------------------------------------------
    def getCreatedRelationship(self):
        created =  Created.objects.filter(content=self)
        if created:
            return created[0]
        else:
            return None

    #-------------------------------------------------------------------------------------------------------------------
    # Returns true if the inputted user should be able to see this content, false otherwise.
    #-------------------------------------------------------------------------------------------------------------------
    def GetPrivilege(self, user):
        if self.privacy == 'PUB':
            return True
        elif self.privacy == 'PRI':
            return False    # or we could check if creator
        else:
            privilege = user.privileges.filter(content=self)
            if privilege:
                return True
            else:
                return False

    #-------------------------------------------------------------------------------------------------------------------
    # Add like vote to content from inputted user (or adjust his vote appropriately)
    #-------------------------------------------------------------------------------------------------------------------
    def like(self, user, privacy):
        my_vote = Voted.lg.get_or_none(user=user, content=self)
        if my_vote:
            # if already liked, do nothing
            if my_vote.value == 1:
                pass
            # if disliked or neutral, increase vote by
            else:
                my_vote.value += 1
                my_vote.autoSave()
                # adjust content values about status and vote
                if my_vote.value == 1:
                    self.upvotes += 1
                    mod = 'L'
                else:
                    self.downvotes -= 1
                    mod = 'U'
                self.status += STATUS_VOTE
                self.save()
                action = Action(relationship=my_vote,modifier=mod)
                action.autoSave()
                self.creator.notify(action)
            return my_vote.value
        else:
            # create new vote
            new_vote = Voted(value=1, content=self, user=user, privacy=privacy)
            new_vote.autoSave()
            # adjust content values about status and vote
            self.upvotes += 1
            self.status += STATUS_VOTE
            self.save()
            action = Action(relationship=new_vote,modifier='L')
            action.autoSave()
            self.creator.notify(action)
            return new_vote.value

    #-------------------------------------------------------------------------------------------------------------------
    # Add dislike vote to content from inputted user (or adjust his vote appropriately)
    #-------------------------------------------------------------------------------------------------------------------
    def dislike(self, user, privacy):
        my_vote = Voted.lg.get_or_none(user=user, content=self)
        if my_vote:
            # if already disliked, do nothing
            if my_vote.value == -1:
                pass
            else:
                my_vote.value -= 1
                my_vote.autoSave()
                # adjust content values about status and vote
                if my_vote.value == -1:
                    self.downvotes += 1
                    mod = 'D'
                else:
                    self.upvotes -= 1
                    mod = 'U'
                self.status -= STATUS_VOTE
                self.save()
                action = Action(relationship=my_vote,modifier=mod)
                action.autoSave()
                self.creator.notify(action)
            return my_vote.value
        else:
            # create new vote
            new_vote = Voted(value=-1, content=self, user=user, privacy=privacy)
            new_vote.autoSave()
            # adjust content values about status and vote
            self.downvotes += 1
            self.status -= STATUS_VOTE
            self.save()
            action = Action(relationship=new_vote,modifier='D')
            action.autoSave()
            self.creator.notify(action)
            return new_vote.value

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a time delta of how old this content is.
    #-------------------------------------------------------------------------------------------------------------------
    def howOld(self):
        now = datetime.datetime.now()
        delta = now - self.created_when
        return delta

    #-------------------------------------------------------------------------------------------------------------------
    # Gets all links from this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getLinks(self):
        links = Linked.objects.filter(from_content=self).order_by('-link_strength')
        return links

    #-------------------------------------------------------------------------------------------------------------------
    # Returns boolean, as to whether user has permission to view this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getPermission(self, user):
        if self.privacy == 'PUB':
            return True
        elif self.privacy == 'PRI':
            if user == self.creator:
                return True
            else:
                return False
        elif self.privacy == 'FOL':
            if user == self.creator:
                return True
            else:
                following_creator = user.getIFollow().filter(to_user__id=self.creator.user_id)
                if following_creator:
                    return True
                else:
                    return False

    #-------------------------------------------------------------------------------------------------------------------
    # Saves creation info.
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        if not creator:
            self.saveDefaultCreated()
        else:
            self.saveCreated(creator=creator, privacy=privacy)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns query set of all UsersFollows following this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getUserFollowMe(self):
        return Followed.objects.filter(content=self)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Users who are (confirmed) following this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowMe(self, num=-1):
        follows = Followed.objects.filter(content=self)
        followers = []
        if num == -1:
            for f in follows:
                followers.append(f.user)
        else:
            i = 0
            while i < len(follows) and i < num:
                followers.append(follows[i].user)
        return followers

    #-------------------------------------------------------------------------------------------------------------------
    # Returns the total number of comments on this content, including replies.
    #-------------------------------------------------------------------------------------------------------------------
    def getNumComments(self):
        comments = Comment.objects.filter(on_content=self)
        num = len(comments)
        for c in comments:
            num += c.getNumComments()
        return num

    #-------------------------------------------------------------------------------------------------------------------
    # Returns the top comment.
    #-------------------------------------------------------------------------------------------------------------------
    def getTopComment(self):
        comments = Comment.objects.filter(on_content=self).order_by('-status')
        if comments:
            return comments[0]
        else:
            return None

#=======================================================================================================================
# UserImage
# use instead of image fields (to allow commenting and shit on images)
#=======================================================================================================================
class UserImage(Content):
    image = models.ImageField(upload_to='images/')
    def autoSave(self, creator=None, privacy='PUB'):
        self.type = 'I'
        self.save() # to get id
        self.main_image_id = self.id
        self.save()
        super(UserImage, self).autoSave(creator=creator, privacy=privacy)
    def createImage(self, file, type=".jpg"):
        from lovegov.modernpolitics.helpers import photoKey
        self.image.save(photoKey(type), File(file))
        self.save()

########################################################################################################################
########################################################################################################################
# USER MODELS
#
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# Stores basic info about a user.
#
#=======================================================================================================================
class BasicInfo(LGModel):
    profile_image = models.ForeignKey(UserImage, null=True)
    # ENUMS
    GENDER_CHOICES = ( ('M', 'Male'), ('F', 'Female'), ('N', 'None') )
    ROLE_CHOICES = ( ('V', 'Voter'), ('E', 'Elected Official') )
    # FIELDS
    middle_name = models.CharField(max_length=100, blank=True)
    nick_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    dob = models.DateField(null=True)
    address = custom_fields.ListField()
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.CharField(max_length=15, blank=True)
    url = custom_fields.ListField()
    religion = models.CharField(max_length=200, blank=True)
    ethnicity = models.CharField(max_length=30, blank=True)
    party = models.CharField(max_length=100, blank=True)
    political_role = models.CharField(max_length=1, choices=ROLE_CHOICES, blank=True)
    invite_message = models.CharField(max_length=10000, blank=True, default=DEFAULT_INVITE_MESSAGE)
    invite_subject = models.CharField(max_length=1000, blank=True, default=DEFAULT_INVITE_SUBJECT)

#=======================================================================================================================
# Tuple for storing a users involvement with content
#=======================================================================================================================
class Involved(LGModel):
    content = models.ForeignKey(Content)
    involvement = models.IntegerField()
    when = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# Tuple for storing a piece of content's place in feed.
#=======================================================================================================================
class FeedItem(LGModel):
    content = models.ForeignKey(Content)
    rank = models.IntegerField()

class Feed(LGModel):
    alias = models.CharField(max_length=30)
    items = models.ManyToManyField(FeedItem)
    def smartClear(self):
        self.items.all().delete()

#=======================================================================================================================
# Tuple for quick access to user's debate record.
#=======================================================================================================================
class DebateResult(LGModel):
    debate = models.IntegerField()  # foreign key to debate
    result = models.CharField(max_length=1)     # 'W', 'L', 'T'

#=======================================================================================================================
# For storing a user's settings for sending them email alerts about notifications for particular user or content..
# user_id and content... but only use one field
#=======================================================================================================================
class CustomNotificationSetting(LGModel):
    content = models.ForeignKey(Content, null=True)        # content this setting is associated with
    user = models.ForeignKey("UserProfile", null=True)              # user this setting is associated with
    email = models.BooleanField(default=True)
    alerts = custom_fields.ListField()                      # list of allowed types

    def checkNotify(self, type):
        setting = self.alerts.filter(type=type)
        if setting:
            return True
        else:
            return False

#=======================================================================================================================
# Topic weight, indicates how much to weigh a particular topic.
#=======================================================================================================================
class TopicWeight(LGModel):
    topic = models.ForeignKey(Topic)
    weight = models.IntegerField(default=100)       # percentage to weight topic

#=======================================================================================================================
# Type weight, indicates how much to weigh a particular type
#=======================================================================================================================
class TypeWeight(LGModel):
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    weight = models.IntegerField(default=100)       # percentage to weight type

#=======================================================================================================================
# For storing a ranking system's settings.
# default =-1 --> no filter
#=======================================================================================================================
class FilterSetting(LGModel):
    alias = models.CharField(max_length=30, default="default")  # unique identifier
    similarity = models.IntegerField(default=-1)    # filter by similarity percent users are to you
    days = models.IntegerField(default=-1)          # filter by how many days old max
    by_topic = models.BooleanField(default=False)   # boolean whether to use topic weights or not
    by_type = models.BooleanField(default=False)    # boolean whether to use type weights
    topic_weights = models.ManyToManyField(TopicWeight) # sum of all topic weights should be 100!
    type_weights = models.ManyToManyField(TypeWeight)   # sum of all type weights should be 100!
    algo = models.CharField(max_length=1, default='D', choices=ALGO_CHOICES)
    hot_window = models.IntegerField(default=HOT_WINDOW)
    def getTopicWeight(self, topic):
        to_return = self.topic_weights.filter(topic=topic)
        if to_return:
            return to_return[0].weight
        else:
            return 0
    def getTypeWeight(self, type):
        to_return = self.type_weights.filter(type=type)
        if to_return:
            return to_return[0].weight
        else:
            return 0


class SimpleFilter(LGModel):
    name = models.CharField(max_length=200, default="filter")
    ranking = models.CharField(max_length=1, choices=RANKING_CHOICES, default="H")
    topics = models.ManyToManyField(Topic)
    types = custom_fields.ListField()                  # list of char of included types
    levels = custom_fields.ListField(default=[])                 # list of char of included levels
    groups = models.ManyToManyField("Group")
    submissions_only = models.BooleanField(default=True) # switch between just created (True) and everything they upvoted (False)
    display = models.CharField(max_length=1, choices=FEED_DISPLAY_CHOICES, default="P")
    # which location
    location = models.ForeignKey("PhysicalAddress", null=True)

    def getDict(self):
        if self.submissions_only:
            submissions_only = 1
        else:
            submissions_only = 0
        topics = list(self.topics.all().values_list("id", flat=True))
        groups = list(self.groups.all().values_list("id", flat=True))
        to_return = {
            'name': self.name,
            'ranking': self.ranking,
            'types': json.dumps(self.types),
            'levels': json.dumps(self.levels),
            'topics': json.dumps(topics),
            'groups': json.dumps(groups),
            'submissions_only': submissions_only,
            'display': self.display
        }
        return to_return


#=======================================================================================================================
# To track promotional codes we advertise to users.
#
#=======================================================================================================================
class RegisterCode(LGModel):
    code_text = models.CharField(max_length=25)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True)

#=======================================================================================================================
# For storing anonymous user ids.
#
#=======================================================================================================================
class AnonID(LGModel):
    url = models.URLField()
    number = models.IntegerField()

#=======================================================================================================================
# Fields for userprofile
#=======================================================================================================================
class FacebookProfileModel(models.Model):
    '''
    Abstract class to add to your profile model.
    NOTE: If you don't use this this abstract class, make sure you copy/paste
    the fields in.
    '''
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(
        blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
        upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('m', 'Male'), ('f', 'Female')), blank=True, null=True)
    raw_data = models.TextField(blank=True)

    def __unicode__(self):
        return self.user.__unicode__()

    class Meta:
        abstract = True

    def getFBAlias(self):
        return self.facebook_profile_url.replace('http://www.facebook.com/', '')



#=======================================================================================================================
# Model for storing user of site. extends FacebookProfileModel, so that there are fields for that.
# extends django user
#=======================================================================================================================
def initView():
    view = WorldView()
    view.save()
    return view

class UserProfile(FacebookProfileModel, LGModel):
    # this is the primary user for this profile, mostly for fb login
    user = models.ForeignKey(User, null=True)
    # for downcasting
    user_type = models.CharField(max_length=1, choices=USER_CHOICES, default='G')
    # twitter integration
    twitter_user_id = models.IntegerField(null=True)
    twitter_screen_name = models.CharField(max_length=200, null=True)
    # info
    alias = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=500, null=True)      # for display, not for login!
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    # REGISTRATION
    registration_code = models.ForeignKey(RegisterCode,null=True)
    confirmed = models.BooleanField(default=False)
    confirmation_link = models.CharField(max_length=500)
    first_login = models.BooleanField(default=True) # for special case for first login
    developer = models.BooleanField(default=False)  # for developmentWrapper
    user_title = models.CharField(max_length=200,null=True)
    # INFO
    basicinfo = models.ForeignKey(BasicInfo, blank=True, null=True)
    view = models.ForeignKey("WorldView", default=initView)
    networks = models.ManyToManyField("Network", related_name='networks')
    location = models.ForeignKey(PhysicalAddress, null=True)
    # old address
    userAddress = models.ForeignKey(UserPhysicalAddress, null=True)
    # CONTENT LISTS
    last_answered = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now, blank=True)     # last time answer question
    debate_record = models.ManyToManyField(DebateResult)
    i_follow = models.ForeignKey('Group', null=True, related_name='i_follow')
    follow_me = models.ForeignKey('Group', null=True, related_name='follow_me')
    private_follow = models.BooleanField(default=False)
    my_involvement = models.ManyToManyField(Involved)       # deprecated
    my_history = models.ManyToManyField(Content, related_name = 'history')   # everything I have viewed
    privileges = models.ManyToManyField(Content, related_name = 'priv')     # for custom privacy these are the content I am allowed to see
    last_page_access = models.IntegerField(default=-1, null=True)       # foreign key to page access
    # feeds & ranking
    my_filters = models.ManyToManyField(SimpleFilter)
    # SETTINGS
    user_notification_setting = custom_fields.ListField()               # list of allowed types
    content_notification_setting = custom_fields.ListField()            # list of allowed types
    email_notification_setting = custom_fields.ListField()              # list of allowed types
    custom_notification_settings = models.ManyToManyField(CustomNotificationSetting)
    # anon ids
    anonymous = models.ManyToManyField(AnonID)
    type = models.CharField(max_length=1,default="U")
    # deprecated
    my_feed = models.ManyToManyField(FeedItem, related_name="newfeed")  # for storing feed based on my custom setting below
    filter_setting = models.ForeignKey(FilterSetting, null=True)
    evolve = models.BooleanField(default=False)     # boolean as to whether their filter setting should learn from them and evolve

    def __unicode__(self):
        return self.first_name
    def get_url(self):
        return '/profile/' + self.alias + '/'
    def getWebUrl(self):
        return '/profile/web/' + self.alias + '/'
    def getAlphaURL(self):
        return self.get_url()
    def get_name(self):
        try:
            to_return = (self.first_name + " " + self.last_name)
        except UnicodeEncodeError:
            to_return = "UnicodeEncodeError"
        return to_return
    def get_nameShort(self):
        try:
            fullname = str(self.first_name) + " " + str(self.last_name)
            if len(fullname) > 19:
                to_return = unicode(str(self.first_name)).encode("UTF-8")
            else:
                to_return = unicode(str(self.first_name) + " " + str(self.last_name)).encode("UTF-8")
        except UnicodeEncodeError:
            to_return = "UnicodeEncodeError"
        return to_return

    def isDeveloper(self):
        return self.developer

    #-------------------------------------------------------------------------------------------------------------------
    # Downcasts users appropriately based on type.
    #-------------------------------------------------------------------------------------------------------------------
    def downcast(self):
        if self.user_type == 'P':
            return self.politician
        elif self.user_type == 'S':
            return self.electedofficial.senator
        elif self.user_type == 'R':
            return self.electedofficial.representative
        else:
            return self

    #-------------------------------------------------------------------------------------------------------------------
    # Makes unique alias from name
    #-------------------------------------------------------------------------------------------------------------------
    def makeAlias(self):
        alias = str.lower((self.first_name.replace(" ","") + self.last_name).encode('utf-8','ignore'))
        users = UserProfile.objects.filter(alias=alias)
        while users:
            alias += '<3'
            users = users.filter(alias=alias)
        self.alias = alias
        self.save()
        return self.alias

    #-------------------------------------------------------------------------------------------------------------------
    # Init notif settings with defaults.
    #-------------------------------------------------------------------------------------------------------------------
    def initNotificationSettings(self):
        self.content_notification_setting = DEFAULT_CONTENT_NOTIFICATIONS
        self.user_notification_setting = DEFAULT_USER_NOTIFICATIONS
        self.email_notification_setting = DEFAULT_EMAIL_NOTIFICATIONS
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # get last page access
    #-------------------------------------------------------------------------------------------------------------------
    def getLastPageAccess(self):
        return PageAccess.lg.get_or_none(id=self.last_page_access)

    #-------------------------------------------------------------------------------------------------------------------
    # Gets anonymous id for the user for that url.
    #-------------------------------------------------------------------------------------------------------------------
    def getAnonID(self, url):
        anon = self.anonymous.filter(url=url)
        if not anon:
            anon = AnonID(url=url, number=random.randint(0,1000))
            anon.save()
            self.anonymous.add(anon)
        else: anon = anon[0]
        return anon.number

    def getAnonDisplay(self, url):
        if url:
            return "Anonymous" + str(self.getAnonID(url))
        else:
            return "Anonymous"

    #-------------------------------------------------------------------------------------------------------------------
    # Gets profilepage for this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getProfilePage(self):
        return ProfilePage.objects.get(person=self)

    #-------------------------------------------------------------------------------------------------------------------
    # Gets profile image for this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getProfileImage(self):
        from modernpolitics.backend import getDefaultImage
        if self.basicinfo.profile_image:
            return self.basicinfo.profile_image
        else:
            return getDefaultImage()

    #-------------------------------------------------------------------------------------------------------------------
    # Fills in fields based on facebook data
    #-------------------------------------------------------------------------------------------------------------------
    def refreshFB(self, fb_data):
        self.facebook_id = fb_data['id']
        self.facebook_profile_url = fb_data['link']
        # self.gender = fb_data['gender']
        self.confirmed = True

        if 'education' in fb_data:
            education = fb_data['education']
            for edu in education:
                school = edu['school']
                name = school['name']
                alias = name.replace(" ","")
                alias = alias.replace(",","")
                alias = alias.replace(".","")
                alias = alias.lower()
                school_networks = Network.objects.filter(alias=alias,network_type='S')
                if not school_networks:
                    school_network = Network(alias=alias,title=name,network_type='S')
                    school_network.autoSave()
                    school_network.members.add(self)
                    self.networks.add(school_network)
                else:
                    school_networks[0].members.add(self)
                    self.networks.add(school_networks[0])


        if 'location' in fb_data:
            location = fb_data['location']
            name = location['name']
            alias = name.replace(" ","")
            alias = alias.replace(",","")
            alias = alias.replace(".","")
            alias = alias.lower()
            location_networks = Network.objects.filter(alias=alias,network_type='L')
            if not location_networks:
                location_network = Network(alias=alias,title=name,network_type='L')
                location_network.autoSave()
                location_network.members.add(self)
                self.networks.add(location_network)
            else:
                location_networks[0].members.add(self)
                self.networks.add(location_networks[0])


        self.setUsername(fb_data['email'])

    #-------------------------------------------------------------------------------------------------------------------
    # Gets worldview for user.
    #-------------------------------------------------------------------------------------------------------------------
    def getView(self):
        if self.view_id != -1:
            return WorldView.objects.get(id=self.view_id)
        else: return None

    #-------------------------------------------------------------------------------------------------------------------
    # Sets username and email for userprofile and controllinguser
    #-------------------------------------------------------------------------------------------------------------------
    def setUsername(self, email):
        self.email = email
        self.username = email
        self.save()
        c = self.user
        c.email = email
        c.username = email
        c.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Get email extension from users email.
    #-------------------------------------------------------------------------------------------------------------------
    def getEmailExtension(self):
        splitted = self.email.split("@")
        if len(splitted)==2:
            return splitted[1]
        else:
            return "none"

    #-------------------------------------------------------------------------------------------------------------------
    # Gets network for user.
    #-------------------------------------------------------------------------------------------------------------------
    def getNetwork(self):
        from modernpolitics.backend import getOtherNetwork
        if len( self.networks.all() ) != 0:
            return self.networks.all()[0]
        else: return getOtherNetwork()


    #-------------------------------------------------------------------------------------------------------------------
    # Makes this UserProfile friends with another UserProfile (two-way following relationship)
    #-------------------------------------------------------------------------------------------------------------------
    def follow( self , to_user , fb=False ):
        relationship = UserFollow.lg.get_or_none( user=self, to_user=to_user )

        if not self.i_follow:
            self.createIFollowGroup()
        self.i_follow.members.add(to_user)

        if not to_user.follow_me:
            to_user.createFollowMeGroup()
        to_user.follow_me.members.add(self)

        #Check and Make Relationship A
        if not relationship:
            relationship = UserFollow( user=self , to_user=to_user , confirmed=True, fb=fb )
            relationship.autoSave()
        else:
            relationship.confirmed = True
            if fb: #Add fb value to relationship if fb is true
                relationship.fb = True
            relationship.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Breaks connections between this UserProfile and another UserProfile (two-way following relationship)
    #-------------------------------------------------------------------------------------------------------------------
    def unfollow( self , to_user ):
        relationship = UserFollow.lg.get_or_none( user=self, to_user=to_user )
        if self.i_follow:
            self.i_follow.members.remove(to_user)
        if to_user.follow_me:
            to_user.follow_me.members.remove(self)
        # Clear UserFollow
        if relationship:
            relationship.clear()

    #-------------------------------------------------------------------------------------------------------------------
    # Sets image to inputted file.
    #-------------------------------------------------------------------------------------------------------------------
    def setProfileImage(self, file):
        """
        Sets a user's profile image.  The most common inputs to this method will be:

            file(path_to_file) - use file from server
            ContentFile(request.FILES['input_from_user'].read()) - user uploaded image.

        Make sure to validate an image is an image before saving it to disk!  How does one do that you ask?

             try:
                file_content = ContentFile(request.FILES['input_from_user'].read())
                Image.open(file_content)
                <do valid response>
            except IOError:
                <do invalid response>

        @param file: The input file
        @type file: file
        """
        title =  self.get_name() + ' Image'
        summary = "This is me."
        image = self.basicinfo.profile_image
        if image:
            image.createImage(File(file))
        else:
            img = UserImage(title=title, summary=summary)
            img.createImage(File(file))
            img.autoSave(creator=self, privacy='PUB')
            self.basicinfo.profile_image = img
            self.basicinfo.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Creates involvement tuple and adds it to myinvolvement if user is not already involved with inputted content
    # otherwise just increases amount of invovlement in tupble.
    #-------------------------------------------------------------------------------------------------------------------
    def updateInvolvement(self, content, amount):
        c = self.my_involvement.filter(content=content)
        # if already involved with content, increase your involvement
        if c:
            c[0].involvement += amount
            c[0].when = datetime.datetime.now()
            c[0].save()
        # else create new involved and add to myinvolvement
        else:
            i = Involved(content=content, involvement=amount)
            i.save()
            self.my_involvement.add(i)

    #-------------------------------------------------------------------------------------------------------------------
    # Send email to user alerting them of notificaiton... depending on their settings.
    #-------------------------------------------------------------------------------------------------------------------
    def emailNotification(self, notification):
        pass
        #send_mail(subject='Notification', message=notification.getEmail(),
        # from_email='info@lovegov.com', recipient_list=[self.email])

    #-------------------------------------------------------------------------------------------------------------------
    # If user has settings to get notified for inputted notification, saves notification and returns True
    # otherwise, does nothing and returns false
    #-------------------------------------------------------------------------------------------------------------------
    def notify(self, action, content=None, user=None):
        relationship = action.relationship
        if action.type != 'FO' and action.type != 'JO':
            if relationship.getFrom().id == self.id and self.id == relationship.getTo().creator.id:
                return False

        if action.type in AGGREGATE_NOTIFY_TYPES:
            stale_date = datetime.datetime.today() - STALE_TIME_DELTA
            already = Notification.objects.filter(notify_user=self,
                                                    when__gte=stale_date,
                                                    action__modifier=action.modifier,
                                                    action__type=action.type ).order_by('when').reverse()
            for notification in already:
                if notification.action.relationship.getTo().id == relationship.getTo().id:
                    notification.when = datetime.datetime.today()
                    if notification.tally == 0:
                        notification.addAggUser( notification.action.relationship.user )
                    notification.addAggUser( relationship.user )
                    return True
            notification = Notification(action=action, notify_user=self)
            notification.autoSave()
            notification.addAggUser( relationship.user )

        elif action.type in NOTIFY_TYPES:
            notification = Notification(action=action, notify_user=self)
            notification.autoSave()
            return True

        else:
            return False

    #-------------------------------------------------------------------------------------------------------------------
    # Add debate result, takes in debate and result (as integer)
    #-------------------------------------------------------------------------------------------------------------------
    def addDebateResult(self, debate, result):
        debate_result = DebateResult(debate=debate.id, result=result)
        debate_result.save()
        self.debate_record.add(debate_result)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns triple tuple (wins, losses, ties)
    #-------------------------------------------------------------------------------------------------------------------
    def getDebateRecord(self):
        wins = self.debate_record.filter(result=1).count()
        losses = self.debate_record.filter(result=-1).count()
        ties = self.debate_record.filter(result=0).count()
        return wins, losses, ties

    #-------------------------------------------------------------------------------------------------------------------
    # Creates system group for that persons connections.
    #-------------------------------------------------------------------------------------------------------------------
    def createIFollowGroup(self):
        title = "Group who " + self.get_name() + " follows."
        group = Group(title=title, full_text="Group of people who "+self.get_name()+" is following.", group_privacy='S', system=True, in_search=False, in_calc=False)
        group.autoSave()
        self.i_follow = group
        self.save()
        return group

    #-------------------------------------------------------------------------------------------------------------------
    # Creates system group for that persons connections.
    #-------------------------------------------------------------------------------------------------------------------
    def createFollowMeGroup(self):
        title = "Group who follows "  + self.get_name()
        group = Group(title=title, full_text="Group of people who are following "+self.get_name(), group_privacy='S', system=True, in_search=False, in_calc=False)
        group.autoSave()
        self.follow_me = group
        self.save()
        return group

    #-------------------------------------------------------------------------------------------------------------------
    # Adds user to lovegov group.
    #-------------------------------------------------------------------------------------------------------------------
    def joinLoveGovGroup(self):
        from modernpolitics.backend import getLoveGovGroup
        lovegov = getLoveGovGroup()
        lovegov.members.add(self)

    #-------------------------------------------------------------------------------------------------------------------
    # Clears m2m and deletes tuples
    #-------------------------------------------------------------------------------------------------------------------
    def smartClearMyFeed(self):
        self.my_feed.all().delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all notifications.
    #-------------------------------------------------------------------------------------------------------------------
    def getNotifications(self, start=0, num=-1, new=False):
        if new:
            notifications = Notification.objects.filter(notify_user=self, viewed=False).order_by('when').reverse()
        else:
            notifications = Notification.objects.filter(notify_user=self).order_by('when').reverse()
        if num != -1:
            notifications = notifications[start:start+num]
        return notifications

    def getNumNewNotifications(self):
        return len( Notification.objects.filter(notify_user=self, viewed=False) )

    def getAllNotifications(self):
        return Notification.objects.filter(notify_user=self).order_by('when').reverse()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a users recent activity.
    #-------------------------------------------------------------------------------------------------------------------
    def getActivity(self, start=0, num=-1):
        actions = Action.objects.filter(relationship__user=self, relationship__privacy='PUB').order_by('when').reverse()
        print len( actions )
        if num != 1:
            actions = actions[start:start+num]
        print len( actions )
        return actions

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowRequests(self, num=-1):
        if num == -1:
            return UserFollow.objects.filter( to_user=self, confirmed=False, requested=True, rejected=False ).order_by('when').reverse()
        else:
            return UserFollow.objects.filter( to_user=self, confirmed=False, requested=True, rejected=False ).order_by('when').reverse()[:num]

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getGroupInvites(self, num=-1):
        if num == -1:
            return GroupJoined.objects.filter( user=self, confirmed=False, invited=True, rejected=False ).order_by('when').reverse()
        else:
            return GroupJoined.objects.filter( user=self, confirmed=False, invited=True, rejected=False ).order_by('when').reverse()[:num]

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Groups this user has joined and been accepted to.
    #-------------------------------------------------------------------------------------------------------------------
    def getGroups(self, num=-1):
        group_joins = GroupJoined.objects.filter( user=self, confirmed=True )
        groups = []
        if num == -1:
            for g in group_joins:
                groups.append(g.group)
        else:
            i = 0
            while i < len(follows) and i < num:
                groups.append(group_joins[i].group)
        return groups

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Users who are (confirmed) following this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowMe(self, num=-1):
        follows = UserFollow.objects.filter( to_user=self, confirmed=True )
        followers = []
        if num == -1:
            for f in follows:
                followers.append(f.user)
        else:
            i = 0
            while i < len(follows) and i < num:
                followers.append(follows[i].user)
        return followers

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Users who this user is (confirmed) following.
    #-------------------------------------------------------------------------------------------------------------------
    def getIFollow(self, num=-1):
        follows = UserFollow.objects.filter( user=self, confirmed=True )
        following = []
        if num == -1:
            for f in follows:
                following.append(f.to_user)
        else:
            i = 0
            while i < len(follows) and i < num:
                following.append(f.to_user)
        return following

    #-------------------------------------------------------------------------------------------------------------------
    # Returns query set of all UserFollow who are (confirmed) following this user and are fb friends with this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getFBFriends(self):
        follows = UserFollow.objects.filter(user=self, confirmed=True, fb=True)
        friends = []
        for f in follows:
            friends.append(f.to_user)
        return friends

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all UserFollow who are (confirmed) following this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getUserFollowMe(self):
        followers = UserFollow.objects.filter( to_user=self, confirmed=True )
        return followers

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all UserFollow who are (confirmed) following this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getIUserFollow(self):
        following = UserFollow.objects.filter( user=self, confirmed=True )
        return following

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a set of random questions that the user hasn't answered
    #-------------------------------------------------------------------------------------------------------------------
    def getQuestions(self):
        responses = self.getView().responses
        answered_ids = responses.values_list('question__id', flat=True)
        unanswered = Question.objects.exclude(id__in=answered_ids)
        unanswered_ids = unanswered.values_list('id', flat=True)
        sample_size = min(NUM_QUESTIONS, len(unanswered_ids))
        questions_ids = random.sample(unanswered_ids, sample_size)
        questions = unanswered.filter(id__in=questions_ids)
        return questions

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if this is the first time the user has logged in.
    #-------------------------------------------------------------------------------------------------------------------
    def checkFirstLogin(self):
        if self.first_login:
            self.first_login = False
            self.save()
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------------------------------
    # Gets the users responses to questions in a list of  (question, response) tuples
    #-----------------------------------------------------------------------------------------------------------------------
    def getUserResponses(self):
        qr = []
        responses = self.getView().responses
        questions = Question.objects.all()
        for q in questions:
            r = responses.filter(question=q)
            qr.append((q,r))
        return qr

    def setAddress(self, newAddress):
        self.userAddress.currentAddress = False
        self.userAddress.save()
        newAddress.currentAddress = True
        self.userAddress = newAddress
        self.save()

#=======================================================================================================================
# Permissions for user to modify shit.. right now just char Field, but could be expanded later
#=======================================================================================================================
class UserPermission(LGModel):
    permission_type = models.CharField(max_length=1, choices=PERMISSION_CHOICES)

#=======================================================================================================================
# Inherits from user,
#=======================================================================================================================
class ControllingUser(User, LGModel):
    permissions = models.ForeignKey(UserPermission, null=True)  # null is default permission
    user_profile = models.ForeignKey(UserProfile, null=True)    # spectator
    objects = UserManager()
    def getUserProfile(self):
        return self.user_profile

#=======================================================================================================================
# Keeps track of user activity.
#=======================================================================================================================
class Action(Privacy):
    type = models.CharField(max_length=2, choices=RELATIONSHIP_CHOICES)
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS, default='D')
    when = models.DateTimeField(auto_now_add=True)
    relationship = models.ForeignKey("Relationship", null=True)
    must_notify = models.BooleanField(default=False)        # to override check for permission to notify
    # optimization
    verbose = models.TextField()  # Don't use me!  I'm deprecated

    def getRelationship(self):
        if self.relationship_id == -1:
            return None
        else:
            return Relationship.objects.get(id=self.relationship_id)

    def autoSave(self):
        relationship = self.relationship
        self.type = relationship.relationship_type
        self.save()

    def getVerbose(self,view_user=None):
        #Check for relationship
        relationship = self.relationship
        #Set default local variables
        action_verbose = ' no action '
        from_you = False
        to_you = False
        #Set to and from users
        to_user = relationship.getTo()
        from_user = relationship.getFrom()
        #check to see if the viewing user is the to or from user
        if view_user and from_user.id == view_user.id:
            from_you = True
        elif view_user and to_user.id == view_user.id:
            to_you = True

        action_context = {'to_user':to_user,
                            'to_you':to_you,
                            'from_user':from_user,
                            'from_you':from_you,
                            'type':self.type,
                            'modifier':self.modifier,
                            'true':True}
        if self.type == 'FO' or self.type == 'JO':
            action_context['follow'] = relationship.downcast()
            reverse_follow = UserFollow.lg.get_or_none(user=to_user,to_user=from_user)
            if reverse_follow:
                action_context['reverse_follow'] = reverse_follow

        action_verbose = render_to_string('deployment/snippets/action_verbose.html',action_context)
        return action_verbose


#=======================================================================================================================
# Notifying a user of something important to them. privacy is in case they ought not be able to see who
#=======================================================================================================================
class Notification(Privacy):
    verbose = models.TextField()
    notify_user = models.ForeignKey(UserProfile, related_name = "notifywho")
    when = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
    action = models.ForeignKey(Action, null=True)
    # for aggregating notifications like facebook
    tally = models.IntegerField(default=0)
    users = models.ManyToManyField(UserProfile, related_name = "notifyagg")
    recent_user = models.ForeignKey(UserProfile, null=True, related_name = "mostrecentuser")
    # for custom notification, who or what triggered this notification.. if both null it was not triggered via following
    trig_content = models.ForeignKey(Content, null=True, related_name = "trigcontent")
    trig_user = models.ForeignKey(UserProfile, null=True, related_name="griguser")
    # deprecated
    type = models.CharField(max_length=2, choices=RELATIONSHIP_CHOICES)
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS, default='D')

    def getVerbose(self,view_user):
        n_action = self.action
        relationship = n_action.relationship
        #Set default local variables
        from_you = False
        to_you = False
        #Set to and from users
        to_user = relationship.getTo()
        from_user = relationship.getFrom()
        if n_action.type in AGGREGATE_NOTIFY_TYPES and self.tally > 0:
            from_user = self.recent_user
        #check to see if the viewing user is the to or from user
        if from_user.id == view_user.id:
            from_you = True
        elif to_user.id == view_user.id:
            to_you = True

        viewed = True
        if not self.viewed:
            viewed = False
            self.viewed = True
            self.save()

        notification_context = {'to_user':to_user,
                          'to_you':to_you,
                          'from_user':from_user,
                          'from_you':from_you,
                          'type':n_action.type,
                          'modifier':n_action.modifier,
                          'tally':self.tally,
                          'true':True,
                          'viewed':viewed}
        if n_action.type == 'FO':
            notification_context['follow'] = relationship.downcast()
            reverse_follow = UserFollow.lg.get_or_none(user=to_user,to_user=from_user)
            if reverse_follow:
                notification_context['reverse_follow'] = reverse_follow
        if n_action.type == 'JO':
            notification_context['group_join'] = relationship.downcast()

        notification_verbose = render_to_string('deployment/snippets/notification_verbose.html',notification_context)
        return notification_verbose

    def addAggUser(self,agg_user):
        already = self.users.filter(alias=agg_user.alias)
        if not already:
            self.users.add(agg_user)
            self.tally += 1
        self.recent_user = agg_user
        self.viewed = False
        self.save()

    def autoSave(self):
        self.save()

    def getEmail(self):
        return "notification email message based on notification"

########################################################################################################################
############ POLITICAL_ROLE ############################################################################################

class ElectedOfficial(UserProfile):
    # ENUMS
    TITLE_CHOICES = ( ('S','Sen.'), ('R','Rep.'), ('M', 'Sel.') )
    # Name/Title
    title = models.CharField(max_length=1, choices=TITLE_CHOICES, null=True)
    official_name = models.CharField(max_length=200,null=True)
    # ID Numbers
    govtrack_id = models.IntegerField(null=True)
    pvs_id = models.IntegerField(null=True)
    os_id = models.CharField(max_length=50, null=True)
    bioguide_id = models.CharField(max_length=50, null=True)
    metavid_id = models.CharField(max_length=150, null=True)
    youtube_id = models.CharField(max_length=150, null=True)
    twitter_id = models.CharField(max_length=150, null=True)
    # Term Data
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def autoSave(self, personXML):
        """
        This method parses an individual person object from the  XML from people.xml from GovTrack

        @param personXML:
        @return:
        """
        def parseDate(date):
            splitDate = str(date).split('-')
            return datetime.date(year=int(splitDate[0]), month=int(splitDate[1]), day=int(splitDate[2]))
            #representative.username = person['id']
        self.govtrack_id = personXML['id']
        if personXML.has_key('middlename'):
            self.basicinfo.middle_name = personXML['middlename']
        if personXML.has_key('nickname'):
            self.basicinfo.nick_name = personXML['nickname']
        if personXML.has_key('birthday'):
            self.basicinfo.dob = parseDate(personXML['birthday'])
        if personXML.has_key('gender'):
            self.basicinfo.gender = personXML['gender']
        if personXML.has_key('religion'):
            self.basicinfo.religion = personXML['religion']
        if personXML.has_key('pvsid'):
            self.pvs_id = personXML['pvsid']
        if personXML.has_key('osid'):
            self.os_id = personXML['osid']
        if personXML.has_key('bioguideid'):
            self.bioguide_id = personXML['bioguideid']
        if personXML.has_key('metavidid'):
            self.metavid_id = personXML['metavidid']
        if personXML.has_key('youtubeid'):
            self.youtube_id = personXML['youtubeid']
        if personXML.has_key('twitterid'):
            self.twitter_id = personXML['twitterid']
        if personXML.has_key('facebookgraphid'):
            self.facebook_id = personXML['facebookgraphid']
        self.start_date = parseDate(personXML.role['startdate'])
        self.end_date = parseDate(personXML.role['enddate'])
        self.basicinfo.party = personXML.role['party']
        self.basicinfo.political_role = 'E'
        # representative.basicinfo.url = list(person.role['url'])
        self.confirmed = True
        self.save()
        self.basicinfo.save()

class Politician(UserProfile):
    party = models.CharField(max_length=100)
    office_seeking = models.CharField(max_length=100)

########################################################################################################################
################################################# Representatives ######################################################
class CongressSessions(LGModel):
    session = models.IntegerField(primary_key=True)
    people = models.ManyToManyField(ElectedOfficial)

    def getReps(self):
        return self.people.filter(title="R")

    def getRepByStateDistrict(self,state,district):
        representatives = self.people.filter(title="R")
        representatives = Representative.objects.filter(representatives)
        return representatives.filter(state=state,district=district)[0]

    def getSenators(self):
        return self.people.filter(title="S")

    def getSenatorByState(self,state):
        return self.people.filter(title="S").get(state=state)

class SelectMan(ElectedOfficial):
    represents = models.CharField(max_length=500)

class Senator(ElectedOfficial):
    state = models.CharField(max_length=2,null=True)
    classNum = models.IntegerField(null=True)

    def autoSave(self, personXML):
        self.title = 'S'
        self.state = personXML.role['state']
        self.classNum = personXML.role['class']
        super(Senator,self).autoSave(personXML)

class Representative(ElectedOfficial):
    state = models.CharField(max_length=2,null=True)
    district = models.IntegerField(null=True)

    def autoSave(self, personXML):
        self.title = 'R'
        self.state = personXML.role['state']
        self.district = personXML.role['district']
        super(Representative,self).autoSave(personXML)



class USPresident(ElectedOfficial):
    pass


# External Imports
class Committee(LGModel):
    COMMITTEE_CHOICES = ( ('S','Senate'), ('H','House'), ('SS', 'Senate Subcommittee'), ('HS','House Subcommittee'), ("O","Other") )
    name = models.CharField(max_length=1000)
    code = models.CharField(max_length=20)
    type = models.CharField(max_length=2, choices=COMMITTEE_CHOICES)
    parent = models.ForeignKey('self', null=True)
    members = models.ManyToManyField(ElectedOfficial, through='CommitteeMember')

    def saveXML(self,committeeXML,session):
        type = committeeXML['type']
        if type == "house": type="H"
        else: type="S"
        self.type = type
        self.name = committeeXML['displayname'].encode("utf-8",'ignore')
        print committeeXML['displayname'].encode("utf-8",'ignore')
        self.code = committeeXML['code']
        self.save()
        for memberXML in committeeXML.findChildren('member',recursive=False):
            committeeMember = CommitteeMember()
            if memberXML.has_key('role'): committeeMember.role = memberXML['role']
            committeeMember.electedOfficial = ElectedOfficial.objects.get(govtrack_id=int(memberXML['id']))
            committeeMember.committee = self
            committeeMember.session =  CongressSessions.objects.get(session=session)
            committeeMember.save()
        for subcommitteeXML in committeeXML.findChildren('subcommittee',recursive=False):
            committee = Committee()
            committee.name = subcommitteeXML['displayname'].rstrip()
            print subcommitteeXML['displayname'].encode("utf-8",'ignore')
            committee.type = type
            committee.parent = self
            committee.code = subcommitteeXML['code']
            committee.save()
            for submemberXML in subcommitteeXML.findChildren('member'):
                committeeMember = CommitteeMember()
                if submemberXML.has_key('role'): committeeMember.role = submemberXML['role']
                committeeMember.electedOfficial = ElectedOfficial.objects.get(govtrack_id=int(submemberXML['id']))
                committeeMember.committee = committee
                committeeMember.session = CongressSessions.objects.get(session=session)
                committeeMember.save()

class CommitteeMember(LGModel):
    role = models.CharField(max_length=200,null=True)
    session = models.ForeignKey(CongressSessions)
    electedOfficial = models.ForeignKey(ElectedOfficial)
    committee = models.ForeignKey(Committee)


########################################################################################################################
########################################################################################################################
#
# Basic Content
#
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# Petition
#
#=======================================================================================================================
class Petition(Content):
    full_text = models.TextField(max_length=10000)
    signers = models.ManyToManyField(UserProfile, related_name = 'petitions')
    finalized = models.BooleanField(default=False)
    def autoSave(self, creator=None, privacy='PUB'):
        if not self.summary:
            self.summary = self.full_text[:400]
        self.type = 'P'
        self.in_feed = True
        self.save()
        super(Petition, self).autoSave(creator=creator, privacy=privacy)

    #-------------------------------------------------------------------------------------------------------------------
    # Adds inputted user to signer list, if the petition is finalized.
    #-------------------------------------------------------------------------------------------------------------------
    def sign(self, user):
        if self.finalized:
            if user in self.signers.all():
                return False
            else:
                self.signers.add(user)
                return True

    def finalize(self):
        self.finalized = True
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Edit method, the petition-specific version of the general content method.
    #-------------------------------------------------------------------------------------------------------------------
    def edit(self,field,value):
        if field=="full_text":
            self.full_text=value
        else:
            super(Petition, self).edit(field,value)
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns all signers.
    #-------------------------------------------------------------------------------------------------------------------
    def getSigners(self):
        return self.signers.all()
    def numSigners(self):
        return self.signers.count()

#=======================================================================================================================
# Event
#
#=======================================================================================================================
class Event(Content):
    # we can get attendees by user relationship, yes_set, maybe_set, no_set
    full_text = models.TextField(max_length=10000)
    datetime_of_event = models.DateTimeField()
    def autoSave(self, creator=None, privacy='PUB'):
        self.type = 'E'
        self.save()
        super(Event, self).autoSave(creator=creator, privacy=privacy)


    def edit(self,field,value):
        if field=="full_text":
            self.full_text=value
        else:
            super(Event, self).edit(field,value)
        self.save()


#=======================================================================================================================
# News
#
#=======================================================================================================================
class News(Content):
    link = models.URLField()
    link_summary = models.TextField(default="")
    link_screenshot = models.ImageField(upload_to='screenshots/')
    def autoSave(self, creator=None, privacy='PUB'):
        self.type = 'N'
        self.in_feed = True
        self.save()
        super(News, self).autoSave(creator=creator, privacy=privacy)

    def getAbsoluteLink(self):
        link = str.replace(str(self.link), 'http://', '')
        return "http://" + link

    def getImage(self):
        return self.link_screenshot

    # takes in a lovegov.com url and saves image file from that location
    def saveScreenShot(self, ref):
        from lovegov.modernpolitics.helpers import photoKey
        relativePath = ref.replace(settings.MEDIA_URL, settings.MEDIA_ROOT, 1)
        file = open(relativePath)
        self.link_screenshot.save(photoKey(".png"), File(file))
        self.save()

#=======================================================================================================================
# UserPost (self post of text...aka a rant)
#
#=======================================================================================================================
class UserPost(Content):
    full_text = models.TextField(max_length=10000)

#=======================================================================================================================
# Photo album
#
#=======================================================================================================================
class PhotoAlbum(Content):
    photos = models.ManyToManyField(UserImage)


#=======================================================================================================================
# Comment (the building block of forums)
#
#=======================================================================================================================
class Comment(Content):

    root_content = models.ForeignKey(Content, related_name='root_content')
    on_content = models.ForeignKey(Content, related_name='comments')
    text = models.TextField(max_length = 1000)
    creator_name = models.CharField(max_length=50)

    def autoSave(self, creator=None, privacy='PUB'):
        from modernpolitics.backend import getLoveGovUser
        if not creator:
            creator = getLoveGovUser()
            # creator name optimization
        if privacy=='PUB':
            self.creator_name = creator.get_name()
        elif privacy=='FOL':
            self.creator_name = 'Someone'
        elif privacy=='PRI':
            self.creator_name = 'Anonymous'
        # set root content
        if self.on_content.type == 'C':
            self.root_content = self.on_content.downcast().root_content
        else:
            self.root_content = self.on_content
        self.title = str(self.creator_name + "'s comment on " + self.root_content.title)
        self.type = 'C'
        self.summary = self.text
        self.in_feed = False
        self.save()
        super(Comment, self).autoSave(creator=creator, privacy=privacy)
        # add parent topics
        self.setMainTopic(self.root_content.main_topic)

    def getAlphaDisplayName(self):
        if self.privacy=='PUB':
            return self.getCreator().get_name()
        elif self.privacy=='PRI':
            return 'Anonymous'
        else:
            return 'Someone'

    def getRootContent(self):
        return self.root_content

#=======================================================================================================================
# Forum, for grouping comment threads and organizing into parents and children.
#
#=======================================================================================================================
class Forum(Content):
    children = models.ManyToManyField(Content, related_name="children")
    parent = models.ForeignKey(Content, null=True, related_name="parent")
    def autoSave(self, creator=None, privacy='PUB'):
        self.type = 'F'
        self.save()
        super(Forum, self).autoSave(creator=creator, privacy=privacy)


########################################################################################################################
########################################################################################################################
#
# Legislation Models
#
########################################################################################################################
########################################################################################################################
#-----------------------------------------------------------------------------------------------------------------------
# parseDateTime
#   This method parses a string into a datetime object.  If the string doesn't contain time, time is set to 00:00:00
#   @example "2012-01-06T06:10:26"
#   @arg    dateTime    string of datetime
#   @return datetime.datetime
#-----------------------------------------------------------------------------------------------------------------------
def parseDateTime(dateTime):
    if 'T' in str(dateTime):
        splitDateTime = str(dateTime).split('T')
        splitDate = str(splitDateTime[0]).split('-')
        splitTime = str(splitDateTime[1]).split('-')
        splitTime = str(splitTime[0]).split(':')
        return datetime.datetime(year=int(splitDate[0]), month=int(splitDate[1]), day=int(splitDate[2]), hour=int(splitTime[0]), minute=int(splitTime[1]), second=int(splitTime[2]))
    else:
        splitDate = str(dateTime).split('-')
        return datetime.datetime(year=int(splitDate[0]), month=int(splitDate[1]), day=int(splitDate[2]), hour=0, minute=0, second=0)

#-----------------------------------------------------------------------------------------------------------------------
# parseDate
#   This method parses a string into a date object.
#   @example "2012-01-03"
#   @arg    date   string of date
#   @return datetime.date
#-----------------------------------------------------------------------------------------------------------------------
def parseDate(date):
    splitDate = str(date).split('-')
    return datetime.date(year=int(splitDate[0]), month=int(splitDate[1]), day=int(splitDate[2]))


#=======================================================================================================================
#
# LegislationStatus
#
#=======================================================================================================================
class LegislationStatus(LGModel):
    STATUS_CHOICES = ( ('I','Introduced'), ('C','Calendar'), ('V', 'Vote'), ('E','Enacted'), ('T','ToPresident') )
    status_text = models.CharField(max_length=1, choices=STATUS_CHOICES)
    datetime = models.DateTimeField(null=True)
    where = models.CharField(max_length=4, null=True)
    result = models.CharField(max_length=20, null=True)
    how = models.CharField(max_length=20, null=True)
    roll = models.IntegerField(null=True)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    parsedXML   a legislation XML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, parsedXML):
        if parsedXML.status.introduced:
            self.status_text = 'I'
            self.datetime = parseDateTime(parsedXML.status.introduced['datetime'])
        elif parsedXML.status.calendar:
            self.status_text = 'C'
            self.datetime = parseDateTime(parsedXML.status.calendar['datetime'])
        elif parsedXML.status.vote:
            self.status_text = 'V'
            self.datetime = parseDateTime(parsedXML.status.vote['datetime'])
            self.where = parsedXML.status.vote['where']
            self.result = parsedXML.status.vote['result']
            self.how = parsedXML.status.vote['how']
            if parsedXML.status.vote.has_key("roll") and parsedXML.status.vote['roll'] != '':
                self.roll = int(parsedXML.status.vote['roll'])
        elif parsedXML.status.vote2:
            self.status_text = 'V'
            self.datetime = parseDateTime(parsedXML.status.vote2['datetime'])
            self.where = parsedXML.status.vote2['where']
            self.result = parsedXML.status.vote2['result']
            self.how = parsedXML.status.vote2['how']
            if parsedXML.status.vote2.has_key("roll") and parsedXML.status.vote2['roll'] != '':
                self.roll = int(parsedXML.status.vote2['roll'])
        elif parsedXML.status.enacted:
            self.status_text = 'E'
            self.datetime = parseDateTime(parsedXML.status.enacted['datetime'])
        elif parsedXML.status.topresident:
            self.status_text = 'T'
            self.datetime = parseDateTime(parsedXML.status.topresident['datetime'])
        self.save()


#=======================================================================================================================
#
# LegislationSubjects
#
#=======================================================================================================================
class LegislationSubjects(LGModel):
    term_name = models.CharField(max_length=300)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    termXML         the XML for terms from parsedXML from govtrack.us
    #   @arg    legislation     the legislation to attach the terms to
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, termXML, legislation):
        term_name = termXML['name']
        if not LegislationSubjects.objects.filter(term_name=term_name):
            newSubject = LegislationSubjects(term_name=term_name)
            newSubject.save()
        legislation.subjects.add(LegislationSubjects.objects.get(term_name=term_name))


#=======================================================================================================================
#
# Legislation
#
#=======================================================================================================================
class Legislation(Content):
    # identifying fields
    bill_session = models.IntegerField(null=True)
    bill_type = models.CharField(max_length=2)
    bill_number = models.IntegerField()
    # descriptive fields
    bill_updated = models.DateTimeField()
    state_datetime = models.DateField()
    state_text = models.CharField(max_length=500)
    bill_status = models.OneToOneField(LegislationStatus)
    introduced_datetime = models.DateField()
    sponsor = models.ForeignKey(ElectedOfficial, related_name="sponsor_id",null=True)
    cosponsors = models.ManyToManyField(ElectedOfficial, through='LegislationCosponsor')
    committees = models.ManyToManyField(Committee, through="LegislationCommittee",null=True)
    bill_relation = models.ManyToManyField('self', null=True, symmetrical=False)
    subjects = models.ManyToManyField(LegislationSubjects)
    bill_summary = models.TextField(null=True)

    #-------------------------------------------------------------------------------------------------------------------
    # setAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    parsedXML   the XML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, parsedXML):
        if parsedXML.bill and parsedXML.bill.has_key('session'):
            self.bill_session = int(parsedXML.bill['session'])
        self.bill_type = parsedXML.bill['type']
        self.bill_number = int(parsedXML.bill['number'])
        self.bill_updated = parseDateTime(parsedXML.bill['updated'])
        self.state_datetime = parseDateTime(parsedXML.state['datetime'])
        self.state_text = parsedXML.state.contents[0]
        self.introduced_datetime = parseDate(parsedXML.introduced['datetime'])
        if parsedXML.sponsor.has_key('id'):
            self.sponsor = ElectedOfficial.objects.get(govtrack_id=int(parsedXML.sponsor['id']))
        self.bill_summary = parsedXML.summary.contents[0]
        # new LegislationStatus, set and save Attributes from parsed XML
        newLegislationStatus = LegislationStatus()
        newLegislationStatus.setSaveAttributes(parsedXML=parsedXML)
        self.bill_status = newLegislationStatus
        self.save()
        # Parses all tags for all relevant information
        for title in parsedXML.findAll('title'):
            newLegislationTitle = LegislationTitle()
            newLegislationTitle.setSaveAttributes(titleXML=title, legislation=self)
        for cosponsor in parsedXML.findAll('cosponsor'):
            legislationCosponsor = LegislationCosponsor()
            legislationCosponsor.setSaveAttributes(cosponsorXML=cosponsor, legislation=self)
        for action in parsedXML.findAll('action'):
            newLegislationAction = LegislationAction()
            newLegislationAction.setSaveAttributes(actionXML=action, legislation=self)
            newLegislationAction.setSaveReferences(actionXML=action)
        for calendar in parsedXML.actions.findAll('calendar'):
            newLegislationCalendar = LegislationCalendar()
            newLegislationCalendar.setSaveAttributes(calendarXML=calendar, legislation=self)
            newLegislationCalendar.setSaveReferences(actionXML=calendar)
        for vote in parsedXML.actions.findAll('vote'):
            newLegislationVote = LegislationVote()
            newLegislationVote.setSaveAttributes(voteXML=vote, legislation=self)
            newLegislationVote.setSaveReferences(actionXML=vote)
        for toPresident in parsedXML.actions.findAll('topresident'):
            newLegislationToPresident = LegislationToPresident()
            newLegislationToPresident.setSaveAttributes(toPresidentXML=toPresident, legislation=self)
            newLegislationToPresident.setSaveReferences(actionXML=toPresident)
        for signed in parsedXML.actions.findAll('signed'):
            newLegislationSigned = LegislationSigned()
            newLegislationSigned.setSaveAttributes(signedXML=signed, legislation=self)
            newLegislationSigned.setSaveReferences(actionXML=signed)
        for enacted in parsedXML.actions.findAll('enacted'):
            newLegislationEnacted = LegislationEnacted()
            newLegislationEnacted.setSaveAttributes(enactedXML=enacted, legislation=self)
            newLegislationEnacted.setSaveReferences(actionXML=enacted)
        for committee in parsedXML.committees.findAll('committee'):
            if committee.has_key('name') and committee['name'] != "":
                newLegislationCommittee = LegislationCommittee()
                newLegislationCommittee.setSaveAttributes(parsedXML=parsedXML, committeeXML=committee, legislation=self)
        for term in parsedXML.subjects.findAll('term'):
            newLegislationSubject = LegislationSubjects()
            newLegislationSubject.setSaveAttributes(termXML=term, legislation=self)


#=======================================================================================================================
#
# LegislationCosponsor
#
#=======================================================================================================================
class LegislationCosponsor(LGModel):
    legislation = models.ForeignKey(Legislation)
    elected_official = models.ForeignKey(ElectedOfficial)
    joined = models.DateField()

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    cosponsorXML   the XML from a cosponsor tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, cosponsorXML, legislation):
        self.legislation = legislation
        self.elected_official = ElectedOfficial.objects.get(govtrack_id=int(cosponsorXML['id']))
        self.joined = parseDate(cosponsorXML['joined'])
        self.save()


#=======================================================================================================================
#
# LegislationTitle
#
#=======================================================================================================================
class LegislationTitle(LGModel):
    bill = models.ForeignKey(Legislation)
    title = models.CharField(max_length=1000)
    title_type = models.CharField(max_length=50)
    title_as = models.CharField(max_length=200)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    titleXML   the XML from a title tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, titleXML, legislation):
        self.bill = legislation
        self.title = titleXML.contents[0]
        self.title_type = titleXML['type']
        self.title_as = titleXML['as']
        self.save()


#=======================================================================================================================
#
# LegislationAction
#
#=======================================================================================================================
class LegislationAction(LGModel):
    ACTION_CHOICES = ( ('A','Action'), ('C','Calendar'), ('V', 'Vote'),
                       ('E','Enacted'), ('S', 'Signed'), ('T', 'ToPresident') )
    bill = models.ForeignKey(Legislation)
    datetime = models.DateTimeField()
    refer_committee = models.ForeignKey(Committee, null=True)
    text = models.TextField(null=True)
    action_type = models.CharField(max_length=1, choices=ACTION_CHOICES)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    titleXML        the XML from a action tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, actionXML, legislation):
        self.bill = legislation
        self.datetime = parseDateTime(actionXML['datetime'])
        self.text = actionXML.text
        self.action_type = 'A'
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveReferences
    #   This method sets and saves references by extracting the information from parsedXML
    #   @arg    actionXML   the XML from an action tag from parsedXML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveReferences(self, actionXML):
        for reference in actionXML.findAll('reference'):
            newLegislationRefLabel = LegislationRefLabel()
            newLegislationRefLabel.action = self
            newLegislationRefLabel.label = reference['label']
            newLegislationRefLabel.ref = reference['ref']
            newLegislationRefLabel.save()


#=======================================================================================================================
#
# LegislationCalendar
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationCalendar(LegislationAction):
    calendar = models.CharField(max_length=100, null=True)
    calendar_number = models.IntegerField(null=True)
    under = models.CharField(max_length=100, null=True)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    calendarXML   the XML from a calendar tag from parsedXML from govtrack.us
    #   @arg    legislation   the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, calendarXML, legislation):
        self.bill = legislation
        self.datetime = parseDateTime(calendarXML['datetime'])
        self.text = calendarXML.text
        self.action_type = 'C'
        if calendarXML.has_key('number'):
            self.calendar_number = int(calendarXML['number'])
        if calendarXML.has_key('calendar'):
            self.calendar = calendarXML['calendar']
        if calendarXML.has_key('under'):
            self.under = calendarXML['under']
        self.save()


#=======================================================================================================================
#
# LegislationVote
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationVote(LegislationAction):
    how = models.CharField(max_length=150, null=True)
    vote_type = models.CharField(max_length=100, null=True)
    roll = models.IntegerField(null=True)
    where = models.CharField(max_length=4, null=True)
    result = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=100, null=True)
    suspension = models.CharField(max_length=50, null=True)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    calendarXML   the XML from a vote tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, voteXML, legislation):
        self.bill = legislation
        self.datetime = parseDateTime(voteXML['datetime'])
        self.text = voteXML.text
        self.action_type = 'V'
        if voteXML.has_key('how'):
            self.how = voteXML['how']
        if voteXML.has_key('type'):
            self.vote_type = voteXML['type']
        if voteXML.has_key('roll'):
            self.roll = int(voteXML['roll'])
        if voteXML.has_key('where'):
            self.where = voteXML['where']
        if voteXML.has_key('result'):
            self.result = voteXML['result']
        if voteXML.has_key('suspension'):
            self.suspension = int(voteXML['suspension'])
        if voteXML.has_key('state'):
            self.state = voteXML['state']
        self.save()

#=======================================================================================================================
#
# LegislationToPresident
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationToPresident(LegislationAction):

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    toPresidentXML   the XML from a topresident tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, toPresidentXML, legislation):
        super(LegislationToPresident, self).setSaveAttributes(toPresidentXML,legislation)
        self.action_type = 'T'
        self.save()


#=======================================================================================================================
#
# LegislationToSigned
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationSigned(LegislationAction):
    pass

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    signedXML   the XML from a signed tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, signedXML, legislation):
        super(LegislationSigned, self).setSaveAttributes(signedXML,legislation)
        self.action_type = 'S'
        self.save()


#=======================================================================================================================
#
# LegislationEnacted
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationEnacted(LegislationAction):
    number = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    enactedXML   the XML from a enacted tag from parsedXML from govtrack.us
    #   @arg    legislation     the legislation which contains this action
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, enactedXML, legislation):
        self.bill = legislation
        self.datetime = parseDateTime(enactedXML['datetime'])
        self.text = enactedXML.text
        if enactedXML.has_key('number'):
            self.number = enactedXML['number']
        if enactedXML.has_key('type'):
            self.type = enactedXML['type']
        if enactedXML.has_key('state'):
            self.state = enactedXML['state']
        self.action_type = 'E'
        self.save()


#=======================================================================================================================
#
# LegislationRefLabel
#
#=======================================================================================================================
class LegislationRefLabel(LGModel):
    action = models.ForeignKey(LegislationAction)
    label = models.CharField(max_length=1000)
    ref = models.CharField(max_length=1000)


#=======================================================================================================================
#
# LegislationCommittee
#
#=======================================================================================================================
class LegislationCommittee(LGModel):
    legislation = models.ForeignKey(Legislation)
    committee = models.ForeignKey(Committee, null=True)
    activity = models.CharField(max_length=250)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    parsedXML       the XML from govtrack.us
    #   @arg    legislation     the legislation which contains this committee
    #   @arg    committeeXML    the XML for a committee tag from parsedXML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, parsedXML, committeeXML, legislation):
        self.legislation = legislation
        self.activity = committeeXML['activity']
        if committeeXML.has_key('code') and not committeeXML.has_key('subcommittee') and committeeXML['code'] != "":
            if Committee.objects.filter(code=committeeXML['code']).exists():
                self.committee = Committee.objects.filter(code=committeeXML['code'])[0]
        elif committeeXML.has_key('subcommittee'):
            subcommittee_name = committeeXML['subcommittee'] + " Subcommittee"
            subcommittee_name = subcommittee_name.replace("Intellectual Property, Competition and the Internet","Intellectual Property, Competition, and the Internet")
            committee_name = committeeXML['name']
            if "House" in committee_name:
                if "Judiciary" in committee_name or "Budget" in committee_name:
                    committee_name = committee_name.replace("House ","House Committee on the ")
                else:
                    committee_name = committee_name.replace("House ","House Committee on ")
            elif "Senate" in committee_name:
                if "Judiciary" in committee_name or "Budget" in committee_name:
                    committee_name = committee_name.replace("Senate ","Senate Committee on the ")
                else:
                    committee_name = committee_name.replace("Senate ","Senate Committee on ")
            if Committee.objects.filter(name=committee_name).exists():
                parent_committee = Committee.objects.get(name=committee_name)
                if Committee.objects.filter(name=subcommittee_name, parent=parent_committee).exists():
                    self.committee = Committee.objects.get(name=subcommittee_name, parent=parent_committee)
        self.save()

#=======================================================================================================================
#
# LegislationAmendment
#
#=======================================================================================================================
class LegislationAmendment(LGModel):
    session = models.IntegerField()
    chamber = models.CharField(max_length=10)
    number = models.IntegerField()
    updated = models.DateTimeField(null=True)
    legislation= models.ForeignKey(Legislation,null=True)
    status_datetime = models.DateTimeField(null=True)
    status = models.CharField(max_length=400)
    sponsor_id = models.ForeignKey(ElectedOfficial,null=True)
    committee = models.ForeignKey(Committee,null=True)
    offered_datetime = models.DateField(null=True)
    description = models.TextField(max_length=50000)
    purpose = models.TextField(max_length=5000)
    amends_sequence = models.IntegerField(null=True)

    def saveXML(self,xml):
        if xml.amendment:
            if xml.amendment.has_key('session'):
                self.session = int(xml.amendment['session'])
            if xml.amendment.has_key('chamber'):
                self.chamber = xml.amendment['chamber']
            if xml.amendment.has_key('number'):
                self.number = int(xml.amendment['number'])
            if xml.amendment.has_key('updated'):
                self.updated = parseDateTime(xml.amendment['updated'])
        if xml.amends:
            if xml.amends.has_key('type') and xml.amends.has_key('number'):
                self.legislation = Legislation.objects.get(bill_type=xml.amends['type'],bill_number=int(xml.amends['number']),bill_session=int(xml.amendment['session']))
            if xml.amends.has_key('sequence') and xml.amends['sequence'] != "":
                self.amends_sequence = int(xml.amends['sequence'])
        if xml.status:
            if xml.status.has_key('datetime'):
                self.status_datetime = parseDateTime(xml.status['datetime'])
            self.status_text = xml.status.contents[0]
        if xml.sponsor and xml.sponsor.has_key('id'):
            self.sponsor_id = ElectedOfficial.objects.get(govtrack_id=int(xml.sponsor['id']))
            #TODO committee
        if xml.offered and xml.offered.has_key('datetime'):
            self.offered_datetime = parseDateTime(xml.offered['datetime'])
        if xml.description:
            self.description = xml.description.contents[0]
        if xml.purpose:
            self.purpose = xml.purpose.contents[0]
        self.save()

#=======================================================================================================================
#
# RollOption
#
#=======================================================================================================================
class RollOption(LGModel):
    key = models.CharField(max_length=100)
    text = models.CharField(max_length=100)


#=======================================================================================================================
#
# CongressRoll
#
#=======================================================================================================================
class CongressRoll(LGModel):
    where = models.CharField(max_length=100)
    session = models.ForeignKey(CongressSessions)
    year = models.IntegerField()
    roll_number = models.IntegerField()
    source =  models.CharField(max_length=100)
    datetime = models.DateTimeField()
    updated = models.DateTimeField()
    aye = models.IntegerField()
    nay = models.IntegerField()
    nv = models.IntegerField()
    present = models.IntegerField()
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=250)
    question = models.CharField(max_length=1000)
    required = models.CharField(max_length=50)
    result = models.CharField(max_length=100)
    bill = models.ForeignKey(Legislation, null=True)
    amendment = models.ForeignKey(LegislationAmendment, null=True)
    options = models.ManyToManyField(RollOption)
    voters = models.ManyToManyField(ElectedOfficial, through='VotingRecord')

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    parsedXML       the XML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self, parsedXML):
        self.where = parsedXML.roll['where']
        self.session = CongressSessions.objects.get(session=int(parsedXML.roll['session']))
        self.year = int(parsedXML.roll['year'])
        self.roll_number = parsedXML.roll['roll']
        self.source = parsedXML.roll['source']
        self.datetime = parseDateTime(parsedXML.roll['datetime'])
        self.updated = parseDateTime(parsedXML.roll['updated'])
        self.aye = int(parsedXML.roll['aye'])
        self.nay = int(parsedXML.roll['nay'])
        self.nv = int(parsedXML.roll['nv'])
        self.present = int(parsedXML.roll['present'])
        self.category = parsedXML.category.contents[0]
        self.type = parsedXML.type.contents[0]
        self.question = parsedXML.question.contents[0]
        self.required = parsedXML.required.contents[0]
        self.result = parsedXML.result.contents[0]
        if parsedXML.bill:
            bill_type = parsedXML.bill['type']
            bill_number = int(parsedXML.bill['number'])
            bill_session = int(parsedXML.bill['session'])
            if Legislation.objects.filter(bill_type=bill_type,bill_number=bill_number,bill_session=bill_session).exists():
                bill =  Legislation.objects.get(bill_type=bill_type,bill_number=bill_number,bill_session=bill_session)
                self.bill = bill
                if parsedXML.amendment and parsedXML.amendment.has_key('number'):
                    number = parsedXML.amendment['number']
                    if "s" in number: chamber="s"
                    else: chamber='h'
                    number = int(number.replace("s",""))
                    if LegislationAmendment.objects.filter(legislation=bill, chamber=chamber, amends_sequence=number):
                        self.amendment = LegislationAmendment.objects.get(legislation=bill, chamber=chamber, amends_sequence=number)
        self.save()
        for option in parsedXML.findAll('option'):
            if not RollOption.objects.filter(key=option['key']):
                newOption = RollOption(key=option['key'], text=option.contents[0])
                newOption.save()
            self.options.add(RollOption.objects.get(key=option['key']))
        for voterXML in parsedXML.findAll('voter'):
            newVotingRecord = VotingRecord()
            newVotingRecord.setSaveAttributes(voterXML,self,self.bill,self.amendment)


#=======================================================================================================================
#
# VotingRecord
#
#=======================================================================================================================
class VotingRecord(LGModel):
    electedofficial = models.ForeignKey(ElectedOfficial)
    roll = models.ForeignKey(CongressRoll)
    bill = models.ForeignKey(Legislation, null=True)
    amendment = models.ForeignKey(LegislationAmendment, null=True)
    votekey = models.CharField(max_length=100)
    votevalue = models.CharField(max_length=100)

    #-------------------------------------------------------------------------------------------------------------------
    # setSaveAttributes
    #   This method sets and saves attributes by extracting the information from parsedXML
    #   @arg    parsedXML       the XML from govtrack.us
    #   @arg    legislation     the legislation which contains this committee
    #   @arg    committeeXML    the XML for a committee tag from parsedXML from govtrack.us
    #   @return void
    #-------------------------------------------------------------------------------------------------------------------
    def setSaveAttributes(self,parsedXML,rollObj,legislation=None,amendment=None):
        if ElectedOfficial.objects.filter(govtrack_id=int(parsedXML['id'])).exists():
            self.electedofficial = ElectedOfficial.objects.get(govtrack_id=int(parsedXML['id']))
            self.roll = rollObj
            if legislation is not None:
                self.bill = legislation
            if amendment is not None:
                self.amendment = amendment
            self.votekey = parsedXML['vote']
            self.votevalue = parsedXML['value']
            self.save()

########################################################################################################################
########################################################################################################################
#   QA Web
#       Question is a piece of content (can be liked, disliked, too_complicated, commented on etc)
#       Users can create questions... but we decide what is official.
#       For any one question there can be as many or as few NextQuestion relations as desired, next_question associates
#       other questions more or less strongly based on the particular answer that the user selected. answer
#       should also have the possible value 'SKIP', which can be taken into account for next_question and for
#       our data about the user and the question.
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# Answer
#
#=======================================================================================================================
class Answer(LGModel):
    answer_text = models.CharField(max_length=500)
    # because each answer must be put on a calibrated scale
    value = models.IntegerField()
    class Admin:
        pass
    def __unicode__(self):
        return self.answer_text

#=======================================================================================================================
# Question
#
#=======================================================================================================================
class Question(Content):
    QUESTION_TYPE = (
        ('MC', 'Multiple Choice'),
        ('CB', 'Check Box'),
        ('SS', 'Sliding Scale')
        )
    question_text = models.TextField(max_length=500)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE)
    relevant_info = models.TextField(max_length=1000, blank=True, null=True)
    official = models.BooleanField()
    lg_weight = models.IntegerField(default=5)
    answers = models.ManyToManyField(Answer)
    class Admin:
        pass
    def __unicode__(self):
        return self.title
    def toJSON(self):
        pass

    #-------------------------------------------------------------------------------------------------------------------
    # Edit method, the question-specific version of the general content method.
    #-------------------------------------------------------------------------------------------------------------------
    def edit(self,field,value):
        if field=="question_text":
            self.question_text=value
        else:
            super(Question, self).edit(field,value)
        self.save()

#=======================================================================================================================
# NextQuestion is essentially a relation from one question to another, based on how you answered the first question.
#
#=======================================================================================================================
class NextQuestion(LGModel):
    from_question = models.ForeignKey(Question, related_name='fquestion')
    to_question = models.ForeignKey(Question, related_name='tquestion')
    answer_value = models.IntegerField(default=-1)
    relevancy = models.IntegerField()

#=======================================================================================================================
# Response, abstract so that content users and groups can inherit from it
#
#=======================================================================================================================
class Response(Content):
    question = models.ForeignKey(Question)
    answer_val = models.IntegerField()
    weight = models.IntegerField(default=5)
    answers = custom_fields.ListField(default=[])    # for storing checkbox response
    #-------------------------------------------------------------------------------------------------------------------
    # Autosaves by adding picture and topic from question.
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.main_image_id = self.question.main_image_id
        self.in_feed = False
        self.save()
        super(Response, self).autoSave(creator=creator, privacy=privacy)
        for t in self.question.topics.all():
            self.topics.add(t)
        return self

    def getValue(self):
        return float(self.answer_val)


#=======================================================================================================================
# Response by a user.
#
#=======================================================================================================================
class UserResponse(Response):
    responder = models.ForeignKey(UserProfile)
    explanation = models.TextField(max_length=1000, blank=True)
    #-------------------------------------------------------------------------------------------------------------------
    # Autosaves with sensible default values.
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.title = unicode(self.question.title + " Response by " + self.responder.get_name())
        self.type = 'R'
        self.in_calc = False
        self.save()
        self.responder.getView().responses.add(self)
        super(UserResponse, self).autoSave(creator=creator, privacy=privacy)

    #-------------------------------------------------------------------------------------------------------------------
    # Updates answer appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def autoUpdate(self, answer_val, explanation):
        self.answer_val = answer_val
        self.explanation = explanation
        self.save()
        return self


########################################################################################################################
########################################################################################################################
#   Debates
#       another important, slightly more complicated piece of content. There will be both persistent and live debates,
#       formal and casual, with group voting and moderator voting. IDEAL, anyone can do it, because its fun and
#       game-like and you and others can see your record...but if you do really well, and are really involved, your
#       your record can actually make your voice more heard, and online debates can become a forum for serious political
#       discourse.
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# A debate message, from a debater at a certain time.
#
#=======================================================================================================================
class Message(Content):
    debater = models.ForeignKey(UserProfile)
    text = models.TextField()
    when = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# A persistent debate. The parent from which other specific kinds of debates will inherit.
#
#=======================================================================================================================
class Persistent(Content):
    # DEBATERS
    affirmative = models.ForeignKey(UserProfile, related_name = "negative", null=True)
    negative = models.ForeignKey(UserProfile, related_name="affirmative", null=True)
    moderator = models.ForeignKey(UserProfile,related_name = "themoderator", null=True)
    # DEBATE RESOLUTION AND STATEMENTS
    resolution = models.CharField(max_length=200)
    statements = models.ManyToManyField(Message)
    # INFO ON DEBATE SETTINGS
    debate_type = models.CharField(max_length=1, choices=DEBATE_CHOICES)
    possible_users = models.ManyToManyField(UserProfile, related_name="possible") # the creator of debate can say who is allowed to join debate
    debate_start_time = models.DateTimeField(auto_now_add=True)
    debate_finish_time = models.DateTimeField(null=True)
    debate_expiration_time = models.DateTimeField(null=True)
    turns_total = models.IntegerField(default=6)      # number of responses per user, default is 6
    allotted_response_delta = models.IntegerField(default=-1)      # window to respond, in minutes, default is unlimited
    allotted_debate_delta = models.IntegerField(default=-1)         # total time for debate, in minutes, default is unlimited
    allotted_expiration_delta = models.IntegerField(default=10080) # time post debate finish, until winner is determined by votes. default=1week
    # DETERMINATION OF WINNER
    votes_affirmative = models.IntegerField(default=0)
    votes_negative = models.IntegerField(default=0)
    turns_elapsed = models.IntegerField(default=0)        # number of turns passed so far
    turn_current = models.BooleanField(default=True)
    turn_lasttime = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(UserProfile, null=True, related_name ="thewinner")
    debate_finished = models.BooleanField(default=False)
    voting_finished = models.BooleanField(default=False)

    #-------------------------------------------------------------------------------------------------------------------
    # # sets debate to voting finished and determines winner
    #-------------------------------------------------------------------------------------------------------------
    def addMessage(self, text):
        now = datetime.datetime.now()
        message = Message(text=text)
        if self.turn_current:
            message.debater = self.affirmative
            to_user = self.negative
        else:
            message.debater = self.negative
            to_user = self.affirmative
        message.save()
        self.statements.add(message)
        # switch current_turn
        self.turn_current = not self.turn_current
        self.turn_lasttime = now
        self.turns_elapsed += 1
        self.save()
        # check if turns have expired
        if self.turns_elapsed > self.turns_total:
            self.debate_finish_time = now
            self.debate_expiration_time = now + self.getDelta(self.allotted_expiration_delta)
            # for testing !!
            test_delta = timedelta(seconds=60)
            self.debate_expiration_time = now + test_delta
            # 3nd of test
            self.debate_finished = True
            self.save()
            # alert other user that debate is finished.
            alert_text = message.debater.get_name() + " responded and the debate is finished."
        # else alert the other debater it is now their turn.
        else:
            alert_text = message.debater.get_name() + " responded and it is your turn."
            # send notification
        to_user.debateNotification(message=alert_text, debate=self, from_user = message.debater)
        return HttpResponse("message added")

    #-------------------------------------------------------------------------------------------------------------------
    # # sets debate to voting finished and determines winner
    #-------------------------------------------------------------------------------------------------------------
    def setOver(self):
        self.voting_finished = True
        # deterimine winner of debate by type
        if self.debate_type == 'C':
            winner_text = "The debate is finished."
            loser_text = "The debate is finished."
            winner = self.affirmative
            loser = self.negative
            tie = False
        elif self.debate_type == 'F':
            winner_text = "You won a debate!"
            loser_text = "You lost a debate."
            if self.votes_affirmative > self.votes_negative:
                self.winner = self.affirmative
                winner = self.winner
                loser = self.negative
                tie = False
            elif self.votes_negative > self.votes_affirmative:
                self.winner = self.negative
                winner = self.winner
                loser = self.affirmative
                tie = False
            else:
                tie = True
                winner = self.affirmative
                loser = self.negative
                winner_text = "You tied a debate."
                loser_text = "You tied a debate."
        else:
            print "cmann"
            return HttpResponse("moderator did not vote")
            # save
        self.save()
        # alert winner that they won and loser that they lost
        if tie:
            # add tie to both debate records
            winner.addDebateResult(self, 0)
            loser.addDebateResult(self, 0)
        else:
            winner.addDebateResult(self, 1)
            loser.addDebateResult(self, -1)
        winner.debateNotification(debate=self, from_user=loser, message=winner_text)
        loser.debateNotification(debate=self, from_user=winner, message=loser_text)
        return HttpResponse("And it was decided..")

    #-------------------------------------------------------------------------------------------------------------------
    # Checks if debate is over, as well as checking if turn has expired.
    #-------------------------------------------------------------------------------------------------------------
    def update(self):
        now = datetime.datetime.now()
        # check if debate already finished
        if self.debate_finished:
            # check if voting already finished
            if self.voting_finished:
                return HttpResponse("debate closed")
            else:
                # check if now is greater than expiration time
                if now > self.debate_expiration_time:
                    # sets debate to voting finished and determines winner
                    return self.setOver()
        else:
            if now > self.debate_finish_time:
                self.finished = True
                return HttpResponse("debate finished")
            else:
                # else check if current turn has expired
                turn_delta = self.getDelta(self.allotted_response_delta)
                turn_over = self.turn_lasttime + turn_delta
                if now > turn_over:
                    # send missed turn message
                    return self.addMessage("[missed turn]")
        return HttpResponse("already up to date")

    #-------------------------------------------------------------------------------------------------------------------
    # Takes in a duration value (in minutes), and returns a python timedelta of that value
    #-------------------------------------------------------------------------------------------------------------------
    def getDelta(self, x):
        # if unlimited
        if x == -1:
            delta = timedelta(days=100)
        else:
            delta = timedelta(minutes=x)
        return delta

    #-------------------------------------------------------------------------------------------------------------------
    # Invites user to debate, and adds to list of possible users.
    #-------------------------------------------------------------------------------------------------------------------
    def invite(self, user, inviter, privacy='PUB'):
        already_invited = DebateJoin.objects.filter(user=user, group=self)
        if already_invited:
            already_invited[0].invite()
        else:
            invitation = DebateJoin(user=user, content=self, group=self, privacy=privacy)
            invitation.autoSave()
            invitation.invite(inviter=inviter)
        self.possible_users.add(user)

    #-------------------------------------------------------------------------------------------------------------------
    # Autocreates and saves a debate with appropriate settings based on its type.
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        if self.debate_type == 'F':
            now = datetime.datetime.now()
            # this is default settings
            self.title = "Debate: " + self.resolution
            self.type = 'Y'
            self.debate_finish_time = now + self.getDelta(self.allotted_debate_delta)
            self.save()
            super(Persistent, self).autoSave(creator=creator, privacy=privacy)
        else:
            print "not yet implemented"




########################################################################################################################
########################################################################################################################
#   Comparisons and Aggregate Views
#
#
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# Model for entire worldview.
#
#=======================================================================================================================
class WorldView(LGModel):
    responses = models.ManyToManyField(Response)

#=======================================================================================================================
# Comparison of specific topic.
#
#=======================================================================================================================
class TopicComparison(LGModel):
    topic = models.ForeignKey(Topic)
    result = models.IntegerField()
    num_q = models.IntegerField()
    def update(self, result, num_q):
        self.result = result
        self.num_q = num_q
        self.save()

#=======================================================================================================================
# Comparison of entire world view.
#
#=======================================================================================================================
class ViewComparison(LGModel):
    viewA = models.ForeignKey(WorldView, related_name="viewa")
    viewB = models.ForeignKey(WorldView, related_name="viewb")
    when = models.DateTimeField(auto_now_add=True)
    result = models.IntegerField()
    num_q = models.IntegerField()
    bytopic = models.ManyToManyField(TopicComparison)

    def get_url(self):
        return '/comparison/' + str(self.id)

    def update(self, result, num_q, when):
        self.result = result
        self.num_q = num_q
        self.when = when
        self.save()

    def toDict(self):
        toReturn = []
        for topic_text in MAIN_TOPICS:
            topic = self.bytopic.filter(topic__topic_text=topic_text)
            topicDict = {'text':topic_text,
                         'colors': MAIN_TOPICS_COLORS[topic_text],
                         'mini_img': MAIN_TOPICS_MINI_IMG[topic_text],
                         'order': MAIN_TOPICS_CLOCKWISE_ORDER[topic_text],
                         'result':0,
                         'num_q':0}
            if topic:
                comparison = topic[0]
                topicDict['result'] = comparison.result
                topicDict['num_q'] = comparison.num_q
            toReturn.append(topicDict)
        vals = {'topics':toReturn,'main':{'result':self.result,'num_q':self.num_q}}
        user = UserProfile.lg.get_or_none(view_id=self.viewB.id)
        if user: vals['user_url'] = user.getWebUrl()
        else: vals['user_url'] = ''
        return vals

    def toJSON(self):
        return json.dumps(self.toDict())

    # checks if the comparison is still valid given the two inputted dates, returns True if Stale, false if still fresh
    def checkStale(self, dateA=None, dateB=None):
        if dateA and dateB:
            newest = max(dateA, dateB)
            return self.when < newest
        else:
            return True






#=======================================================================================================================
# Comparison of two people's worldview.
#
#=======================================================================================================================
class UserComparison(ViewComparison):
    userA = models.ForeignKey(UserProfile, related_name="a")
    userB = models.ForeignKey(UserProfile, related_name="b")
    def autoSave(self):
        self.viewA = self.userA.getView()
        self.viewB = self.userB.getView()
        self.save()


#=======================================================================================================================
# Tuple for storing how many people in an aggregate view chose this answer.
#
#=======================================================================================================================
class AggregateTuple(LGModel):
    answer_val = models.IntegerField()
    tally = models.IntegerField()

#=======================================================================================================================
# Model for storing how a group of people answered a question.
#
#=======================================================================================================================
class AggregateResponse(Response):
    users = models.ManyToManyField(UserProfile)
    responses = models.ManyToManyField(AggregateTuple)
    answer_avg = models.DecimalField(default=0, max_digits=4, decimal_places=2)
    total = models.IntegerField()
    def autoSave(self):
        self.type = 'Z'
        self.in_feed = False
        self.in_search = False
        self.in_calc = False
        self.save()
        super(AggregateResponse, self).autoSave()

    def getValue(self):
        return float(self.answer_avg)

    #-------------------------------------------------------------------------------------------------------------------
    # Clears m2m and deletes tuples
    #-------------------------------------------------------------------------------------------------------------------
    def smartClearResponses(self):
        self.responses.all().delete()

########################################################################################################################
########################################################################################################################
#   Groups
#       pretty simple right now...but planning to make Democratic groups and other kinds much more interesting in
#       in the future... idea - groups with serious rules and even more serious and transparent security (crypotgraphical)
#       that eventually can serve as politically functioning bodies in their onw right (really putting politics online).
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# The basic group (will be fleshed out by having child models inherit from this).
#
#=======================================================================================================================
class Group(Content):
    # people
    admins = models.ManyToManyField(UserProfile, related_name='admin')
    members = models.ManyToManyField(UserProfile, related_name='member')
    # info
    full_text = models.TextField(max_length=1000)
    group_content = models.ManyToManyField(Content, related_name='ongroup')
    group_view = models.ForeignKey(WorldView)           # these are all aggregate response, so they can be downcasted
    group_newfeed = models.ManyToManyField(FeedItem, related_name='groupnew')
    group_hotfeed = models.ManyToManyField(FeedItem, related_name='grouphot')
    group_bestfeed = models.ManyToManyField(FeedItem, related_name='groupbest')
    # group type
    group_privacy = models.CharField(max_length=1,choices=GROUP_PRIVACY_CHOICES, default='O')
    group_type = models.CharField(max_length=1,choices=GROUP_TYPE_CHOICES, default='U')
    democratic = models.BooleanField(default=False)
    system = models.BooleanField(default=False)     # means you can't leave

    #-------------------------------------------------------------------------------------------------------------------
    # Returns json of histogram data.
    #-------------------------------------------------------------------------------------------------------------------
    def getComparisonHistogram(self, user, topic_alias=None, resolution=10):
        from modernpolitics.backend import getUserUserComparison
        histogram = {}                  # initialize empty histogram
        topic = Topic.lg.get_or_none(alias=topic_alias)
        for i in range(0, resolution+1):
            histogram[i]= {'num':0, 'percent':0}
        members = self.members.all()
        for x in members:
            comparison = getUserUserComparison(user, x)
            if topic and topic_alias != 'general':
                comparison = comparison.bytopic.get(topic=topic)
            if comparison.num_q:
                block = comparison.result / 10
                if block in histogram:
                    histogram[block]['num'] += 1
        # calc percents
        people = float(len(members))
        for k in histogram:
            tuple = histogram[k]
            num = tuple['num']
            if  not num:
                pix = 5
            else:
                pix = (num/people*100)*5
            tuple['pix'] = int(pix)
        return histogram

    #-------------------------------------------------------------------------------------------------------------------
    # Edit method, the group-specific version of the general content method.
    #-------------------------------------------------------------------------------------------------------------------
    def edit(self,field,value):
        if field=="full_text":
            self.full_text=value
        else:
            super(Group, self).edit(field,value)
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # autosave
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.type='G'
        worldview = WorldView()
        worldview.save()
        self.group_view = worldview
        self.save()
        super(Group, self).autoSave(creator=creator, privacy=privacy)

    #-------------------------------------------------------------------------------------------------------------------
    # getFeed
    #-------------------------------------------------------------------------------------------------------------------
    def getFeed(self):
        return self.group_newfeed.order_by('-rank')

    #-------------------------------------------------------------------------------------------------------------------
    # getGroupView
    #-------------------------------------------------------------------------------------------------------------------
    def getGroupView(self):
        return self.group_view

    #-------------------------------------------------------------------------------------------------------------------
    # check if group has member
    #-------------------------------------------------------------------------------------------------------------------
    def hasMember(self, user):
        test = self.members.filter(id=user.id)
        if test:
            return True
        else:
            return False

    #-------------------------------------------------------------------------------------------------------------------
    # gets group motions
    #-------------------------------------------------------------------------------------------------------------------
    def getMotions(self):
        motions = Motion.objects.filter(group=self)
        return motions

    #-------------------------------------------------------------------------------------------------------------------
    # Clears m2m and deletes tuples
    #-------------------------------------------------------------------------------------------------------------------
    def smartClearGroupFeed(self, feed_type):
        if feed_type=='N':
            self.group_newfeed.all().delete()
        elif feed_type=='B':
            self.group_bestfeed.all().delete()
        elif feed_type=='H':
            self.group_hotfeed.all().delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Get members, filtered by some criteria
    #-------------------------------------------------------------------------------------------------------------------
    def getMembers(self, user, block=-1, topic_alias=None):
        from modernpolitics.backend import getUserUserComparison
        if block == -1:
            return self.members.order_by('id')
        else:
            topic = Topic.lg.get_or_none(alias=topic_alias)
            ids = []
            for x in self.members.order_by('id'):
                comparison = getUserUserComparison(user, x)
                if topic and topic_alias!='general':
                   comparison = comparison.bytopic.get(topic=topic)
                if comparison.num_q:
                    x_block = comparison.result / HISTOGRAM_RESOLUTION
                    if x_block == block:
                        ids.append(x.id)
            return self.members.filter(id__in=ids).order_by('id')

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowRequests(self, num=-1):
        if num == -1:
            return GroupJoined.objects.filter( group=self, confirmed=False, requested=True, rejected=False ).order_by('when').reverse()
        else:
            return GroupJoined.objects.filter( group=self, confirmed=False, requested=True, rejected=False ).order_by('when').reverse()[:num]


    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getActivity(self, start=0, num=-1):
        gmembers = self.members.all()
        actions = Action.objects.filter(relationship__user__in=gmembers, relationship__privacy='PUB').order_by('when').reverse()
        if num != 1:
            actions = actions[start:start+num]
        return actions


#=======================================================================================================================
# Motion, for democratic groups.
#
#=======================================================================================================================
class Motion(Content):
    group = models.ForeignKey(Group)
    motion_type = models.CharField(max_length=1, choices=MOTION_CHOICES, default='O')
    full_text = models.TextField()

    #-------------------------------------------------------------------------------------------------------------------
    # autosave
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.type='M'
        self.save()
        super(Motion, self).autoSave(creator=creator, privacy=privacy)


#=======================================================================================================================
# Network Group
#
#=======================================================================================================================
class Network(Group):
    name = models.CharField(max_length=50)                  # DEPRECATED
    network_type = models.CharField(max_length=1, choices=NETWORK_TYPE, default='D')
    extension = models.CharField(max_length=50, null=True)

    # autosave any network
    def autoSave(self, creator=None, privacy="PUB"):
        self.group_type = 'N'
        self.system = True
        self.group_privacy = "P"
        super(Network, self).autoSave()

    def get_url(self):
        return '/network/' + self.alias + '/'

#=======================================================================================================================
# User Group
#
#=======================================================================================================================
class UserGroup(Group):
    def autoSave(self, creator=None, privacy="PUB"):
        self.in_feed = True
        super(UserGroup, self).autoSave()
    pass

########################################################################################################################
########################################################################################################################
#
# User Logging and Authorization
#
########################################################################################################################
########################################################################################################################

def secondsToTimeObj(seconds):
    hours = int(seconds/3600)
    minutes = int((seconds%3600)/60)
    seconds = seconds%60
    return datetime.time(hour=hours,minute=minutes,second=seconds)

#=======================================================================================================================
# Saves a widget access
#
#=======================================================================================================================
class WidgetAccess(LGModel):
    path = models.CharField(max_length=500, null=True)
    host = models.CharField(max_length=100, null=True)
    when = models.DateTimeField(auto_now_add=True)
    which = models.CharField(max_length=30)

#=======================================================================================================================
# Stores every page and action by users.
#
#=======================================================================================================================
class PageAccess(LGModel):
    ACCESS_CHOICES= ('POST', 'GET')
    user = models.ForeignKey(UserProfile)
    ipaddress = models.IPAddressField(default='255.255.255.255', null=True)
    page = models.CharField(max_length=50)
    action = models.CharField(max_length=50, null=True)
    when = models.DateTimeField(auto_now_add=True)
    left = models.DateTimeField(null=True)
    duration = models.TimeField(null=True)
    type = models.CharField(max_length=4)
    exit = models.BooleanField(default=False)
    login = models.BooleanField(default=True)

    def autoSave(self, request):
        if not LOCAL:
            user_prof = ControllingUser.lg.get_or_none(id=request.user.id)
            if user_prof:
                user_prof = user_prof.user_profile
                self.user = user_prof
                self.page = request.path
                self.ipaddress = request.META['REMOTE_ADDR']
                if not UserIPAddress.objects.filter(user=self.user, ipaddress=self.ipaddress):
                    newUserIPAddress = UserIPAddress(user=self.user,ipaddress=self.ipaddress)
                    newUserIPAddress.autoSave()
                if request.method == "POST":
                    self.type = 'POST'
                    if 'action' in request.POST:
                        self.action = request.POST['action']
                else:
                    self.type = 'GET'
                    if 'action' in request.GET:
                        self.action = request.GET['action']
                self.save()
                user_prof.last_page_access = self.id
                user_prof.save()


#-----------------------------------------------------------------------------------------------------------------------
# ipAddrConvert
#   @arg ipaddr         string of an IP address
#   @return integer     ipnum for geodata
#-----------------------------------------------------------------------------------------------------------------------
def ipAddrConvert(ipaddr):
    split = str(ipaddr).split('.')
    return (int(split[0])*16777216) + (int(split[1]) * 65536) + (int(split[2])*256) + int(split[3])

#=======================================================================================================================
# UserIPAddress
#   Stores IP addresses from which a user uses our site.  Also stores the location ID so that we may track where
#   they are logging in from.
#=======================================================================================================================
class UserIPAddress(LGModel):
    user = models.ForeignKey(UserProfile)
    ipaddress = models.IPAddressField(default='255.255.255.255')
    locID = models.IntegerField()

    def autoSave(self):
        def threadSave(self):
            ipnum = ipAddrConvert(self.ipaddress)
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT locID FROM geodata.`GeoLiteCity-Blocks` where " + str(ipnum) + " BETWEEN startIPNum and endIPNum LIMIT 1;")
            result = cursor.fetchall()
            self.locID = int(result[0][0])
            self.save()
        thread.start_new_thread(threadSave,(self,))


#=======================================================================================================================
# Stores what scripts are run and by who.
#
#=======================================================================================================================
class Script(LGModel):
    user = models.CharField(max_length=50)
    command = models.CharField(max_length=400)
    when = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# Stores when an email is sent.
#
#=======================================================================================================================
class SentEmail(LGModel):
    user = models.CharField(max_length=50)
    from_email = models.CharField(max_length=50)
    to_email = models.CharField(max_length=50)
    message = models.CharField(max_length=100)
    when = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# Stores user feedback
#
#=======================================================================================================================
class Feedback(LGModel):
    user = models.ForeignKey(UserProfile)
    feedback = models.TextField()
    when = models.DateTimeField(auto_now_add=True)
    page = models.CharField(max_length=200)

#=======================================================================================================================
# Stores email list
#
#=======================================================================================================================
class EmailList(LGModel):
    email = models.EmailField()
    when = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# Stores an error message, for when a 500 server-error happens.
#
#=======================================================================================================================
class Bug(LGModel):
    user = models.ForeignKey(UserProfile)
    error = models.TextField()
    when = models.DateTimeField(auto_now_add=True)
    page = models.CharField(max_length=200)

#=======================================================================================================================
# For validating specific user emails that we are accepting to use our site
#
#=======================================================================================================================
class ValidEmail(LGModel):
    email = models.EmailField()
    description = models.CharField(max_length=1000, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

#=======================================================================================================================
# For validating email extensions that we are accepting to use our site
#
#=======================================================================================================================
class ValidEmailExtension(LGModel):
    extension = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

########################################################################################################################
########################################################################################################################
#   Relationships
#
#
########################################################################################################################
########################################################################################################################
class Relationship(Privacy):
    user = models.ForeignKey(UserProfile, related_name='frel')
    when = models.DateTimeField(auto_now_add=True)
    relationship_type = models.CharField(max_length=2,choices=RELATIONSHIP_CHOICES)
    #-------------------------------------------------------------------------------------------------------------------
    # Downcasts relationship to appropriate child model.
    #-------------------------------------------------------------------------------------------------------------------
    def downcast(self):
        type = self.relationship_type
        if type == 'VO':
            object = self.ucrelationship.voted
        elif type == 'CR':
            object = self.ucrelationship.created
        elif type == 'CO':
            object = self.ucrelationship.commented
        elif type == 'ED':
            object = self.ucrelationship.edited
        elif type == 'SH':
            object = self.ucrelationship.shared
        elif type == 'FC':
            object = self.ucrelationship.followed
        elif type == 'DV':
            object = self.ucrelationship.debatevoted
        elif type == 'MV':
            object = self.ucrelationship.motionvoted
        elif type == 'XX':
            object = self.ucrelationship.deleted
        # relationships with invite/request/decline/reject. all inherit from Invite , below
        elif type == 'AE':
            object = self.ucrelationship.attending
        elif type== 'JO':
            object = self.ucrelationship.groupjoined
        elif type== 'JD':
            object = self.ucrelationship.debatejoined
        elif type == 'FO':
            object = self.uurelationship.userfollow
        elif type == 'SI':
            object = self.ucrelationship.signed
        else:
            object = self
        return object

    def getFrom(self):
        return self.user

    def getTo(self):
        return self.downcast().getTo()

#=======================================================================================================================
# Abstract model for handling relationships with requests and invitations.
#=======================================================================================================================
class Invite(LGModel):
    confirmed = models.BooleanField(default=False)
    invited = models.BooleanField(default=False)        # unused in bi-directional relationships
    requested = models.BooleanField(default=False)
    inviter = models.IntegerField(default=-1)           # foreign key to userprofile, inviter
    rejected = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)

    class Meta:
        abstract=True
    def confirm(self):
        self.confirmed = True
        self.save()
    def request(self):
        self.requested = True
        if self.invited:
            self.confirm()
        else:
            self.save()
    def invite(self, inviter):
        self.invited = True
        self.inviter = inviter.id
        if self.requested:
            self.confirm()
        else:
            self.save()
    def getInviter(self):
        if self.inviter == -1:
            return None
        else:
            return UserProfile.objects.get(id=self.inviter)
    def clear(self):
        self.confirmed = False
        self.requested = False
        self.invited = False
        self.declined = False
        self.rejected = False
        self.save()
        ##### EVERYTHING BELOW IS DEPRECATED #####
    def reject(self):
        if self.requested:
            self.rejected = True
            self.save()
    def decline(self):
        if self.invited:
            self.declined = True
            self.save()
    def accept(self):
        if self.invited:
            self.confirm()
    def allow(self):
        if self.requested:
            self.confirm()
    def remove(self):
        if self.confirmed:
            self.confirmed = False
            self.rejected = True
            self.save()

#=======================================================================================================================
# Relationships between User and Content.
# This is the parent model for such relationships from which all specific relationships inherit.
#=======================================================================================================================
class UCRelationship(Relationship):
    content = models.ForeignKey(Content, related_name='trel')
    def getTo(self):
        return self.content

#=======================================================================================================================
# Exact same as vote, except for debates.
# inherits from relationship
#=======================================================================================================================
class DebateVoted(UCRelationship):
    value = models.IntegerField()        # 1 is like, 0 neutral, -1 dislike
    def autoSave(self):
        self.relationship_type = 'DV'
        self.creator=self.user_id
        self.save()

#=======================================================================================================================
# Exact same as vote, except for motions.
# inherits from relationship
#=======================================================================================================================
class MotionVoted(UCRelationship):
    value = models.IntegerField()        # 1 is like, 0 neutral, -1 dislike
    def autoSave(self):
        self.relationship_type = 'MV'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Vote by a user on a piece of content. like or dislike.
# inherits from relationship
#=======================================================================================================================
class Voted(UCRelationship):
    value = models.IntegerField(default=0)        # 1 is like, 0 neutral, -1 dislike
    def autoSave(self):
        self.relationship_type = 'VO'
        self.creator = self.user
        self.save()

    def getValue(self, ranking='D'):
        if ranking=='D':
            if self.value == 1:
                value = 1
            elif self.value == -1:
                value = -1
            else:
                value = 0
        else: value = 0
        return value

#=======================================================================================================================
# Stores what content a user has created.
# inherits from relationship
#=======================================================================================================================
class Created(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'CR'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# User deletes content.
#=======================================================================================================================
class Deleted(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'XX'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Stores what content a user has created.
# inherits from relationship
#=======================================================================================================================
class Commented(UCRelationship):
    comment = models.ForeignKey(Comment)
    def autoSave(self):
        self.relationship_type = 'CO'
        self.creator = self.user
        content = self.comment.root_content
        content.num_comments += 1
        content.save()
        self.save()

#=======================================================================================================================
# Stores when a user edits a piece of content.
# inherits from relationship
#=======================================================================================================================
class Edited(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'ED'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Stores a user sharing a piece of content.
# inherits from relationship
#=======================================================================================================================
class Shared(UCRelationship):
    share_users = models.ManyToManyField(UserProfile)
    share_groups = models.ManyToManyField(Group)
    def autoSave(self):
        self.relationship_type = 'SH'
        self.creator = self.user
        self.save()

    def addUser(self, user):
        if not user in self.share_users:
            self.share_users.add(user)
            # follow notification flow

    def addGroup(self, group):
        if not group in self.share_groups:
            self.share_groups.add(group)
            # follow notification flow

#=======================================================================================================================
# Stores a user sharing a piece of content.
# inherits from relationship
#=======================================================================================================================
class Signed(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'SI'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Stores a user following a piece of content.
# inherits from relationship
#=======================================================================================================================
class Followed(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'FC'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Relation between user and event, about whether or not they are attending.
#
#=======================================================================================================================
class Attending(UCRelationship, Invite):
    CONFIRMATION_CHOICE = (
        ('Y','yes'),
        ('N','no'),
        ('M','maybe')
        )
    choice = models.CharField(max_length=1, choices=CONFIRMATION_CHOICE)
    def autoSave(self):
        self.relationship_type = 'AE'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Relation between user and event, about whether or not they are attending.
#
#=======================================================================================================================
class GroupJoined(UCRelationship, Invite):
    group = models.ForeignKey(Group)
    def autoSave(self):
        self.relationship_type = 'JO'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# Relation between user and event, about whether or not they are attending.
#
#=======================================================================================================================
class DebateJoined(UCRelationship, Invite):
    debate = models.ForeignKey(Persistent)
    def autoSave(self):
        self.relationship_type = 'JD'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# relationship between two users
#=======================================================================================================================
class UURelationship(Relationship):
    to_user = models.ForeignKey(UserProfile, related_name='tuser')
    def getTo(self):
        return self.to_user

#=======================================================================================================================
# Friends, (relationships between users)
#=======================================================================================================================
class UserFollow(UURelationship, Invite):
    fb = models.BooleanField(default=False)
    def autoSave(self):
        self.creator = self.user
        self.relationship_type = 'FO'
        self.save()

#=======================================================================================================================
# Linked, (relationships between two pieces of content)
#
#=======================================================================================================================
class Linked(LGModel):
    from_content = models.ForeignKey(Content, related_name='fcontent')
    to_content = models.ForeignKey(Content, related_name='tcontent')
    link_strength = models.IntegerField()
    link_bonus = models.IntegerField(default=0)      # made by users who link content
    association_strength = models.IntegerField(default=0)
    when = models.DateTimeField(auto_now_add=True)
    def autoSave(self):
        self.link_strength = self.association_strength + self.link_bonus
        self.save()

########################################################################################################################
########################################################################################################################
#   For storing what goes on your profile page.
#
#
########################################################################################################################
#####################################################################################################################
#=======================================================================================================================
# For storing some content on a users profile page.
#
#=======================================================================================================================
class MyContent(LGModel):
    content = models.ForeignKey(Content)
    rank = models.IntegerField()

#=======================================================================================================================
# For storing some people on a users profile page.
#
#=======================================================================================================================
class MyPeople(LGModel):
    person = models.ForeignKey(UserProfile)
    rank = models.IntegerField()

#=======================================================================================================================
# For storing activity on a users profile page.
#
#=======================================================================================================================
class MyAction(LGModel):
    action = models.ForeignKey(Action)
    rank = models.IntegerField()

#=======================================================================================================================
# For a user to write about their views on a topic.
#
#=======================================================================================================================
class TopicView(Privacy):
    view = models.TextField(max_length=10000, blank=True)
    topic = models.ForeignKey(Topic)

#=======================================================================================================================
# Stores information about what should be displyed on user's profile page.
#
#=======================================================================================================================
class ProfilePage(LGModel):
    person = models.ForeignKey(UserProfile)
    bio = models.TextField(max_length=5000, blank=True)
    my_views = models.ManyToManyField(TopicView)
    # I don't want to use these. for efficiency. but here just in case.
    my_content = models.ManyToManyField(MyContent)
    my_people = models.ManyToManyField(MyPeople)
    my_activity = models.ManyToManyField(MyAction)
    #-------------------------------------------------------------------------------------------------------------------
    # Adds content to profile page.
    #-------------------------------------------------------------------------------------------------------------------
    def addContent(self, content):
        new_content = MyContent(content=content, rank=0)
        new_content.save()
        self.my_content.add(new_content)

    #-------------------------------------------------------------------------------------------------------------------
    # Adds politician to profile page.
    #-------------------------------------------------------------------------------------------------------------------
    def addPerson(self, person):
        new_person = MyPeople(person=person, rank=0)
        new_person.save()
        self.my_people.add(new_person)

    #-------------------------------------------------------------------------------------------------------------------
    # Removes content from profile page.
    #-------------------------------------------------------------------------------------------------------------------
    def removeContent(self, content):
        to_remove = self.my_content.filter(content=content)
        if to_remove:
            to_remove.delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Removes politician from profile page.
    #-------------------------------------------------------------------------------------------------------------------
    def removePerson(self, people):
        to_remove = self.my_people.filter(person=person)
        if to_remove:
            to_remove.delete()


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


class LGNumber(LGModel):
    alias = models.CharField(max_length=50)
    number = models.IntegerField()


#=======================================================================================================================
# Handles password resets
#=======================================================================================================================
#TODO: make this link expire after a certain length of time
class ResetPassword(LGModel):
    userProfile = models.ForeignKey(UserProfile)
    email_code = models.CharField(max_length=75)

    def create(username):
        from lovegov.modernpolitics.helpers import generateRandomPassword
        toDelete = ResetPassword.lg.get_or_none(userProfile__username=username)
        if toDelete: toDelete.delete()

        userProfile = UserProfile.lg.get_or_none(username=username)
        if userProfile and userProfile.confirmed:
            try:
                userProfile = UserProfile.objects.get(username=username)
                reseturl = generateRandomPassword(50)
                new = ResetPassword(userProfile=userProfile,email_code=reseturl)
                new.save()
                vals = {'firstname':userProfile.first_name, 'url':reseturl}
                send_email.sendTemplateEmail("LoveGov Password Recovery",'passwordRecovery.html',vals,'info@lovegov.com',userProfile.username)
                return True
            except:
                return False
        else:
            return False
    create = staticmethod(create)


class BlogEntry(LGModel):
    CATEGORY_CHOICES = ['General','Update','News']
    creator = models.ForeignKey(UserProfile)
    datetime = models.DateTimeField(auto_now_add=True)
    category = custom_fields.ListField()
    title = models.CharField(max_length=5000)
    message = models.TextField()

    def getURL(self):
        return '/blog/' + self.creator.alias + '/' + str(self.id)





########################################################################################################################
########################################################################################################################
#  Deprecated
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

#=======================================================================================================================
# Temp models and models for optimization.
#=======================================================================================================================
class QuestionDiscussed(LGModel):
    question = models.ForeignKey(Question)
    num_comments = models.IntegerField()        # number of comments, including replies

# for ordering questions
class qOrdered(LGModel):
    question = models.ForeignKey(Question)
    rank = models.IntegerField()

# model for creating ordered lists of questions
class QuestionOrdering(LGModel):
    alias = models.CharField(max_length=30)
    questions = models.ManyToManyField(qOrdered)





