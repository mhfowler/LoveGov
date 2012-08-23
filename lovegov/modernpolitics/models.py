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
import time
from datetime import timedelta
from datetime import datetime

# lovegov
from lovegov.modernpolitics import custom_fields
from lovegov.modernpolitics.constants import *

import logging

logger = logging.getLogger('filelogger')
scheduled_logger = logging.getLogger('scheduledlogger')
normal_logger = logging.getLogger('filelogger')
errors_logger = logging.getLogger('errorslogger')
temp_logger = logging.getLogger('templogger')
lg_logger = logging.getLogger("lglogger")

#-----------------------------------------------------------------------------------------------------------------------
# Useful manager for all our models.
#-----------------------------------------------------------------------------------------------------------------------
class LGManager(models.Manager):
    """Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        to_return = self.filter(**kwargs)
        if to_return:
            return to_return[0]
        else:
            return to_return

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
    creator = models.ForeignKey("UserProfile", default=1)             # 154 is lovegov user
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
            from lovegov.modernpolitics.backend import getLoveGovUser
            return getLoveGovUser() 
        return creator

    def getCreatorDisplay(self, viewer=None):
        from lovegov.modernpolitics.initialize import getAnonUser
        if self.getPublic():
            creator = self.getCreator()
        else:
            creator = getAnonUser()
        if viewer:
            creator.you = (self.getCreator() == viewer)
        else:
            creator.you = None

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
    longitude = models.DecimalField(max_digits=30, decimal_places=15, null=True)
    latitude = models.DecimalField(max_digits=30, decimal_places=15, null=True)
    state = models.CharField(max_length=2, null=True)
    city = models.CharField(max_length=500, null=True)
    district = models.IntegerField(null=True)

    def clear(self):
        self.address_string = None
        self.zip = None
        self.longitude = None
        self.latitude = None
        self.state = None
        self.city = None
        self.district = None
        self.save()

#=======================================================================================================================
# Abstract tuple for representing what location and scale content is applicable to.
#=======================================================================================================================
class LocationLevel(models.Model):
    location = models.ForeignKey(PhysicalAddress, null=True, blank=True)
    scale = models.CharField(max_length=1, choices=SCALE_CHOICES, default='A')
    class Meta:
        abstract = True

    def getScaleVerbose(self):
        scale = self.scale
        if scale == 'L':
            return 'Local'
        elif scale == 'S':
            return 'State'
        elif scale == 'F':
            return 'Federal'
        elif scale == 'W':
            return 'World'
        elif scale == 'A':
            return 'Uncategorized'
        else:
            return 'None'


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
    # fields for images
    icon = models.ImageField(null=True, upload_to="defaults/")
    image = models.ImageField(null=True, upload_to="defaults/")
    hover = models.ImageField(null=True, upload_to="defaults/")
    selected = models.ImageField(null=True, upload_to="defaults/")

    def __unicode__(self):
        return self.topic_text

    def getColor(self):
        return MAIN_TOPICS_COLORS_ALIAS[self.alias]['default']
    def getLightColor(self):
        return MAIN_TOPICS_COLORS_ALIAS[self.alias]['light']

    def getColors(self):
        return {'color':self.color,'color_light':self.color_light}

    def getQuestions(self):
        return Question.objects.filter(official=True, main_topic=self).order_by("-rank")

    def getContent(self):
        ids = []
        for c in Content.objects.filter(Q(type='P') | Q(type='N')):
            if c.getMainTopic() == self:
                ids.append(c.id)
        return Content.objects.filter(id__in=ids)

    def getPre(self):
        return self.alias[0:3]

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

    def getImageURL(self):
        return self.image.url

    def getIconURL(self):
        return self.icon.url


class OfficeTag(LGModel):
    name = models.CharField(max_length=100)


#=======================================================================================================================
# Content
#
#=======================================================================================================================
class Content(Privacy, LocationLevel):
    # unique identifier
    alias = models.CharField(max_length=1000, default="default")
    # optimizations for excluding some types of content
    in_feed = models.BooleanField(default=False)
    in_search = models.BooleanField(default=False)
    in_calc = models.BooleanField(default=False)
    # FIELDS
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    topics = models.ManyToManyField(Topic)
    main_topic = models.ForeignKey(Topic, null=True, related_name="maintopic", blank=True)
    title = models.CharField(max_length=500)
    summary = models.TextField(max_length=500, blank=True, null=True)
    created_when = models.DateTimeField(auto_now_add=True)
    main_image = models.ForeignKey("UserImage", null=True, blank=True)
    active = models.BooleanField(default=True)
    calculated_view = models.ForeignKey("WorldView", null=True, blank=True)     # foreign key to worldview
    # RANK, VOTES
    status = models.IntegerField(default=STATUS_CREATION)
    rank = models.DecimalField(default="0.0", max_digits=4, decimal_places=2)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    commenters = models.ManyToManyField("UserProfile", related_name="commented_on_content")
    # POSTING TO GROUPS
    posted_to = models.ForeignKey("Group", null=True, related_name="posted_content")
    shared_to = models.ManyToManyField("Group", related_name="shared_content")
    content_privacy = models.CharField(max_length=1,choices=CONTENT_PRIVACY_CHOICES, default='O')
    # deprecated
    unique_commenter_ids = custom_fields.ListField(default=[])

    #-------------------------------------------------------------------------------------------------------------------
    # Gets url for viewing detail of this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getAliasURL(self):
        alias = self.alias
        if alias != "" and alias !="default":
            return '/' + alias + "/"
        else:
            return None

    def get_url(self):
        if self.type=='C':
            return self.downcast().root_content.get_url()
        elif self.type=='R':
            return self.downcast().question.get_url()
        elif self.type=='P':
            return '/petition/' + str(self.id) + '/'
        elif self.type=='N':
            return '/news/' + str(self.id) + '/'
        elif self.type=='O':
            return '/poll/' + str(self.id) + '/'
        elif self.type=='Q':
            return '/question/' + str(self.id) + '/'
        elif self.type=='D':
            return '/discussion/' + str(self.id) + '/'
        elif self.type=='E':
            return '/event/' + str(self.id) + '/'
        elif self.type=='G':
            return self.getAliasURL() or '/group/' + str(self.id) + '/'
        else:
            return self.type

    def getUrl(self):
        return self.get_url()

    def getBreakdownURL(self):
        return self.get_url() + 'breakdown/'

    def getCommentsURL(self):
        return self.get_url() + "#comments-wrapper"

    #-------------------------------------------------------------------------------------------------------------------
    # Gets name of content for display.
    #-------------------------------------------------------------------------------------------------------------------
    def getName(self):
        return self.title
    def get_name(self):
        return self.getName()
    def getTitle(self):
        return self.title
    def getTitleDisplay(self):
        return self.downcast().getTitleDisplay()

    #-------------------------------------------------------------------------------------------------------------------
    # returns group that this content was orginally posted to
    #-------------------------------------------------------------------------------------------------------------------
    def getPostedTo(self):
        from lovegov.modernpolitics.initialize import getLoveGovGroup
        posted = self.posted_to
        if not posted:
            posted = getLoveGovGroup()
        return posted

    #-------------------------------------------------------------------------------------------------------------------
    # Recalculate status for this content.
    #-------------------------------------------------------------------------------------------------------------------
    def recalculateVotes(self):
        self.status = self.upvotes - self.downvotes
        self.save()

    def contentCommentsRecalculate(self):
        direct_comments = Comment.objects.filter(on_content=self, active=True)
        num_comments = 0

        if direct_comments:
            for comment in direct_comments:

                self.commenters.add(comment.getCreator())

                num_children_comments = comment.contentCommentsRecalculate()

                num_comments += num_children_comments + 1

        self.num_comments = num_comments
        self.save()

        return num_comments


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
        img.setMainTopic(self.getMainTopic())
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

    def getImageURL(self):
        if self.main_image_id < 0:
            return self.getMainTopic().getImageURL()
        elif self.main_image:
            return self.main_image.image.url
        else:
            return self.getMainTopic().getImageURL()

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
        action = CreatedAction(user=creator,content=self,privacy=privacy)
        action.autoSave()
        self.like(user=creator, privacy=privacy)

        logger.debug("created " + self.title)

    #-------------------------------------------------------------------------------------------------------------------
    # Saves a creation relationship for this content, with inputted creator and privacy.
    #-------------------------------------------------------------------------------------------------------------------
    def saveEdited(self, privacy):
        self.privacy = privacy
        self.save()

        edited = EditedAction(user=self.creator, content=self, privacy=privacy)
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
    # Handle adding a new comment appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def addComment(self, commenter):
        self.num_comments += 1
        if commenter and (not commenter in self.commenters.all()):
            self.commenters.add(commenter)
            self.status += STATUS_COMMENT
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
        elif type == 'C':
            object = self.comment
        elif type == 'D':
            object = self.discussion
        elif type == 'Q':
            object = self.question
        elif type == 'R':
            object = self.response
        elif type == 'I':
            object = self.userimage
        elif type == 'O':
            object = self.poll
        elif type == 'G':
            object = self.group
        elif type == 'Z':
            object = self.response
        elif type == 'M':
            object = self.motion
        else: object = self
        return object

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
    def getThreadDisplayName(self, user, url=None):
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
        created = Created.objects.filter(content=self)
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
    # Gets a comparison, between inputted user and this content.
    #-------------------------------------------------------------------------------------------------------------------
    def getComparison(self, viewer):
        from lovegov.modernpolitics.backend import getUserContentComparison
        return getUserContentComparison(user=viewer, content=self)

    def getComparisonJSON(self, viewer):
        comparison = self.getComparison(viewer)
        return comparison, comparison.toJSON()

    def prepComparison(self, viewer):
        comparison, json = self.getComparisonJSON(viewer)
        self.compare = json
        self.result = comparison.result

    #-------------------------------------------------------------------------------------------------------------------
    # Add like vote to content from inputted user (or adjust his vote appropriately)
    #-------------------------------------------------------------------------------------------------------------------
    def like(self, user, privacy):
        my_vote = Voted.lg.get_or_none(user=user, content=self)

        if my_vote:
            # if already liked, do nothing
            if my_vote.value == 1:
                pass

            # if disliked or neutral, increase vote by 1
            else:
                my_vote.value += 1

                # adjust content values about status and vote
                if my_vote.value == 1:
                    self.upvotes += 1
                else:
                    self.downvotes -= 1

                self.status += STATUS_VOTE
                self.save()
                my_vote.save()

        else:
            # create new vote
            my_vote = Voted(value=1, content=self, user=user, privacy=privacy)
            my_vote.autoSave()
            # adjust content values about status and vote
            self.upvotes += 1
            self.status += STATUS_VOTE
            self.save()
            creator = self.getCreator()
            creator.upvotes += 1
            creator.save()

        # make the action and notify
        action = VotedAction(user=user,content=self,value=my_vote.value)
        action.autoSave()
        self.creator.notify(action)

        if self.type == 'M':
            self.downcast().motionVote(my_vote)

        return my_vote.value

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
                # adjust content values about status and vote
                if my_vote.value == -1:
                    self.downvotes += 1
                else:
                    self.upvotes -= 1
                self.status -= STATUS_VOTE
                self.save()
                my_vote.save()
        else:
            # create new vote
            my_vote = Voted(value=-1, content=self, user=user, privacy=privacy)
            my_vote.autoSave()
            # adjust content values about status and vote
            self.downvotes += 1
            self.status -= STATUS_VOTE
            self.save()
            creator = self.getCreator()
            creator.downvotes += 1
            creator.save()

        action = VotedAction(user=user,content=self,value=my_vote.value)
        action.autoSave()
        self.creator.notify(action)

        if self.type == 'M':
            self.downcast().motionVote(my_vote)
        return my_vote.value

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
        from lovegov.modernpolitics.initialize import getGeneralTopic
        if not self.main_topic:
            self.main_topic = getGeneralTopic()
            self.save()
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
        f_ids = UserFollow.objects.filter(content=self, confirmed=True).values_list('user', flat=True)
        followers = UserProfile.objects.filter(id__in=f_ids)
        if num != -1:
            followers = followers[:num]
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
class BasicInfo(models.Model):
    profile_image = models.ForeignKey(UserImage, null=True)
    # ENUMS
    GENDER_CHOICES = ( ('M', 'Male'), ('F', 'Female'), ('N', 'None') )
    ROLE_CHOICES = ( ('V', 'Voter'), ('E', 'Elected Official') )
    # FIELDS
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    nick_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(null=True)
    age = models.IntegerField(null=True)
    address = custom_fields.ListField(default=[])
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=15, blank=True, null=True)
    url = custom_fields.ListField(default=[])
    religion = models.CharField(max_length=200, blank=True, null=True)
    ethnicity = models.CharField(max_length=30, blank=True, null=True)
    party = models.CharField(max_length=100, blank=True, null=True)
    political_role = models.CharField(max_length=1, choices=ROLE_CHOICES, blank=True, null=True)
    invite_message = models.CharField(max_length=10000, blank=True, default="default")
    invite_subject = models.CharField(max_length=1000, blank=True, default="default")
    bio = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        abstract = True

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
    name = models.CharField(max_length=200, default="default")
    created_when = models.DateTimeField(auto_now_add=True, null=True)
    creator = models.ForeignKey("UserProfile", null=True)
    ranking = models.CharField(max_length=1, choices=RANKING_CHOICES, default="H")
    topics = models.ManyToManyField(Topic)
    types = custom_fields.ListField()                  # list of char of included types
    levels = custom_fields.ListField(default=[])                 # list of char of included levels
    groups = models.ManyToManyField("Group")
    submissions_only = models.BooleanField(default=True) # switch between just created (True) and everything they upvoted (False)
    display = models.CharField(max_length=1, default="P")
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
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    fb_image = models.ImageField(blank=True, null=True,
        upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
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

class UserProfile(FacebookProfileModel, LGModel, BasicInfo):
    type = models.CharField(max_length=1,default="U")
    # this is the primary user for this profile, mostly for fb login
    user = models.ForeignKey(User, null=True)
    created_when = models.DateTimeField(auto_now_add=True)
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
    first_login = models.IntegerField(default=0) # for special case for first login
    developer = models.BooleanField(default=False)  # for developmentWrapper
    user_title = models.CharField(max_length=200,null=True)
    # INFO
    view = models.ForeignKey("WorldView", default=initView)
    networks = models.ManyToManyField("Network", related_name='networks')
    location = models.ForeignKey(PhysicalAddress, null=True)
    # GAMIFICATION
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    num_petitions = models.IntegerField(default=0)
    num_articles = models.IntegerField(default=0)
    num_ifollow = models.IntegerField(default=0)
    num_followme = models.IntegerField(default=0)
    num_groups = models.IntegerField(default=0)
    num_signatures = models.IntegerField(default=0)
    num_answers = models.IntegerField(default=0)
    num_posts = models.IntegerField(default=0)
    # old address
    userAddress = models.ForeignKey(UserPhysicalAddress, null=True)
    # CONTENT LISTS
    last_answered = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now, blank=True)     # last time answer question
    i_follow = models.ForeignKey('Group', null=True, related_name='i_follow')
    follow_me = models.ForeignKey('Group', null=True, related_name='follow_me')
    private_follow = models.BooleanField(default=False)
    my_involvement = models.ManyToManyField(Involved)       # deprecated
    my_history = models.ManyToManyField(Content, related_name = 'history')   # everything I have viewed
    privileges = models.ManyToManyField(Content, related_name = 'priv')     # for custom privacy these are the content I am allowed to see
    last_page_access = models.IntegerField(default=-1, null=True)       # foreign key to page access
    parties = models.ManyToManyField("Party", related_name='parties')
    # my groups and feeds
    group_subscriptions = models.ManyToManyField("Group")
    # SETTINGS
    user_notification_setting = custom_fields.ListField()               # list of allowed types
    content_notification_setting = custom_fields.ListField()            # list of allowed types
    email_notification_setting = custom_fields.ListField()              # list of allowed types
    custom_notification_settings = models.ManyToManyField(CustomNotificationSetting)
    ghost = models.BooleanField(default=False)
    # Government Stuff
    political_title = models.CharField(max_length=100, default="Citizen")
    primary_role = models.ForeignKey("OfficeHeld", null=True)
    politician = models.BooleanField(default=False)
    elected_official = models.BooleanField(default=False)
    currently_in_office = models.BooleanField(default=False)
    supporters = models.ManyToManyField('UserProfile', related_name='supportees')
    num_supporters = models.IntegerField(default=0)
    num_messages = models.IntegerField(default=0)
    govtrack_id = models.IntegerField(default=-1)
    political_statement = models.TextField(null=True)
    # anon ids
    anonymous = models.ManyToManyField(AnonID)
    # deprecated
    my_feed = models.ManyToManyField(FeedItem, related_name="newfeed")  # for storing feed based on my custom setting below
    filter_setting = models.ForeignKey(FilterSetting, null=True)
    evolve = models.BooleanField(default=False)     # boolean as to whether their filter setting should learn from them and evolve

    def __unicode__(self):
        return self.first_name
    def get_url(self):
        if self.alias!='' and self.alias!='default':
            return '/' + self.alias + '/'
        else:
            return '/profile/' + str(self.id) + '/'
    def getQuestionsURL(self):
        return self.get_url() + 'worldview/'

    def getWebUrl(self):
        return self.getWebURL()
    def getWebURL(self):
        return '/profile/web/' + self.alias + '/'
    def getAlphaURL(self):
        return self.get_url()
    def get_name(self):
        try:
            to_return = (self.first_name + " " + self.last_name)
            if self.alias == 'anonymous':
                try:
                    if self.you:
                        to_return += "(You)"
                except:
                    pass
        except UnicodeEncodeError:
            to_return = "UnicodeEncodeError"
        return to_return
    def get_nameShort(self, max_length=15):
        try:
            fullname = str(self.first_name) + " " + str(self.last_name)
            if len(fullname) > max_length:
                to_return = unicode(str(self.first_name)).encode("UTF-8")
                if len(to_return) > max_length:
                    to_return = to_return[:max_length-3] + "..."
            else:
                to_return = unicode(str(self.first_name) + " " + str(self.last_name)).encode("UTF-8")
        except UnicodeEncodeError:
            to_return = "UnicodeEncodeError"
        return to_return

    def get_email(self):
        return self.username

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def isDeveloper(self):
        return self.developer

    def get_address(self):
        if self.location: return self.location.address_string
        else: return ""

    def setZipCode(self, zip):
        location = self.location
        if not location:
            location = PhysicalAddress()
            location.save()
            self.location = location
            self.save()
        location.zip = zip
        location.save()

    def setDOB(self, dob):
        self.dob = dob
        age = datetime.date.today() - dob
        years = age.days / 365
        self.age = years
        self.save()

    def isAnon(self):
        return self.alias == 'anonymous'

    def isSuperHero(self):
        return self.alias in SUPER_HEROES

    def isNormal(self):
        return not (self.politician or self.elected_official)

    def clearResponses(self):
        return self.getView().clearResponses()

    #-------------------------------------------------------------------------------------------------------------------
    # automatically parse city and state groups
    #-------------------------------------------------------------------------------------------------------------------
    def joinTownGroup(self, city, state):
        if city:
            already = TownGroup.lg.get_or_none(location__city=city, location__state=state)
            if already:
                if not self in already.members.all():
                    already.joinMember(self)
            else:
                city_group = TownGroup().autoCreate(city, state)
                city_group.joinMember(self)

    def joinStateGroup(self, state):
        if state:
            already = StateGroup.lg.get_or_none(location__state=state)
            if already:
                if not self in already.members.all():
                    already.joinMember(self)

    def joinLocationGroups(self):
        if self.location:
            self.joinTownGroup(self.location.city, self.location.state)
            self.joinStateGroup(self.location.state)

    #-------------------------------------------------------------------------------------------------------------------
    # returns the number of separate sessions a user has had.
    #-------------------------------------------------------------------------------------------------------------------
    def getNumSessions(self):
        pa = PageAccess.objects.filter(user=self).order_by("when")
        sessions = 0
        if pa:
            sessions = 1
            last=pa[0].when
            for x in pa:
                delta = x.when - last
                if delta.total_seconds() > (60*60):
                    sessions += 1
                last = x.when
        return sessions

    #-------------------------------------------------------------------------------------------------------------------
    # returns all content this user has created in public mode
    #-------------------------------------------------------------------------------------------------------------------
    def getContent(self):
        return Content.objects.filter(in_feed=True, creator=self, privacy="PUB")

    #-------------------------------------------------------------------------------------------------------------------
    # gets string represetning parties of user
    #-------------------------------------------------------------------------------------------------------------------
    def getPartiesString(self):
        parties = self.parties.all()
        if not parties:
            to_return = "None"
        else:
            to_return = ""
            for x in parties:
                to_return += x.title + " "
        return to_return

    #-------------------------------------------------------------------------------------------------------------------
    # Gets users location object
    #-------------------------------------------------------------------------------------------------------------------
    def getLocation(self):
        if self.location:
            return self.location
        else:
            return self.newLocation()

    def newLocation(self):
        location = PhysicalAddress()
        location.save()
        self.location = location
        self.save()
        return location

    #-------------------------------------------------------------------------------------------------------------------
    # Gets a comparison, between inputted user and this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getComparison(self, viewer):
        from lovegov.modernpolitics.compare import getUserUserComparison
        return getUserUserComparison(userA=viewer, userB=self)

    def getComparisonJSON(self, viewer):
        comparison = self.getComparison(viewer)
        return comparison, comparison.toJSON(viewB_url=self.getWebURL())

    def prepComparison(self, viewer):
        comparison, json = self.getComparisonJSON(viewer)
        self.compare = json
        self.result = comparison.result

    #-------------------------------------------------------------------------------------------------------------------
    # Makes unique alias from name
    #-------------------------------------------------------------------------------------------------------------------
    def makeAlias(self):
        alias = self.first_name.replace(" ","") + self.last_name
        if type(alias) == unicode:
            alias = alias.encode('utf-8','ignore')
        alias = str.lower(alias)
        from lovegov.modernpolitics.helpers import genAliasSlug
        self.alias = genAliasSlug(alias)
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
    # create default fillter
    #-------------------------------------------------------------------------------------------------------------------
    def createDefaultFilter(self):
        filter = SimpleFilter(creator=self, ranking="N")
        filter.save()
        self.my_filters.add(filter)

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
    # Gets profile image for this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getProfileImage(self):
        from modernpolitics.backend import getDefaultImage
        if self.profile_image:
            return self.profile_image
        else:
            return getDefaultImage()

    def getProfileImageURL(self):
        if self.profile_image:
            return self.profile_image.image.url
        else:
            return DEFAULT_PROFILE_IMAGE_URL

    def getImage(self):
        return self.getProfileImage().image

    def getImageURL(self):
        return self.getProfileImageURL()

    def userPetitionsRecalculate(self):
        self.num_petitions = Created.objects.filter(user=self,content__type="P").count()
        self.save()

    def userNewsRecalculate(self):
        self.num_articles = Created.objects.filter(user=self,content__type="N").count()
        self.save()

    def userCommentsRecalculate(self):
        self.num_comments = Created.objects.filter(user=self,content__type="C").count()
        self.save()

    def userStatsRecalculate(self):
        self.userPetitionsRecalculate()
        self.userNewsRecalculate()
        self.userCommentsRecalculate()

    def getSupporters(self):
        support = Supported.objects.filter(user=self, confirmed=True)
        supporter_ids = support.values_list('to_user', flat=True)
        return UserProfile.objects.filter(id__in=supporter_ids)

    def support(self, politician):
        supported = Supported.lg.get_or_none(user=self, to_user=politician)
        if not supported:
            supported = Supported(user=self, to_user=politician)
            supported.autoSave()
            politician.num_supporters += 1
            politician.save()
        if not supported.confirmed:
            supported.confirmed = True
            supported.save()
            politician.num_supporters += 1
            politician.save()

    def unsupport(self, politician):
        supported = Supported.lg.get_or_none(user=self, to_user=politician)
        if supported and supported.confirmed:
            supported.confirmed = False
            supported.save()
            politician.num_supporters -= 1
            politician.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Fills in fields based on facebook data
    #-------------------------------------------------------------------------------------------------------------------
    def refreshFB(self, fb_data):
        self.facebook_id = fb_data['id']
        self.facebook_profile_url = fb_data['link']
        # self.gender = fb_data['gender']
        self.confirmed = True


        if 'birthday' in fb_data:
            split_bday = fb_data['birthday'].split('/')
            birthday = datetime.date.min

            month = int(split_bday[0])
            day = int(split_bday[1])
            year = int(split_bday[2])

            if 0 < month < 13:
                birthday = birthday.replace(month=month)
            if 0 < day < 32:
                birthday = birthday.replace(day=day)
            if 0 < year < 10000:
                birthday = birthday.replace(year=year)

            self.dob = birthday
            self.save()


        if 'education' in fb_data:
            education = fb_data['education']
            for edu in education:
                school = edu['school']
                name = school['name']
                alias = name.replace(" ","")
                alias = alias.replace(",","")
                alias = alias.replace(".","")
                alias = alias.lower()
                school_network = Network.lg.get_or_none(alias=alias,network_type='S')
                if not school_network:
                    school_network = Network(alias=alias,title=name,network_type='S')
                    school_network.autoSave()
                school_network.joinMember(self)
                self.networks.add(school_network)

        if 'location' in fb_data:
            location = fb_data['location']
            name = location['name']
            alias = name.replace(" ","")
            alias = alias.replace(",","")
            alias = alias.replace(".","")
            alias = alias.lower()
            location_network = Network.lg.get_or_none(alias=alias,network_type='L')
            if not location_network:
                location_network = Network(alias=alias,title=name,network_type='L')
                location_network.autoSave()
            location_network.joinMember(self)
            self.networks.add(location_network)


        self.setUsername(fb_data['email'])

    #-------------------------------------------------------------------------------------------------------------------
    # Gets worldview for user.
    #-------------------------------------------------------------------------------------------------------------------
    def getView(self):
        if self.view_id and self.view_id != -1:
            return self.view
        else:
            view = WorldView()
            view.save()
            self.view = view
            self.save()
            return self.view

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
        self.i_follow.joinMember(to_user)

        if not to_user.follow_me:
            to_user.createFollowMeGroup()
        to_user.follow_me.joinMember(self)

        #Check and Make Relationship A
        if not relationship:
            relationship = UserFollow( user=self , to_user=to_user , confirmed=True, fb=fb )
            relationship.autoSave()
            self.num_ifollow += 1
            self.save()
            to_user.num_followme += 1
            to_user.save()
        else:
            if not relationship.confirmed:
                self.num_ifollow += 1
                self.save()
                to_user.num_followme += 1
                to_user.save()
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
            if relationship.confirmed:
                self.num_ifollow -= 1
                self.save()
                to_user.num_followme -= 1
                to_user.save()
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
        image = self.profile_image
        if image:
            image.createImage(File(file))
        else:
            img = UserImage(title=title, summary=summary)
            img.createImage(File(file))
            img.autoSave(creator=self, privacy='PUB')
            self.profile_image = img
            self.save()



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
    def notify(self, action):
        type = action.action_type

        #If you are the one doing the action, do not notify yourself
        if action.user.id == self.id:
            return False

        #Do aggregate notifications if necessary
        if type in AGGREGATE_NOTIFY_TYPES:
            # IF the action does not have modifiers or this modifier is notifiable
            if type not in NOTIFY_MODIFIERS:

                stale_date = datetime.datetime.today() - STALE_TIME_DELTA
                # Find all recent notifications with this action type/modifier directed towards this user
                already = Notification.objects.filter(notify_user=self,
                                                        when__gte=stale_date,
                                                        action__action_type=type ).order_by('-when')

                for notification in already: # For all recent notifications matching this one
                    if notification.action.getTo().id == action.getTo().id: # If these actions target the same content
                        # Update Notification with this action
                        notification.when = datetime.datetime.today()
                        notification.addAggAction( action )
                        return True

                notification = Notification(action=action, notify_user=self)
                notification.save()
                notification.addAggAction( action )
                return True

        #Otherwise do normal notifications
        elif type in NOTIFY_TYPES:
            modifier = action.getModifier()
            # IF the action does not have modifiers or this modifier is notifiable
            if type not in NOTIFY_MODIFIERS or (modifier and modifier in NOTIFY_MODIFIERS[type]):
                notification = Notification(action=action, notify_user=self)
                notification.save()
                return True

        return False

    #-------------------------------------------------------------------------------------------------------------------
    # Creates system group for that persons connections.
    #-------------------------------------------------------------------------------------------------------------------
    def createIFollowGroup(self):
        if not Group.lg.get_or_none(id=self.i_follow_id):
            title = "People who " + self.get_name() + " follows"
            group = Group(title=title, full_text="Group of people who "+self.get_name()+" is following.", group_privacy='S', system=True, in_search=False, in_feed=False)
            group.system = True
            group.hidden = True
            group.subscribable = False
            group.content_by_posting = False
            group.autoSave()
            self.i_follow = group
            self.save()
        return self.i_follow

    #-------------------------------------------------------------------------------------------------------------------
    # Creates system group for that persons connections.
    #-------------------------------------------------------------------------------------------------------------------
    def createFollowMeGroup(self):
        if not Group.lg.get_or_none(id=self.follow_me_id):
            title = "People who follow " + self.get_name()
            group = Group(title=title, full_text="Group of people who are following "+self.get_name(), group_privacy='S', in_search=False, in_feed=False)
            group.system = True
            group.hidden = True
            group.subscribable = False
            group.content_by_posting = False
            group.autoSave()
            self.follow_me = group
            self.save()
        return self.follow_me

    #-------------------------------------------------------------------------------------------------------------------
    # Adds user to lovegov group.
    #-------------------------------------------------------------------------------------------------------------------
    def joinLoveGovGroup(self):
        from modernpolitics.backend import getLoveGovGroup
        lovegov = getLoveGovGroup()
        lovegov.joinMember(self)

    #-------------------------------------------------------------------------------------------------------------------
    # Clears m2m and deletes tuples
    #-------------------------------------------------------------------------------------------------------------------
    def smartClearMyFeed(self):
        self.my_feed.all().delete()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all notifications.
    #-------------------------------------------------------------------------------------------------------------------
    def getNotifications(self, start=0, num=-1, new=False, old=False):
        if new:
            notifications = Notification.objects.filter(notify_user=self, viewed=False).order_by('-when')
        elif old:
            notifications = Notification.objects.filter(notify_user=self, viewed=True).order_by('-when')
        else:
            notifications = Notification.objects.filter(notify_user=self).order_by('-when')
        if num != -1:
            notifications = notifications[start:start+num]
        return notifications

    def getNumNewNotifications(self):
        return len( Notification.objects.filter(notify_user=self, viewed=False) )

    def getAllNotifications(self):
        return Notification.objects.filter(notify_user=self).order_by('-when')

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a users recent activity.
    #-------------------------------------------------------------------------------------------------------------------
    def getActivity(self, start=0, num=-1):
        actions = self.actions.all().order_by('-when')
        if num != -1:
            actions = actions[start:start+num]
        return actions

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowRequests(self, num=-1):
        if num == -1:
            return UserFollow.objects.filter( to_user=self, confirmed=False, requested=True, rejected=False ).order_by('-when')
        else:
            return UserFollow.objects.filter( to_user=self, confirmed=False, requested=True, rejected=False ).order_by('-when')[:num]


    def getNumFollowRequests(self):
        return UserFollow.objects.filter( to_user=self, confirmed=False, requested=True, rejected=False ).count()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getGroupInvites(self, num=-1):
        if num == -1:
            return GroupJoined.objects.filter( user=self, confirmed=False, invited=True, declined=False ).order_by('-when')
        else:
            return GroupJoined.objects.filter( user=self, confirmed=False, invited=True, declined=False ).order_by('-when')[:num]

    def getNumGroupInvites(self):
        return GroupJoined.objects.filter( user=self, confirmed=False, invited=True, declined=False ).count()

    #-------------------------------------------------------------------------------------------------------------------
    # return a query set of groups and networks user is in
    #-------------------------------------------------------------------------------------------------------------------
    def getGroups(self):
        g_ids = GroupJoined.objects.filter(user=self, confirmed=True).values_list('group', flat=True)
        return Group.objects.filter(id__in=g_ids)

    # get groups that non-ghost groups
    def getRealGroups(self):
        return self.getGroups().filter(hidden=False)

    def getUserGroups(self, num=-1, start=0):
        if num == -1:
            return self.getGroups().filter(group_type='U',system=False)[start:]
        else:
            return self.getGroups().filter(group_type='U',system=False)[start:start+num]

    def getNetworks(self):
        return self.networks.all()

    def getGroupSubscriptions(self):
        return self.group_subscriptions.all()

    def getPoliticians(self):
        supported = Supported.objects.filter(confirmed=True, user=self)
        politician_ids = supported.values_list("to_user", flat=True)
        return UserProfile.objects.filter(id__in=politician_ids)

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Users who are (confirmed) following this user.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowMe(self, num=-1):
        f_ids = UserFollow.objects.filter(to_user=self, confirmed=True ).values_list('user', flat=True)
        followers = UserProfile.objects.filter(id__in=f_ids)
        if num != -1:
            followers = followers[:num]
        return followers

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a list of all Users who this user is (confirmed) following.
    #-------------------------------------------------------------------------------------------------------------------
    def getIFollow(self, num=-1):
        f_ids = UserFollow.objects.filter(user=self, confirmed=True ).values_list('to_user', flat=True)
        followers = UserProfile.objects.filter(id__in=f_ids)
        if num != -1:
            followers = followers[:num]
        return followers

    #-------------------------------------------------------------------------------------------------------------------
    # Refreshes the users follow groups
    #-------------------------------------------------------------------------------------------------------------------
    def userFollowRecalculate(self):
        following = self.getIFollow()
        followers = self.getFollowMe()
        for follow in following:
            self.follow(follow)
        for follower in followers:
            follower.follow(self)

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
        if self.first_login == 0:
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------------------------------
    # Gets the users responses to questions in a list of  (question, response) tuples
    #-----------------------------------------------------------------------------------------------------------------------
    def getUserResponses(self):
        qr = []

        responses = list( self.view.responses.all() )

        official_questions = list( Question.objects.filter(official=True) )

        for r in responses:
            q = r.question
            if q.official:
                qr.append((q,r))
                if q in official_questions:
                    official_questions.remove(q)

        for q in official_questions:
            qr.append((q,None))

        return qr


    def setAddress(self, newAddress):
        self.userAddress.currentAddress = False
        self.userAddress.save()
        newAddress.currentAddress = True
        self.userAddress = newAddress
        self.save()


#    def getSupporters(self):
#        support = Supported.objects.filter(user=self, confirmed=True)
#        supporter_ids = support.values_list('to_user', flat=True)
#        return UserProfile.objects.filter(id__in=supporter_ids)

    def addSupporter(self, user):
        supported = Supported.lg.get_or_none(user=user, to_user=self)
        if not supported:
            supported = Supported(user=user, to_user=self)
            supported.confirmed()
            supported.autoSave()
            supporters.add(user)
            self.num_supporters += 1
            self.save()
        if not supported.confirmed:
            supported.confirmed = True
            supported.save()
            self.num_supporters += 1
            self.save()

    def removeSupporter(self, user):
        supported = Supported.lg.get_or_none(user=user, to_user=self)
        if supported and supported.confirmed:
            supported.confirmed = False
            supported.save()
            self.num_supporters -= 1
            self.save()
        if user in supporters:
            supporters.remove(user)

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
    prohibited_actions = custom_fields.ListField(default=DEFAULT_PROHIBITED_ACTIONS)
    def getUserProfile(self):
        return self.user_profile

#=======================================================================================================================
# Keeps track of user activity.
#=======================================================================================================================
class Action(Privacy):
    user = models.ForeignKey(UserProfile,related_name="actions")
    action_type = models.CharField(max_length=2, choices=ACTION_CHOICES)
    when = models.DateTimeField(auto_now_add=True)
    #must_notify = models.BooleanField(default=False)        # to override check for permission to notify

    def autoSave(self):
        self.creator = self.user
        self.save()

    def getTo(self):
        action = self.downcast()
        if action:
            return action.getTo()
        return None

    def downcast(self):
        action_type = self.action_type
        if action_type == 'VO':
            object = self.votedaction
        elif action_type== 'JO':
            object = self.groupjoinedaction
        elif action_type == 'FO':
            object = self.userfollowaction
        elif action_type == 'SI':
            object = self.signedaction
        elif action_type == 'CR':
            object = self.createdaction
        elif action_type == 'ED':
            object = self.editedaction
        elif action_type == 'SH':
            object = self.sharedaction
        elif action_type == 'XX':
            object = self.deletedaction
        elif action_type == 'SU':
            object = self.supportedaction
        elif action_type == 'AS':
            object = self.askedaction
        elif action_type == 'ME':
            object = self.messagedaction
        elif action_type == 'GF':
            object = self.groupfollowaction
        else:
            object = None
        return object

    def getVerbose(self,viewer=None,vals={}):
        action = self.downcast()
        if action:
            return action.getVerbose(viewer,vals)
        return ''

    def getModifier(self):
        return None


#=======================================================================================================================
# Signing a petition action
#=======================================================================================================================
class SignedAction(Action):
    petition = models.ForeignKey('Petition')

    def autoSave(self):
        self.action_type = 'SI'
        super(SignedAction,self).autoSave()

    def getTo(self):
        return self.petition

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.petition
        })

        return render_to_string('site/pieces/actions/signed_verbose.html',vals)

#=======================================================================================================================
# Following or unfollowing a group, aka adding or removing from group subscriptions
#=======================================================================================================================
class GroupFollowAction(Action):
    group = models.ForeignKey("Group")
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS)

    def getModifier(self):
        return self.modifier

    def getTo(self):
        return self.group

    def autoSave(self):
        self.action_type = 'GF'
        self.privacy = "PRI"
        super(GroupFollowAction,self).autoSave()

    def getTo(self):
        return self.group

    def getVerbose(self,viewer=None,vals={}):
        return None


#=======================================================================================================================
# Message a politician
#=======================================================================================================================
class MessagedAction(Action):
    politician = models.ForeignKey(UserProfile)
    message = models.TextField()

    def autoSave(self):
        self.action_type = 'ME'
        politician = self.politician
        politician.num_messages += 1
        politician.save()
        super(MessagedAction,self).autoSave()
        print "sent " + self.politician.get_name() + " an email with message!"

    def getTo(self):
        return self.politician

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.politician
        })

        return render_to_string('site/pieces/actions/messaged_verbose.html',vals)

#=======================================================================================================================
# Asking a politician to join lovegov.
#=======================================================================================================================
class AskedAction(Action):
    politician = models.ForeignKey(UserProfile)

    def autoSave(self):
        self.action_type = 'AS'
        print "sent an email to " + self.politician.get_name() + " !"
        super(AskedAction,self).autoSave()

    def getTo(self):
        return self.politician

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.politician
        })

        return render_to_string('site/pieces/actions/asked_verbose.html',vals)

class ClaimProfile(LGModel):
    user = models.ForeignKey(UserProfile, related_name="claims")
    politician = models.ForeignKey(UserProfile, related_name="claimers")
    email = models.CharField(max_length=200)
    def autoSave(self):
        print "sent us an email telling about claim"
        self.save()

#=======================================================================================================================
# Creating some content action
#=======================================================================================================================
class CreatedAction(Action):
    content = models.ForeignKey(Content)

    def autoSave(self):
        self.action_type = 'CR'
        super(CreatedAction,self).autoSave()

    def getTo(self):
        return self.content

    def getVerbose(self,viewer=None,vals={}):

        you_acted = (viewer.id == self.user.id)

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.content
        })

        return render_to_string('site/pieces/actions/created_verbose.html',vals)


#=======================================================================================================================
# Editing some content action
#=======================================================================================================================
class EditedAction(Action):
    content = models.ForeignKey(Content)

    def getTo(self):
        return self.content

    def autoSave(self):
        self.action_type = 'ED'
        super(EditedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.content
        })

        return render_to_string('site/pieces/actions/edited_verbose.html',vals)


#=======================================================================================================================
# Sharing some content with a user or group action
#=======================================================================================================================
class SharedAction(Action):
    content = models.ForeignKey(Content)
    to_user = models.ForeignKey(UserProfile,null=True)
    to_group = models.ForeignKey('Group',null=True,related_name="shared_to_actions")

    def getTo(self):
        return self.content

    def autoSave(self):
        self.action_type = 'SH'
        super(SharedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        to_object = None
        to_you = False

        if to_user:
            to_object = to_user
            if to_user.id == viewer.id:
                to_you = True

        elif to_group:
            to_object = to_group

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'shared_object' : self.content,
            'to_object' : to_object,
            'to_you' : to_you
        })

        return render_to_string('site/pieces/actions/shared_verbose.html',vals)


#=======================================================================================================================
# Deleting some content action
#=======================================================================================================================
class DeletedAction(Action):
    content = models.ForeignKey(Content)

    def getTo(self):
        return self.content

    def autoSave(self):
        self.action_type = 'XX'
        super(DeletedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.content
        })

        return render_to_string('site/pieces/actions/deleted_verbose.html',vals)

#=======================================================================================================================
# Some action that changes a UserFollow relationship
#=======================================================================================================================
class UserFollowAction(Action):
    user_follow = models.ForeignKey('UserFollow', related_name="follow_actions")
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS)

    def getModifier(self):
        return self.modifier

    def getTo(self):
        return self.user_follow

    def autoSave(self):
        self.action_type = 'FO'
        super(UserFollowAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        user_follow = self.user_follow
        from_you = False
        to_you = False

        from_user = user_follow.user
        to_user = user_follow.to_user

        if from_user.id == viewer.id:
            from_you = True
        elif to_user.id == viewer.id:
            to_you = True

        vals.update({
            'user' : self.user,
            'timestamp' : self.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'to_you' : to_you,
            'to_user' : to_user,
            'from_user' : from_user,
            'modifier' : self.modifier
        })

        return render_to_string('site/pieces/actions/user_follow_verbose.html',vals)

#=======================================================================================================================
# Some action that changes a politician supported relationship
#=======================================================================================================================
class SupportedAction(Action):
    support = models.ForeignKey('Supported', related_name="support_actions")
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS)

    def getModifier(self):
        return self.modifier

    def getTo(self):
        return self.support

    def autoSave(self):
        self.action_type = 'SU'
        super(SupportedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        support = self.support
        from_you = False
        to_you = False

        from_user = support.user
        to_user = support.to_user

        if from_user.id == viewer.id:
            from_you = True
        elif to_user.id == viewer.id:
            to_you = True

        vals.update({
            'user' : self.user,
            'timestamp' : self.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'to_you' : to_you,
            'to_user' : to_user,
            'from_user' : from_user,
            'modifier' : self.modifier
        })

        return render_to_string('site/pieces/actions/support_verbose.html',vals)

#=======================================================================================================================
# Some action that changes a GroupJoined relationship
#=======================================================================================================================
class GroupJoinedAction(Action):
    group_joined = models.ForeignKey('GroupJoined', related_name="joined_actions" )
    modifier = models.CharField(max_length=1, choices=ACTION_MODIFIERS)

    def getModifier(self):
        return self.modifier

    def getTo(self):
        return self.group_joined

    def autoSave(self):
        self.action_type = 'JO'
        super(GroupJoinedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        group_joined = self.group_joined

        from_you = False
        if group_joined.user.id == viewer.id:
            from_you = True

        inviter = group_joined.getInviter()
        you_invited = False
        if inviter and inviter.id == viewer.id:
            you_invited = True

        vals.update({
            'user' : self.user,
            'timestamp' : self.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'you_invited' : you_invited,
            'group' : group_joined.group,
            'inviter' : inviter,
            'from_user' : group_joined.user,
            'modifier' : self.modifier
        })

        return render_to_string('site/pieces/actions/group_joined_verbose.html',vals)


#=======================================================================================================================
# Some action that changes a voted relationship
#=======================================================================================================================
class VotedAction(Action):
    content = models.ForeignKey(Content)
    value = models.IntegerField(default=0)

    def getTo(self):
        return self.content

    def autoSave(self):
        self.action_type = 'VO'
        super(VotedAction,self).autoSave()

    def getVerbose(self,viewer=None,vals={}):
        you_acted = False
        if viewer.id == self.user.id:
            you_acted = True

        vals.update({
            'timestamp' : self.when,
            'user' : self.user,
            'you_acted' : you_acted,
            'to_object' : self.content,
            'value' : self.value
        })

        return render_to_string('site/pieces/actions/voted_verbose.html',vals)


#=======================================================================================================================
# Notifying a user of something important to them. privacy is in case they ought not be able to see who
#=======================================================================================================================
class Notification(Privacy):
    notify_user = models.ForeignKey(UserProfile, related_name="notifications")
    action = models.ForeignKey(Action , related_name="notifications") ## For Aggregate Notifications :: most recent action
    viewed = models.BooleanField(default=False)
    when = models.DateTimeField(auto_now_add=True)
    # for aggregating notifications like facebook
    agg_actions = models.ManyToManyField(Action , related_name="agg_notifications")

    def addAggAction(self,action):
        self.agg_actions.add(action)
        if action.privacy == "PUB":
            self.action = action
        self.viewed = False
        self.save()


    ## Notificaitons Verbose Switch ##
    def getVerbose(self,viewer,vals={}):
        self.viewed = True
        self.save()

        type = self.action.action_type

        if type == 'VO':
            return self.getVotedVerbose(viewer,vals)
        elif type== 'JO':
            return self.getGroupJoinedVerbose(viewer,vals)
        elif type == 'FO':
            return self.getUserFollowVerbose(viewer,vals)
        elif type == 'SI':
            return self.getSignedVerbose(viewer,vals)
        elif type == 'SH':
            return self.getSharedVerbose(viewer,vals)
        elif type == 'SU':
            return self.getSupportedVerbose(viewer, vals)
        else:
            return ''

    ## Voted Notification Verbose ##
    def getVotedVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        vals.update({
            'timestamp' : action.when,
            'user' : action_user,
            'you_acted' : you_acted,
            'to_object' : action.content,
            'value' : action.value,
            'tally' : action.agg_actions.count()
        })

        return render_to_string('site/pieces/notifications/voted_verbose.html',vals)

    ## Signed Notification Verbose ##
    def getSignedVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        vals.update({
            'timestamp' : action.when,
            'user' : action_user,
            'you_acted' : you_acted,
            'to_object' : action.content,
            'tally' : action.agg_actions.count()
        })

        return render_to_string('site/pieces/notifications/signed_verbose.html',vals)

    ## Created Notification Verbose ## NOTE: This is primarily for comment notifications
    def getCreatedVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        vals.update({
            'timestamp' : action.when,
            'user' : action_user,
            'you_acted' : you_acted,
            'to_object' : action.content,
            'tally' : action.agg_actions.count()
        })

        return render_to_string('site/pieces/notifications/created_verbose.html',vals)

    ## Shared Notification Verbose ##
    def getSharedVerbose(self,viewer=None,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        to_object = None
        to_you = False

        if to_user:
            to_object = to_user
            if to_user.id == viewer.id:
                to_you = True

        elif to_group:
            to_object = to_group

        vals.update({
            'timestamp' : action.when,
            'user' : action_user,
            'you_acted' : you_acted,
            'shared_object' : action.content,
            'to_object' : to_object,
            'to_you' : to_you,
            'tally' : action.agg_actions.count()
        })

        return render_to_string('site/pieces/notifications/shared_verbose.html',vals)

    ## Group Joined Notification Verbose ##
    def getGroupJoinedVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        group_joined = action.group_joined

        from_you = False
        if group_joined.user.id == viewer.id:
            from_you = True

        inviter = group_joined.getInviter()
        you_invited = False
        if inviter and inviter.id == viewer.id:
            you_invited = True

        vals.update({
            'user' : action_user,
            'timestamp' : action.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'you_invited' : you_invited,
            'group' : group_joined.group,
            'inviter' : inviter,
            'from_user' : group_joined.user,
            'modifier' : action.modifier,
            'group_join' : group_joined
        })

        return render_to_string('site/pieces/notifications/group_joined_verbose.html',vals)

    ## User Follow Notification Verbose ##
    def getUserFollowVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        user_follow = action.user_follow

        from_user = user_follow.user
        to_user = user_follow.to_user
        from_you = False
        to_you = False

        if from_user.id == viewer.id:
            from_you = True
        elif to_user.id == viewer.id:
            to_you = True

        reverse_follow = UserFollow.lg.get_or_none(user=to_user,to_user=from_user)

        vals.update({
            'user' : action_user,
            'timestamp' : action.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'to_you' : to_you,
            'to_user' : to_user,
            'from_user' : from_user,
            'modifier' : action.modifier,
            'follow' : user_follow,
            'reverse_follow' : reverse_follow
        })

        return render_to_string('site/pieces/notifications/user_follow_verbose.html',vals)

    ## Supported verbose ##
    def getSupportedVerbose(self,viewer,vals={}):
        action = self.action.downcast()
        action_user = self.action.user

        you_acted = False
        if viewer.id == action_user.id:
            you_acted = True

        support_relationship = action.support

        from_user = support_relationship.user
        to_user = support_relationship.to_user
        from_you = False
        to_you = False

        if from_user.id == viewer.id:
            from_you = True
        elif to_user.id == viewer.id:
            to_you = True

        vals.update({
            'user' : action_user,
            'timestamp' : action.when,
            'viewer' : viewer,
            'you_acted' : you_acted,
            'from_you' : from_you,
            'to_you' : to_you,
            'to_user' : to_user,
            'from_user' : from_user,
            'modifier' : action.modifier,
            'support' : support_relationship,
        })

        return render_to_string('site/pieces/notifications/support_verbose.html',vals)

########################################################################################################################
############ POLITICAL_ROLE ############################################################################################
class Office(Content):
    tags = models.ManyToManyField("OfficeTag",related_name='tag_offices')
    # optimization
    governmental = models.BooleanField(default=False)
    representative = models.BooleanField(default=False)
    senator = models.BooleanField(default=False)

    def autoSave(self,creator=None,privacy='PUB'):
        self.type = "O"
        self.in_search = True
        super(Office,self).autoSave(creator,privacy)

    def setBooleans(self):
        rep_tag = OfficeTag.objects.get(name="representative")
        if rep_tag in self.tags.all():
            self.representative=True
            self.save()
        sen_tag = OfficeTag.objects.get(name="senator")
        if sen_tag in self.tags.all():
            self.senator = True
            self.save()
        congress_tag = OfficeTag.objects.get(name="congress")
        if congress_tag in self.tags.all():
            self.governmental = True
            self.save()


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
    current = models.IntegerField(default=0)
    goal = models.IntegerField(default=10)
    p_level = models.IntegerField(default=1)

    def getTitleDisplay(self):
        return "Petition: " + self.title

    def getFilledPercent(self):
        return int(100*(self.current / float(self.goal)))

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

                signed = Signed(user=user, content=self)
                signed.autoSave()
                action = SignedAction(petition=self,user=user)
                action.autoSave()
                self.getCreator().notify(action)

                self.current += 1
                if self.current >= self.goal:
                    self.p_level += 1
                    self.goal = PETITION_LEVELS[self.p_level]
                self.save()

                user.num_signatures += 1
                user.save()

                return True
        else:
            return False

    #-------------------------------------------------------------------------------------------------------------------
    # Finalize petition for signing.
    #-------------------------------------------------------------------------------------------------------------------
    def finalize(self):
        self.finalized = True
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Return percentages for petition bar.
    #-------------------------------------------------------------------------------------------------------------------
    def getCompletionPercent(self):
        val = float(self.current) / self.goal
        return int(val*100)

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

    #-------------------------------------------------------------------------------------------------------------------
    # Override getImageURL function to use default petition image
    #-------------------------------------------------------------------------------------------------------------------
    def getImageURL(self):
        if self.main_image_id < 0:
            return DEFAULT_PETITION_IMAGE_URL
        elif self.main_image:
            return self.main_image.image.url
        else:
            return DEFAULT_PETITION_IMAGE_URL

#=======================================================================================================================
# News
#
#=======================================================================================================================
class News(Content):
    link = models.URLField()
    link_summary = models.TextField(default="")
    link_screenshot = models.ImageField(upload_to='screenshots/')

    def getTitleDisplay(self):
        return "News: " + self.title

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

    def getImageURL(self):
        if self.link_screenshot:
            return self.link_screenshot.url
        else:
            return DEFAULT_NEWS_IMAGE_URL

    # takes in a lovegov.com url and saves image file from that location
    def saveScreenShot(self, ref):
        from lovegov.modernpolitics.helpers import photoKey
        relativePath = ref.replace(settings.MEDIA_URL, settings.MEDIA_ROOT, 1)
        file = open(relativePath)
        self.link_screenshot.save(photoKey(".png"), File(file))
        self.save()

#=======================================================================================================================
# UserPost/Discussion
#
#=======================================================================================================================
class Discussion(Content):
    user_post = models.TextField(blank=True)
    def autoSave(self, creator=None, privacy="PUB"):
        self.in_feed = True
        self.type = "D"
        super(Discussion, self).autoSave(creator=creator, privacy=privacy)

    def getTitleDisplay(self):
        return "Discussion: " + self.title

#=======================================================================================================================
# Comment (the building block of forums)
#
#=======================================================================================================================
class Comment(Content):

    root_content = models.ForeignKey(Content, related_name='root_content')
    on_content = models.ForeignKey(Content, related_name='comments')
    text = models.TextField(max_length = 10000)
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
        self.title = self.creator_name + "'s comment on " + self.root_content.title
        self.type = 'C'
        self.summary = self.text
        self.in_feed = False
        self.save()
        super(Comment, self).autoSave(creator=creator, privacy=privacy)
        self.setMainTopic(self.root_content.getMainTopic())
        # update on_content
        root_content = self.root_content
        root_content.addComment(commenter=creator)
        on_content = self.on_content
        if on_content != root_content:
            on_content.addComment(commenter=creator)


    def getAlphaDisplayName(self):
        if self.privacy=='PUB':
            return self.getCreator().get_name()
        elif self.privacy=='PRI':
            return 'Anonymous'
        else:
            return 'Someone'

    def getRootContent(self):
        return self.root_content

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


def truncateField(string,name,limit):
    if len( string ) > limit:
        print "+WW+ " + name + " truncated, length = " + str(len(string))
    return string[:limit]

class CongressSession(LGModel):
    session = models.IntegerField(primary_key=True)


#=======================================================================================================================
#
# Legislation
#
#=======================================================================================================================
class Legislation(Content):
    # Bill Identifiers
    congress_session = models.ForeignKey(CongressSession)
    bill_type = models.CharField(max_length=2)
    bill_number = models.IntegerField()
    # Bill Times
    bill_updated = models.DateTimeField(null=True)
    bill_introduced = models.DateField(null=True)
    # State
    state_date = models.DateField(null=True)
    state_text = models.CharField(max_length=50,null=True)
    # Title
    full_title = models.CharField(max_length=5000,null=True)
    # Sponsors
    # cosponsor relationship is stored in LegislationCosponsor object.  To retrieve them you can use "self.legislation_cosponsors"
    sponsor = models.ForeignKey(UserProfile, related_name="sponsored_legislation", null=True)
    committees = models.ManyToManyField('Committee', related_name="legislation_committees", null=True)
    # Others
    bill_relation = models.ManyToManyField('self', null=True, symmetrical=False)
    bill_subjects = models.ManyToManyField('LegislationSubject', null=True, related_name="subject_bills")
    bill_summary = models.TextField(null=True,max_length=400000)
    # action relationship is stored in LegislationAction object.  To retrieve them you can use "self.legislation_actions"

    def getTitle(self):
        if self.title and self.title != '':
            return self.title
        elif self.full_title and self.full_title != '':
            return self.full_title
        else:
            return 'No Legislation Title Available'

    # Returns a list of UserProfile objects that are cosponsors
    # in order to return a list of all LegislationCosponsor relationships, use the query "self.legislation_cosponsors"
    def getCosponsors(self):
        return map( lambda x : x.cosponsor, self.legislation_cosponsors.all() )

    def getActions(self):
        return self.legislation_actions.all()


    def autoSave(self,creator=None,privacy='PUB'):
        self.type = 'L'
        if self.sponsor:
            creator = self.sponsor
            self.creator = creator
        super(Legislation,self).autoSave(creator,privacy)

#=======================================================================================================================
#
# LegislationSubject
#
#=======================================================================================================================
class LegislationSubject(LGModel):
    name = models.CharField(max_length=300)


#=======================================================================================================================
#
# LegislationCosponsor
#
#=======================================================================================================================
class LegislationCosponsor(LGModel):
    legislation = models.ForeignKey(Legislation,related_name="legislation_cosponsors")
    cosponsor = models.ForeignKey(UserProfile)
    date = models.DateField(null=True)


#=======================================================================================================================
#
# LegislationAction
#
#=======================================================================================================================
class LegislationAction(LGModel):
    ACTION_CHOICES = ( ('A','Action'), ('C','Calendar'), ('V', 'Vote'),
                       ('E','Enacted'), ('S', 'Signed'), ('T', 'ToPresident') )
    datetime = models.DateTimeField(null=True)
    legislation = models.ForeignKey(Legislation, null=True, related_name='legislation_actions')
    amendment = models.ForeignKey('LegislationAmendment', null=True, related_name='amendment_actions')
    committee = models.ForeignKey('Committee', null=True, related_name="legislation_activity")
    state = models.TextField(max_length=100, null=True)
    text = models.TextField(max_length=2000, null=True)
    action_type = models.CharField(max_length=1, choices=ACTION_CHOICES)
    references = models.ManyToManyField('LegislationReference')


    def parseGovtrack(self,XML,legislation=None,amendment=None):

        # If action type has not been already, this action has type "action"
        if not self.action_type:
            self.action_type = "A"
        # Get other standard fields
        self.datetime = parseDateTime(XML['datetime'])

        self.text = truncateField( XML.text.encode('utf-8','ignore') , "LegislationAction text" , 500 )

        #Begin duplicate action filtering
        already = LegislationAction.objects.filter( datetime=self.datetime , text=self.text , action_type=self.action_type )

        if legislation:
            self.legislation = legislation
            already = already.filter( legislation = legislation )
        if amendment:
            self.amendment = amendment
            already = already.filter( amendment = amendment )

        if XML.committee: # If this action has a committee
            committee = None # Set initial to None
            subcommittee_name = XML.committee.get('subcommittee') # get potential subcommittee name
            if subcommittee_name: # if that name exists
                committee = Committee.lg.get_or_none(title=subcommittee_name) # try to find that subcommittee
            if not committee: # if no subcommittee was found
                committee_name = XML.committee.get('name') # get the committee name
                if committee_name: # if there is a committee name
                    committee = Committee.lg.get_or_none(title=committee_name) # try to find that committee
            if committee: # if a committee was found
                already = already.filter( committee = committee ) # Refine duplicate filtering
                self.committee = committee # set it!

        #Get state
        if XML.has_key('state'):
            state = truncateField( XML['state'].encode('utf-8','ignore') , "LegislationAction state" , 100 )
            already = already.filter( state = state ) # Refine duplicate filtering
            self.state = state

        action = self # Make the current action yourself
        if already: # If an identical action exists
            action = already[0]

        action.save()

        for refer in XML.findChildren('reference',recursive=False):
            ref_label = truncateField( refer.get('label').encode('utf-8','ignore') , 'LegislationReference ref_label' , 400 )

            ref_reference = truncateField( refer.get('ref').encode('utf-8','ignore') , 'LegislationReference ref_reference' , 400 )

            reference = LegislationReference.lg.get_or_none(ref=ref_reference,label=ref_label)
            if not reference:
                reference = LegislationReference(ref=ref_reference,label=ref_label)
                reference.save()
            action.references.add(reference)


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


    def parseGovtrack(self, XML,legislation=None,amendment=None):
        self.action_type = 'C'

        if XML.has_key('number'):
            self.calendar_number = int(XML['number'])

        if XML.has_key('calendar'):
            self.calendar = truncateField( XML['calendar'].encode('utf-8','ignore') , 'LegislationCalendar calendar' , 100 )

        if XML.has_key('under'):
            self.under = truncateField( XML['under'].encode('utf-8','ignore') , 'LegislationCalendar under' , 100 )

        super(LegislationCalendar, self).parseGovtrack(XML,legislation=legislation,amendment=amendment)



#=======================================================================================================================
#
# LegislationVote
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationVote(LegislationAction):
    how = models.CharField(max_length=100, null=True)
    vote_type = models.CharField(max_length=100, null=True)
    roll = models.IntegerField(null=True)
    where = models.CharField(max_length=4, null=True)
    result = models.CharField(max_length=50, null=True)
    suspension = models.BooleanField(default=False)


    def parseGovtrack(self, XML,legislation=None,amendment=None):
        self.action_type = 'V'

        if XML.has_key('how'):
            self.how = truncateField( XML['how'].encode('utf-8','ignore') , 'LegislationVote how' , 100 )

        if XML.has_key('type'):
            self.vote_type = truncateField( XML['type'].encode('utf-8','ignore') , 'LegislationVote vote_type' , 100 )

        if XML.has_key('roll'):
            self.roll = int(XML['roll'])

        if XML.has_key('where'):
            self.where = truncateField( XML['where'].encode('utf-8','ignore') , 'LegislationVote where' , 4 )

        if XML.has_key('result'):
            self.result = truncateField( XML['result'].encode('utf-8','ignore') , 'LegislationVote result' , 50 )

        if XML.has_key('suspension'):
            self.suspension = ( 1 == int(XML['suspension']) )

        super(LegislationVote, self).parseGovtrack(XML,legislation=legislation,amendment=amendment)


#=======================================================================================================================
#
# LegislationToPresident
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationToPresident(LegislationAction):
    pass


    def parseGovtrack(self, XML,legislation=None,amendment=None):
        self.action_type = 'T'
        super(LegislationToPresident, self).parseGovtrack(XML,legislation=legislation,amendment=amendment)


#=======================================================================================================================
#
# LegislationToSigned
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationSigned(LegislationAction):
    pass


    def parseGovtrack(self,XML,legislation=None,amendment=None):
        self.action_type = 'S'
        super(LegislationSigned, self).parseGovtrack(XML,legislation=legislation,amendment=amendment)


#=======================================================================================================================
#
# LegislationEnacted
#   @super LegislationAction
#
#=======================================================================================================================
class LegislationEnacted(LegislationAction):
    number = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True)


    def parseGovtrack(self, XML,legislation=None,amendment=None):
        self.action_type = 'E'

        if enactedXML.has_key('number'):
            self.number = enactedXML['number'].encode('utf-8','ignore')
        if enactedXML.has_key('type'):
            self.type = enactedXML['type'].encode('utf-8','ignore')

        super(LegislationEnacted, self).parseGovtrack(XML,legislation=legislation,amendment=amendment)


#=======================================================================================================================
#
# LegislationRefLabel
#
#=======================================================================================================================
class LegislationReference(LGModel):
    label = models.CharField(max_length=400)
    ref = models.CharField(max_length=400)


#=======================================================================================================================
#
# LegislationAmendment
#
#=======================================================================================================================
class LegislationAmendment(Content):
    # Identifiers
    legislation= models.ForeignKey(Legislation, related_name="legislation_amendments")
    congress_session = models.ForeignKey('CongressSession', related_name='session_amendments')
    amendment_type = models.CharField(max_length=2)
    amendment_number = models.IntegerField()
    # Datetimes
    updated = models.DateTimeField(null=True)
    offered_datetime = models.DateField(null=True)
    # Status
    status_datetime = models.DateTimeField(null=True)
    status_text = models.CharField(max_length=20)
    # Sponsors
    sponsor = models.ForeignKey(UserProfile,null=True)
    # Other
    description = models.TextField(max_length=50000,null=True)
    purpose = models.TextField(max_length=5000,null=True)
    amends_sequence = models.IntegerField(null=True)

    def autoSave(self,creator=None,privacy='PUB'):
        self.type = 'A'
        if self.sponsor:
            creator = self.sponsor
            self.creator = creator
        super(LegislationAmendment,self).autoSave(creator,privacy)


#=======================================================================================================================
#
# CongressRoll
#
#=======================================================================================================================
class CongressRoll(LGModel):
    # Basic Info
    where = models.CharField(max_length=20)
    session = models.ForeignKey(CongressSession)
    roll_number = models.IntegerField()
    source =  models.CharField(max_length=100)
    # Times
    datetime = models.DateTimeField()
    updated = models.DateTimeField(null=True)
    # Voting Data
    aye = models.IntegerField(default=-1)
    nay = models.IntegerField(default=-1)
    nv = models.IntegerField(default=-1)
    present = models.IntegerField(default=-1)
    # votes are stored with a foreign key
    # Text Info
    category = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    question = models.CharField(max_length=1000, null=True)
    required = models.CharField(max_length=10, null=True)
    result = models.CharField(max_length=80, null=True)
    # Legislation
    legislation = models.ForeignKey(Legislation, null=True, related_name="bill_votes")
    amendment = models.ForeignKey(LegislationAmendment, null=True, related_name="amendment_votes")


#=======================================================================================================================
#
# VotingRecord
#
#=======================================================================================================================
class CongressVote(LGModel):
    roll = models.ForeignKey(CongressRoll,related_name="votes")
    voter = models.ForeignKey(UserProfile,related_name="congress_votes")
    votekey = models.CharField(max_length=1)
    votevalue = models.CharField(max_length=15)



########################################################################################################################
########################################################################################################################
#   QA
#       Question is a piece of content (can be liked, disliked, too_complicated, commented on etc)
#       Users can create questions.
#
########################################################################################################################
########################################################################################################################
#=======================================================================================================================
# Poll, a bunch of questions
#
#=======================================================================================================================
class Poll(Content):
    questions = models.ManyToManyField("Question")
    num_questions = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    def getTitleDisplay(self):
        return "Poll: " + self.title

    def get_url(self):
        return '/poll/' + str(self.id) + '/'

    def autoSave(self, creator=None, privacy='PUB'):
        self.type = "O"
        self.in_feed = True
        self.save()
        super(Poll, self).autoSave(creator=creator, privacy=privacy)

    def addQuestion(self, q):
        if q not in self.questions.all():
            self.questions.add(q)
            self.num_questions += 1
            self.save()

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
    question_text = models.TextField(max_length=500)
    question_type = models.CharField(max_length=2, default="D")
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

    def getTitleDisplay(self):
        return "Question: " + self.title

    def autoSave(self, creator=None, privacy='PUB'):
        self.type = "Q"
        self.in_feed = True
        self.save()
        super(Question, self).autoSave(creator=creator, privacy=privacy)

    def edit(self,field,value):
        if field=="question_text":
            self.question_text=value
        else:
            super(Question, self).edit(field,value)
        self.save()

    def getImageURL(self):
        if self.main_image_id < 0:
            return DEFAULT_DISCUSSION_IMAGE_URL
        elif self.main_image:
            return self.main_image.image.url
        else:
            return DEFAULT_DISCUSSION_IMAGE_URL


#=======================================================================================================================
# Response, abstract so that content users and groups can inherit from it
#
#=======================================================================================================================
class Response(Content):
    question = models.ForeignKey(Question)
    answer_val = models.IntegerField(default=-1)
    most_chosen_answer = models.ForeignKey(Answer,related_name="responses",null=True)
    most_chosen_num = models.IntegerField(default=0)
    total_num = models.IntegerField(default=0)
    weight = models.IntegerField(default=50)
    explanation = models.TextField(max_length=1000, blank=True)
    answer_tallies = models.ManyToManyField('AnswerTally')

    def getPercent(self, a_id):
        if self.total_num:
            if a_id == self.most_chosen_answer_id:
                percent = self.most_chosen_num / float(self.total_num)
            else:
                tally = self.answer_tallies.filter(answer_id=a_id)
                if tally:
                    percent = tally[0].tally / float(self.total_num)
                else:
                    percent = 0
            return int(percent*100)
        else:
            return 0

    #-------------------------------------------------------------------------------------------------------------------
    # Autosaves by adding picture and topic from question.
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.main_image_id = self.question.main_image_id
        self.in_feed = False
        self.save()
        self.type = 'R'
        if creator:
            view = creator.getView()
            view.responses.add(self)
        super(Response, self).autoSave(creator=creator, privacy=privacy)
        self.setMainTopic(self.question.getMainTopic())

    def getValue(self):
        return float(self.answer_val)

    def clearAnswerTallies(self):
        self.answer_tallies.delete()

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

    def clearResponses(self):
        self.responses.all().delete()

#=======================================================================================================================
# Comparison of specific topic.
#
#=======================================================================================================================
class TopicComparison(LGModel):
    topic = models.ForeignKey(Topic)
    result = models.IntegerField(default=0)
    num_q = models.IntegerField(default=0)
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
    result = models.IntegerField(default=0)
    num_q = models.IntegerField(default=0)
    bytopic = models.ManyToManyField(TopicComparison)
    optimized = models.CharField(max_length=1000, null=True)

    def loadOptimized(self):
        from lovegov.modernpolitics.compare import FastComparison
        if self.optimized:
            comparison = FastComparison(json_buckets=self.optimized)
            return comparison
        else:
            return None

    def saveOptimized(self, fast_comparison):
        self.optimized = fast_comparison.dumpBuckets()

    def get_url(self):
        return '/comparison/' + str(self.id)

    def update(self, result, num_q, when):
        self.result = result
        self.num_q = num_q
        self.when = when
        self.save()

    def oldToDict(self):
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

    def  toDict(self, viewB_url=''):
        from lovegov.modernpolitics.helpers import getMainTopics
        to_return = []
        fast_comparison = self.loadOptimized()
        if not fast_comparison:
            temp_logger.debug('old comparison.')
            return self.oldToDict()
        else:
            topics = getMainTopics()
            for t in topics:
                topic_text = t.topic_text
                topic_dict = {'text':topic_text,
                             'colors': MAIN_TOPICS_COLORS[topic_text],
                             'mini_img': '/static' + MAIN_TOPICS_MINI_IMG[topic_text],
                             'order': MAIN_TOPICS_CLOCKWISE_ORDER[topic_text],
                             'result':0,
                             'num_q':0}
                topic_bucket = fast_comparison.getTopicBucket(t)
                topic_dict['result'] = topic_bucket.getSimilarityPercent()
                topic_dict['num_q'] = topic_bucket.num_questions
                to_return.append(topic_dict)
            to_return.sort(key=lambda x: x['order'])
            total_bucket = fast_comparison.getTotalBucket()
            vals = {'topics':to_return,'main':{'result':total_bucket.getSimilarityPercent(),'num_q':total_bucket.num_questions}}
            vals['user_url'] = viewB_url
            return vals

    def toBreakdown(self):
        from lovegov.modernpolitics.helpers import LGException
        from lovegov.modernpolitics.helpers import getMainTopics
        fast_comparison = self.loadOptimized()
        if not fast_comparison:
            raise LGException("no fast comparison whaaa")
        else:
            topics = getMainTopics()
            topics_comparisons = []
            to_return ={'topics':topics_comparisons}
            for topic in topics:
                topic_text = topic.topic_text
                t = {'topic':topic,
                     'order':MAIN_TOPICS_CLOCKWISE_ORDER[topic_text],
                     'light_color':MAIN_TOPICS_COLORS[topic_text]['default'],
                     'dark_color':MAIN_TOPICS_COLORS[topic_text]['light']}
                topic_bucket = fast_comparison.getTopicBucket(topic)
                t['result'] = topic_bucket.getSimilarityPercent()
                t['empty'] = 100 - t['result']
                t['num_q'] = topic_bucket.num_questions
                topics_comparisons.append(t)
            topics_comparisons.sort(key=lambda x: x['order'])
            total_bucket = fast_comparison.getTotalBucket()
            to_return['main'] = {'result':total_bucket.getSimilarityPercent(),'num_q':total_bucket.num_questions}
            to_return['main']['empty'] = 100 - to_return['main']['result']
            return to_return




    def toJSON(self, viewB_url=''):
        return json.dumps(self.toDict(viewB_url))

    # checks if the comparison is still valid given the two inputted dates, returns True if Stale, false if still fresh
    def checkStale(self, dateA=None, dateB=None):
        if dateA and dateB:
            newest = max(dateA, dateB)
            return self.when < newest
        else:
            return True

    def updateTopic(self, topic, topic_bucket):
        by_topic = self.bytopic.filter(topic=topic)
        result = topic_bucket.getSimilarityPercent()
        num_q =  topic_bucket.num_questions
        if by_topic:
            by_topic = by_topic[0]
            by_topic.result = result
            by_topic.num_q = num_q
            by_topic.save()
        else:
            by_topic = TopicComparison(topic=topic, result=result, num_q=num_q)
            by_topic.save()
            self.bytopic.add(by_topic)

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
class AnswerTally(LGModel):
    answer = models.ForeignKey('Answer',null=True)
    tally = models.IntegerField()

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
    admins = models.ManyToManyField(UserProfile, related_name='admin_of')
    members = models.ManyToManyField(UserProfile, related_name='member_of')
    num_members = models.IntegerField(default=0)
    # info
    full_text = models.TextField(max_length=1000)
    pinned_content = models.ManyToManyField(Content, related_name='pinned_to')
    group_view = models.ForeignKey(WorldView)           # these are all aggregate response, so they can be downcasted
    # group type
    group_type = models.CharField(max_length=1,choices=GROUP_TYPE_CHOICES, default='S')
    group_privacy = models.CharField(max_length=1,choices=GROUP_PRIVACY_CHOICES, default='O')   # for non-system groups, is it open or invite-only?
    system = models.BooleanField(default=False)                                                 # indicates users can't voluntarily join or leave
    hidden = models.BooleanField(default=False)                                                 # indicates that a group shouldn't be visible in lists [like-minded, folow groups etc]
    autogen = models.BooleanField(default=False)                                                # indicates whether we created group or not
    subscribable = models.BooleanField(default=True)                                            # indicates whether or not you can follow or unfollow this group
    content_by_posting = models.BooleanField(default=True)                                      # if true, group content is determined based on what is posted to group
                                                                                                # else false, then group content is determined by things created by members anywhere
    # democratic groups
    democratic = models.BooleanField(default=False)       # if false, fields below have no importance
    government_type = models.CharField(max_length=30, choices=GOVERNMENT_TYPE_CHOICES, default="traditional")
    participation_threshold = models.IntegerField(default=30)   # % of group which must upvote on motion to pass
    agreement_threshold = models.IntegerField(default=50)       # % of group which most agree with motion to pass
    motion_expiration = models.IntegerField(default=7)          # number of days before motion expires and vote close

    def getTitleDisplay(self):
        return "Group: " + self.title

    #-------------------------------------------------------------------------------------------------------------------
    # gets content posted to group, for feed
    #-------------------------------------------------------------------------------------------------------------------
    def getContent(self):
        return Content.objects.filter(posted_to=self, in_feed=True)

    #-------------------------------------------------------------------------------------------------------------------
    # gets url for content
    #-------------------------------------------------------------------------------------------------------------------
    def get_url(self):
        if self.alias != "default":
            return '/' + self.alias + '/'
        else:
            return '/group/' + str(self.id) + '/'

    #-------------------------------------------------------------------------------------------------------------------
    # Downcasts Group to appropriate child model.
    #-------------------------------------------------------------------------------------------------------------------
    def downcast(self):
        type = self.group_type
        if type == 'N':
            object = self.network
        elif type == 'P':
            object = self.party
        elif type == 'U':
            object = self.usergroup
        elif type == 'E':
            object = self.election
        elif type == 'S':
            object = self.stategroup
        elif type == 'C':
            object = self.committee
        elif type == 'T':               # for towngroup?
            object = self.towngroup
        elif type == 'Y':
            object = self.politiciangroup
        else: object = self
        return object

    #-------------------------------------------------------------------------------------------------------------------
    # Returns json of histogram data.
    #-------------------------------------------------------------------------------------------------------------------
    def getComparisonHistogram(self, user, bucket_list, start=0, num=-1, topic_alias=None):

        def getBucket(result, buckets_list):            # takes in a number and returns closest >= bucket
            i = 0
            current=buckets_list[0]
            num_buckets = len(buckets_list)
            while current < result and i < num_buckets:
                current = buckets_list[i]
                i += 1

            if result > current:
                to_return = num_buckets-1
            elif i>0:
                to_return = i-1
            else:
                to_return = 0

            return buckets_list[to_return]

        # ACTUAL METHOD
        buckets = {}                              # initialize empty histogram dictionary
        for bucket in bucket_list:
            buckets[bucket] = {'num':0, 'u_ids':[]}

        if num == -1:
            members = self.members.all()[start:]
        else:
            members = self.members.all()[start:start+num]

        topic = Topic.lg.get_or_none(alias=topic_alias)
        total = 0
        identical = 0
        identical_uids = []

        for x in members:
            comparison = x.getComparison(user).loadOptimized()
            if comparison:
                total += 1
                if topic and topic_alias != 'all':
                    comparison = comparison.getTopicBucket(topic)
                else:
                    comparison = comparison.getTotalBucket()
                if comparison.getNumQuestions():
                    result = comparison.getSimilarityPercent()
                    bucket = getBucket(result, bucket_list)
                    buckets[bucket]['num'] += 1
                    buckets[bucket]['u_ids'].append(x.id)
                    if result == 100:
                        identical += 1
                        identical_uids.append(x.id)

        return {'total':int(total), 'identical': identical, 'identical_uids': identical_uids,
                'buckets':buckets,'color':MAIN_TOPICS_COLORS_ALIAS[topic_alias]['default']}


    #-------------------------------------------------------------------------------------------------------------------
    # Get url of histogram detail.
    #-------------------------------------------------------------------------------------------------------------------
    def getHistogramURL(self):
        return self.get_url() + 'histogram/'

    #-------------------------------------------------------------------------------------------------------------------
    # Joins a member to the group and creates GroupJoined appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def countMembers(self):
        self.num_members = self.members.count()
        self.save()

    #-------------------------------------------------------------------------------------------------------------------
    # Joins a member to the group and creates GroupJoined appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def joinMember(self, user, privacy='PUB'):
        group_joined = GroupJoined.lg.get_or_none(user=user, group=self)
        if not group_joined:
            group_joined = GroupJoined(user=user, group=self)
            group_joined.autoSave()
        group_joined.privacy = privacy
        if not group_joined.confirmed and not group_joined.group.system:
            user.num_groups += 1
            user.save()
        group_joined.confirm()
        group_joined.ever_member = True
        self.members.add(user)
        self.num_members += 1
        self.save()
        from lovegov.modernpolitics.actions import followGroupAction
        followGroupAction(user, self, True, privacy)

    #-------------------------------------------------------------------------------------------------------------------
    # Removes a member from the group and creates GroupJoined appropriately.
    #-------------------------------------------------------------------------------------------------------------------
    def removeMember(self, user, privacy='PUB'):
        group_joined = GroupJoined.lg.get_or_none(user=user, group=self)
        if not group_joined:
            group_joined = GroupJoined(user=user, group=self)
            group_joined.autoSave()
        group_joined.privacy = privacy
        if group_joined.confirmed and not group_joined.group.hidden:
            user.num_groups -= 1
            user.save()
        group_joined.clear()
        if user in self.members.all():
            self.num_members -= 1
            self.save()
        self.members.remove(user)
        self.admins.remove(user)

    #-------------------------------------------------------------------------------------------------------------------
    # Gets comparison between this group and inputted user.
    #-------------------------------------------------------------------------------------------------------------------
    def getComparison(self, viewer):
        from lovegov.modernpolitics.compare import getUserGroupComparison
        return getUserGroupComparison(user=viewer, group=self)

    def getComparisonJSON(self, viewer):
        comparison = self.getComparison(viewer)
        return comparison, comparison.toJSON()

    def prepComparison(self, viewer):
        comparison, json = self.getComparisonJSON(viewer)
        self.compare = json
        self.result = comparison.result

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
        if not self.summary:
            self.summary = self.full_text[:400]
        self.type='G'
        worldview = WorldView()
        worldview.save()
        self.group_view = worldview
        self.alias = self.makeAlias()
        self.in_calc = False
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
    def getMembers(self, start=0, num=-1):
        members = self.members.all()
        if num == -1:
            return members[start:]
        else:
            return members[start:start+num]

    def getNumMembers(self):
        return self.members.count()

    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getFollowRequests(self, num=-1):
        if num == -1:
            return GroupJoined.objects.filter( group=self, confirmed=False, requested=True, rejected=False ).order_by('-when')
        else:
            return GroupJoined.objects.filter( group=self, confirmed=False, requested=True, rejected=False ).order_by('-when')[:num]

    def getNumFollowRequests(self):
        return GroupJoined.objects.filter( group=self, confirmed=False, requested=True, rejected=False ).count()


    #-------------------------------------------------------------------------------------------------------------------
    # Returns a query set of all unconfirmed requests.
    #-------------------------------------------------------------------------------------------------------------------
    def getActivity(self, start=0, num=-1):
        gmembers = self.members.all()
        actions = Action.objects.filter(relationship__user__in=gmembers, privacy='PUB').order_by('-when')
        if num != 1:
            return actions[start:start+num]
        return actions[start:]


    #-------------------------------------------------------------------------------------------------------------------
    # Returns the number of petitions the whole group has created
    #-------------------------------------------------------------------------------------------------------------------
    def getNumPetitions(self):
        num_petitions = 0
        for member in self.members.all():
            num_petitions += member.num_petitions
        return num_petitions

    #-------------------------------------------------------------------------------------------------------------------
    # Returns the number of articles the whole group has created
    #-------------------------------------------------------------------------------------------------------------------
    def getNumArticles(self):
        num_articles = 0
        for member in self.members.all():
            num_articles += member.num_articles
        return num_articles

    #-------------------------------------------------------------------------------------------------------------------
    # Returns the average number of questions the whole group has answered
    #-------------------------------------------------------------------------------------------------------------------
    def getAverageQuestions(self):
        if self.members.count() == 0:
            return 0
        num_questions = 0
        for member in self.members.all():
            num_questions += member.getView().responses.count()
        avg_questions = num_questions/self.members.count()
        return int(round(avg_questions))

    def getImageURL(self):
        if self.main_image_id < 0:
            return DEFAULT_GROUP_IMAGE_URL
        elif self.main_image:
            return self.main_image.image.url
        else:
            return DEFAULT_GROUP_IMAGE_URL

    def makeAlias(self):
        from lovegov.modernpolitics.helpers import genAliasSlug
        self.alias = genAliasSlug(self.title)
        self.save()
        return self.alias

    def getMotionExpiration(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=self.motion_expiration)
        expiration = now + delta
        return  expiration

    def coup(self, government_type):
        self.government_type = government_type
        if government_type == 'traditional':
            self.democratic = False
        else:
            self.democratic = True
        self.save()

#=======================================================================================================================
# Motion, for democratic groups.
#
#=======================================================================================================================
class Motion(Content):
    group = models.ForeignKey(Group)
    motion_type = models.CharField(max_length=30, choices=MOTION_CHOICES, default='other')
    full_text = models.TextField()
    expiration_date = models.DateTimeField()
    passed = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    above_threshold = models.BooleanField(default=False)
    motion_upvotes = models.IntegerField(default=0)
    motion_downvotes = models.IntegerField(default=0)
    # add/remove moderator motion
    moderator = models.ForeignKey(UserProfile, null=True)
    # change group government type
    government_type = models.CharField(max_length=30, choices=GOVERNMENT_TYPE_CHOICES, default="traditional")

    #-------------------------------------------------------------------------------------------------------------------
    # autosave
    #-------------------------------------------------------------------------------------------------------------------
    def autoSave(self, creator=None, privacy='PUB'):
        self.type='M'
        expiration_date = self.group.getMotionExpiration()
        self.expiration_date = expiration_date
        self.in_feed = True
        self.title = self.getTitle()
        self.summary = self.full_text[:100]
        self.save()
        super(Motion, self).autoSave(creator=creator, privacy=privacy)

    def getTitle(self):
        if self.motion_type == "add_moderator":
            return "MOTION: " + self.group.get_name() + " Add Moderator " + self.moderator.get_name()
        elif self.motion_type == "remove_moderator":
            return "MOTION: " + self.group.get_name() + " Remove Moderator " + self.moderator.get_name()
        elif self.motion_type == "coup_detat":
            return "MOTION: " + self.group.get_name() + " Coup D'etat"

    def execute(self):
        if self.motion_type == "add_moderator":
            self.group.admins.add(self.moderator)
        elif self.motion_type == "remove_moderator":
            self.group.admins.remove(self.moderator)
        elif self.motion_type == "coup_detat":
            self.group.coup(self.government_type)

    def motionVote(self, my_vote):
        if self.isActionable():
            group = self.group
            user = my_vote.user
            if group.hasMember(user):
                motion_vote = MotionVoted.lg.get_or_none(user=user, content=self)
                if motion_vote:
                    motion_vote.value = my_vote.value
                    motion_vote.save()
                else:
                    motion_vote = MotionVoted(user=user, content=self, value=my_vote.value, privacy=my_vote.privacy)
                    motion_vote.autoSave()
            self.calc()

    def calc(self):

        if self.isActionable():
            group = self.group

            votes = MotionVoted.objects.filter(content=self)
            upvotes = votes.filter(value=1).count()
            downvotes = votes.filter(value=-1).count()
            totalvotes = upvotes + downvotes
            self.motion_upvotes = upvotes
            self.motion_downvotes = downvotes

            participation = int(totalvotes / float(group.members.count()) * 100)
            agreement = int(upvotes / float(totalvotes) * 100)

            if participation > group.participation_threshold and agreement > group.agreement_threshold:
                self.above_threshold = True

            now = datetime.datetime.now()
            expiration_date = self.expiration_date
            if now > expiration_date:
                self.expired = True
                if self.above_threshold:
                    self.passed = True
            else:
                if participation > group.agreement_threshold:
                    self.passed = True
            self.save()

            if self.passed:
                self.execute()

    def isActionable(self):
        return not (self.passed or self.expired)

#=======================================================================================================================
# Network Group, created by parsing facebook networks
#
#=======================================================================================================================
class Network(Group):
    name = models.CharField(max_length=50)                  # DEPRECATED
    network_type = models.CharField(max_length=1, choices=NETWORK_TYPE, default='D')
    extension = models.CharField(max_length=50, null=True)

    # autosave any network
    def autoSave(self, creator=None, privacy="PUB"):
        self.group_type = 'N'
        self.autogen = True
        self.group_privacy = "O"
        super(Network, self).autoSave()

#=======================================================================================================================
# Location group, is created for specific locations (from submitted addresses)
#
#=======================================================================================================================
class StateGroup(Group):
    pass
    def autoCreate(self, state):
        state_text = STATES_DICT[state]
        self.title = state_text + " State Group"
        self.description = "A group for sharing political information relevant to the state of " + state_text + "."
        self.group_type = 'S'
        self.autogen = True
        self.group_privacy = "O"
        super(StateGroup, self).autoSave()
        location = PhysicalAddress(state=state)
        location.save()
        self.location = location
        self.save()

class TownGroup(Group):
    pass
    def autoCreate(self, city, state):
        city_state = city + ", " + state
        self.title = city_state + " Group"
        self.description = "A group for sharing political information relevant to " + city_state + "."
        self.group_type = 'T'
        self.autogen = True
        self.group_privacy = "O"
        super(TownGroup, self).autoSave()
        location = PhysicalAddress(state=state, city=city)
        location.save()
        self.location = location
        self.save()

#=======================================================================================================================
# Politician group, is a sytem group for organizing politicians
#
#=======================================================================================================================
class PoliticianGroup(Group):
    def autoSave(self):
        self.group_type = 'Y'
        self.system = True
        self.autogen = True
        self.content_by_posting = False
        self.group_privacy = 'O'
        super(PoliticianGroup, self).autoSave()

# uniquely identified by location__state                # for visualization of all congress from a state
class StatePoliticianGroup(PoliticianGroup):
    pass

# uniquely identified by location__state location__district combo           # for visualization for all congress form a district
class DistrictPoliticianGroup(PoliticianGroup):
    representatives = models.ManyToManyField(UserProfile, related_name="district_rep_group")
    senators = models.ManyToManyField(UserProfile, related_name="district_sen_group")
    pass

#=======================================================================================================================
# Political party group
#
#=======================================================================================================================
class Party(Group):
    party_type = models.CharField(max_length=1, choices=PARTY_TYPE, default='D')
    party_label = models.ImageField(null=True, upload_to="defaults/")

    # autosave any network
    def autoSave(self, creator=None, privacy="PUB"):
        self.group_type = 'P'
        self.system = False
        self.group_privacy = 'O'
        super(Party, self).autoSave()

    def get_url(self):
        return '/group/' + str( self.id ) + '/'

    def joinMember(self, user, privacy='PUB'):
        user.parties.add(self)
        user.save()
        super(Party, self).joinMember(user, privacy)

    def removeMember(self, user, privacy='PUB'):
        user.parties.remove(self)
        user.save()
        super(Party, self).removeMember(user, privacy)

#=======================================================================================================================
# User Group
#
#=======================================================================================================================
class UserGroup(Group):
    def autoSave(self, creator=None, privacy="PUB"):
        self.group_type = 'U'
        super(UserGroup, self).autoSave(creator=creator,privacy=privacy)

#=======================================================================================================================
# an election, is a group centered around a particular office
#=======================================================================================================================
class Election(Group):
    running = models.ManyToManyField(UserProfile, related_name="running_for")
    winner = models.ForeignKey(UserProfile, null=True, related_name="elections_won")
    office = models.ForeignKey(Office, null=True)
    election_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    def autoSave(self, creator=None, privacy="PUB"):
        self.group_type = 'E'
        super(Election, self).autoSave(creator=creator,privacy=privacy)

    def joinRace(self, user):
        if not user in self.running.all():
            self.running.add(user)

    def getCandidatesURL(self):
        return self.get_url() + '/candidates/'

########################################################################################################################
################################################### Committees #########################################################
# External Imports
class Committee(Group):
    code = models.CharField(max_length=20)
    committee_type = models.CharField(max_length=2, choices=COMMITTEE_CHOICES)
    parent = models.ForeignKey('self', null=True)

    def autoSave(self):
        self.group_type = 'C'
        super(Committee, self).autoSave()

    def joinMember(self, user, congress_session, role=None, privacy='PUB'):
        committee_joined = CommitteeJoined.lg.get_or_none(user=user, group=self)
        if not committee_joined:
            committee_joined = CommitteeJoined(user=user, group=self)
            committee_joined.autoSave()

        committee_joined.privacy = privacy
        committee_joined.congress_sessions.add(congress_session)
        if role:
            committee_joined.role = role
        committee_joined.ever_member = True

        if congress_session.session == CURRENT_CONGRESS:
            committee_joined.confirm()
            if user not in self.members.all():
                self.members.add(user)
                self.num_members += 1
                self.save()


    def removeMember(self, user, privacy='PUB'):
        committee_joined = CommitteeJoined.lg.get_or_none(user=user, group=self)
        if not committee_joined:
            committee_joined = CommitteeJoined(user=user, group=self)
            committee_joined.autoSave()
        committee_joined.privacy = privacy
        committee_joined.clear()
        if user in self.members.all():
            self.members.remove(user)
            self.num_members -= 1
            self.save()



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
    page = models.CharField(max_length=5000)
    action = models.CharField(max_length=50, null=True)
    when = models.DateTimeField(auto_now_add=True)
    left = models.DateTimeField(null=True)
    duration = models.TimeField(null=True)
    type = models.CharField(max_length=4)
    exit = models.BooleanField(default=False)
    login = models.BooleanField(default=True)

    def autoSave(self, request):
        from lovegov.modernpolitics.helpers import getSourcePath, getUserProfile
        user_prof = getUserProfile(request)
        if user_prof:
            self.user = user_prof
            self.page = getSourcePath(request)
            self.ipaddress = request.META['REMOTE_ADDR']
            if request.method == "POST":
                self.type = 'POST'
                if 'action' in request.POST:
                    self.action = request.POST['action']
            else:
                self.type = 'GET'
                if 'action' in request.GET:
                    self.action = request.GET['action']
            self.save()

class CompatabilityLog(LGModel):
    user = models.ForeignKey("UserProfile", null=True)
    incompatible = custom_fields.ListField(default=[])
    page = models.CharField(max_length=100, blank=True)
    ipaddress = models.IPAddressField(default='255.255.255.255', null=True)
    user_agent = models.CharField(max_length=250, blank=True)
    when = models.DateTimeField(auto_now_add=True)
    def autoSave(self):
        self.save()
        return self

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
    user = models.ForeignKey(UserProfile, related_name='relationships')
    created_when = models.DateTimeField(auto_now_add=True)
    relationship_type = models.CharField(max_length=2,choices=RELATIONSHIP_CHOICES)
    #-------------------------------------------------------------------------------------------------------------------
    # Downcasts relationship to appropriate child model.
    #-------------------------------------------------------------------------------------------------------------------
    def downcast(self):
        type = self.relationship_type
        if type == 'VO':
            object = self.ucrelationship.voted
        # relationships with invite/request/decline/reject. all inherit from Invite , below
        elif type== 'JO':
            object = self.ucrelationship.groupjoined
        elif type == 'FO':
            object = self.uurelationship.userfollow
        elif type == 'SI':
            object = self.ucrelationship.signed
        elif type == 'OH':
            object = self.ucrelationship.officeheld
        elif type == 'CJ':
            object = self.ucrelationship.committeejoined
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
        self.declined = False
        self.invited = True
        self.inviter = inviter.id
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
# office held
#=======================================================================================================================
class OfficeHeld(UCRelationship):
    office = models.ForeignKey('Office',related_name="office_terms")
    confirmed = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    current = models.BooleanField(default=False)
    election = models.BooleanField(default=False)
    congress_sessions = models.ManyToManyField(CongressSession)

    def autoSave(self):
        self.content = self.office
        self.relationship_type = "OH"
        self.save()

    def isCurrent(self):
        if (datetime.date.today() - self.end_date).days <= 0:
            return True
        return False

    def setCurrent(self):
        if self.office.tags.filter(name="congress"):
            if self.congress_sessions.filter(session=CURRENT_CONGRESS_SESSION) and self.confirmed:
                self.current = True
                self.save()
            else:
                self.current = False
                self.save()
        else:
            is_current = self.isCurrent()
            if is_current and self.confirmed:
                self.current = True
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
# Stores a user sharing a piece of content.
# inherits from relationship
#=======================================================================================================================
class Signed(UCRelationship):
    def autoSave(self):
        self.relationship_type = 'SI'
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
        self.content = self.group
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
# Support a politician.
#=======================================================================================================================
class Supported(UURelationship):
    confirmed = models.BooleanField(default=True)
    def autoSave(self):
        self.relationship_type = 'SU'
        self.creator = self.user
        self.save()

#=======================================================================================================================
# A Method that stores data on the relationship between an Elected Offical and a Committee
#
#=======================================================================================================================
class CommitteeJoined(GroupJoined):
    role = models.CharField(max_length=200,null=True)
    congress_sessions = models.ManyToManyField(CongressSession)

    def autoSave(self):
        self.relationship_type = 'CJ'
        super(CommitteeJoined, self).autoSave()




















#=======================================================================================================================
# For a user to write about their views on a topic.
#
#=======================================================================================================================
class TopicView(Privacy):
    view = models.TextField(max_length=10000, blank=True)
    topic = models.ForeignKey(Topic)


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
class ResetPassword(LGModel):
    userProfile = models.ForeignKey(UserProfile)
    email_code = models.CharField(max_length=75)
    created_when = models.DateTimeField(auto_now_add=True)

    def create(username):

        from lovegov.modernpolitics.helpers import generateRandomPassword

        toDelete = ResetPassword.lg.get_or_none(userProfile__username=username)
        if toDelete: toDelete.delete()

        userProfile = UserProfile.lg.get_or_none(username=username)
        if userProfile:
            try:
                reseturl = generateRandomPassword(50)
                new = ResetPassword(userProfile=userProfile,email_code=reseturl)
                new.save()
                vals = {'firstname':userProfile.first_name, 'url':reseturl}
                from lovegov.modernpolitics import send_email
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


