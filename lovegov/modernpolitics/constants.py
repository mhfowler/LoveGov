########################################################################################################################
########################################################################################################################
#
#           Constants
#
#
########################################################################################################################
########################################################################################################################

# django
from django.conf import settings
from lovegov.settings import PROJECT_PATH

# python
import sunlight
import os.path
import datetime
import os

LOCAL = settings.LOCAL

SUPER_HEROES = ['lovegov', 'anonymous']

########################################## PROHIBITED BROWSERS #########################################################

PROHIBITED_BROWSERS = ["MSIE"]
ALLOWED_BROWSERS = ["Chrome","Mozilla"]

########################################## EMAIL LISTS #################################################################

TEAM_EMAILS =  ['max_fowler@brown.edu','jonathanvkoh@gmail.com',
                'loweth.g@gmail.com','yoshi141@gmail.com',
                'cschmidt@risd.edu', 'jsgreenf@gmail.com', 'ccapuozz@risd.edu']
YAY_EMAILS = TEAM_EMAILS
DAILY_SUMMARY_EMAILS = TEAM_EMAILS

########################################## KEYS ########################################################################

# for lovegov
RECAPTCHA_PUBLIC = "6Lcuys0SAAAAAPjzGtCQ1BEuFLocySXZMuApQjvd"
RECAPTCHA_PRIVATE = "6Lcuys0SAAAAAKFVKH6DP2_4JPt_dKtc8n-tZ_2M"

# for novavote
GOOGLE_NOVAVOTE = 'UA-31121281-1'
GOOGLE_LOVEGOV = 'UA-31122448-1'

sunlight.config.API_KEY  = '47ec0a395b9241d7902d6c5c896a8167'
GOOGLEMAPS_API_KEY = 'AIzaSyA_ZfbazhowTs7D4e93YuG6pdLefZIG1gs'

BILL_TYPES = {
    's': 'Senate Bill',
    'h': 'House of Representatives Bill',
    'hr': 'House of Representatives Resolution',
    'sr': 'Senate Resolution',
    'hc': 'House of Representatives Concurrent Resolution',
    'sc': 'Senate Concurrent Resolution',
    'sj': 'Senate Joint Resolution',
    'hj': 'House of Representatives Joint Resolution',
}

########################################## FOR RANKING & FILTERING #####################################################

# systems of ranking... each implies a different filter_setting
RANKING_CHOICES = (
    ('B','best'),
    ('N','new'),
    ('H', 'hot')
    )

# different algos for ranking [we could add more]
ALGO_CHOICES = (
    ('D','default'),
    ('H','hot'),
    ('B', 'bayesian')
    )

# general constants for ranking
MIN_RANK = -1000
DOWNVOTE_DAMPEN = 0.5       # two downvotes is equivalent to one upvote
FEED_SIZE = 10              # default feed size
FEED_MAX = 100              # feed max (for sitewide feeds)

# constants for new filter
NEWFILTER_DAYS = 14
TIME_BONUS = 5          # this should be how many upvotes a day we think a good piece of content should get

# constants for hot filter
HOT_WINDOW = 3 # number of days to count votes within when using hot algo


########################################### DEFAULT SETTINGS ###########################################################

# for chunksize comparison
COMPARISON_CHUNKSIZE = 2

# initial bonus on creation
STATUS_CREATION = 0

# increase with vote
STATUS_VOTE = 1

# increase with various actions
STATUS_COMMENT = 1
STATUS_SHARE = 0
STATUS_FOLLOW = 0

NOTIFICATION_INCREMENT = 5
MEMBER_INCREMENT = 24
GROUP_INCREMENT = 4

PRESIDENTIAL_CANDIDATES = ['rick@lovegov.com','barack@lovegov.com','newt@lovegov.com','mitt@lovegov.com','ron@lovegov.com']

PRESIDENTIAL_IMG_FOLDER = "/static/images/presidential/"
PRESIDENTIAL_CANDIDATES_IMG = {'rick@lovegov.com':PRESIDENTIAL_IMG_FOLDER + 'santorum.jpg',
                               'barack@lovegov.com':PRESIDENTIAL_IMG_FOLDER + 'obama.jpg',
                               'newt@lovegov.com':PRESIDENTIAL_IMG_FOLDER + 'gingrich.jpg',
                               'mitt@lovegov.com':PRESIDENTIAL_IMG_FOLDER + 'romney.jpg',
                               'ron@lovegov.com':PRESIDENTIAL_IMG_FOLDER + 'paul.jpg'}

DEFAULT_CONTENT_NOTIFICATIONS = ['CO', 'VO', 'FC', 'XX', 'ED', 'MV', 'DV', 'SI', 'JO', 'AE']
DEFAULT_USER_NOTIFICATIONS = ['SI', 'CR', 'JO', 'DM', 'AE']
DEFAULT_EMAIL_NOTIFICATIONS = ['VO', 'DM', 'CO', 'FO', 'JO']


NUM_QUESTIONS = 5

HISTOGRAM_RESOLUTION = 10

DEFAULT_INVITE_SUBJECT = "Welcome to LoveGov Alpha"

DEFAULT_INVITE_MESSAGE = "LoveGov Alpha is now up and running! We would really appreciate it if you logged in and test run the features of our site. "\
                         "Please keep in mind that Alpha only contains a portion of the functionality intended for the Brown/RISD beta, "\
                         "so you will see us regularly adding new features over the next month. If you encounter any problems while using our site"\
                         "or just want to send us comments then please don't hesitate to contact us - we want to hear your opinions!"

FIRST_LOGIN_LAST_STAGE = 7

########################################### MAIN TOPICS ################################################################
MAIN_TOPICS = ['Economy', 'Education', 'Energy', 'Environment', 'Health Care', 'National Security', 'Social Issues']

MAIN_TOPIC_IMG_FOLDER = "/static/images/questionIcons/"

MAIN_TOPICS_IMG = {'Economy':MAIN_TOPIC_IMG_FOLDER + 'economy/eco_default.png',
                   'Education':MAIN_TOPIC_IMG_FOLDER + 'education/edu_default.png',
                   'Social Issues':MAIN_TOPIC_IMG_FOLDER + 'socialissues/soc_default.png',
                   'National Security':MAIN_TOPIC_IMG_FOLDER + 'nationalsecurity/nat_default.png',
                   'Environment':MAIN_TOPIC_IMG_FOLDER + 'environment/env_default.png',
                   'Energy':MAIN_TOPIC_IMG_FOLDER + 'energy/ene_default.png',
                   'Health Care':MAIN_TOPIC_IMG_FOLDER + 'healthcare/hea_default.png',
                   'General':MAIN_TOPIC_IMG_FOLDER + 'general/gen_default.png'}

MAIN_TOPICS_MINI_IMG = {'Economy':MAIN_TOPIC_IMG_FOLDER + 'economy/eco_mini.png',
                        'Education':MAIN_TOPIC_IMG_FOLDER + 'education/edu_mini.png',
                        'Social Issues':MAIN_TOPIC_IMG_FOLDER + 'socialissues/soc_mini.png',
                        'National Security':MAIN_TOPIC_IMG_FOLDER + 'nationalsecurity/nat_mini.png',
                        'Environment':MAIN_TOPIC_IMG_FOLDER + 'environment/env_mini.png',
                        'Energy':MAIN_TOPIC_IMG_FOLDER + 'energy/ene_mini.png',
                        'Health Care':MAIN_TOPIC_IMG_FOLDER + 'healthcare/hea_mini.png'}

MAIN_TOPICS_COLORS = {'Economy':{'default':'#92B76C','light':'#CCDDC0'},
                     'Education':{'default':'#9DC5C9','light':'#D3EBED'},
                     'Social Issues':{'default':'#639E9B','light':'#A3C6C4'},
                     'National Security':{'default':'#EA947D','light':'#FFCBC0'},
                     'Environment':{'default':'#9797C6','light':'#D4D3EF'},
                     'Energy':{'default':'#F9D180','light':'#FFF0C5'},
                     'Health Care':{'default':'#EA7D95','light':'#FBCCD6'},
                     'All':{'default':'#EF503B','light':'#FC8A81'}}

MAIN_TOPICS_COLORS_ALIAS = {'economy':{'default':'#92B76C','light':'#CCDDC0'},
                      'education':{'default':'#9DC5C9','light':'#D3EBED'},
                      'socialissues':{'default':'#639E9B','light':'#A3C6C4'},
                      'nationalsecurity':{'default':'#EA947D','light':'#FFCBC0'},
                      'environment':{'default':'#9797C6','light':'#D4D3EF'},
                      'energy':{'default':'#F9D180','light':'#FFF0C5'},
                      'healthcare':{'default':'#EA7D95','light':'#FBCCD6'},
                      'all':{'default':'#EF503B','light':'#FC8A81'}}

MAIN_TOPICS_CLOCKWISE_ORDER = {'Economy':0,
                               'Education':1,
                               'Social Issues':6,
                               'National Security':5,
                               'Environment':3,
                               'Energy':2,
                               'Health Care':4}

MAIN_TOPIC_COLORS_LIST = []
for topic in MAIN_TOPICS:
    MAIN_TOPIC_COLORS_LIST.insert(MAIN_TOPICS_CLOCKWISE_ORDER[topic],MAIN_TOPICS_COLORS[topic]['default'])

POLITICAL_PARTIES_IMAGES = []
#for imgRef in os.listdir(os.path.join(PROJECT_PATH, 'frontend/static/images/party_labels/')):
#    if imgRef != "filter.svg": POLITICAL_PARTIES_IMAGES.append({'path':'/static/images/party_labels/' + imgRef,'name':imgRef.replace(".png",'')})


########################################### PROCESS PATHS ##############################################################

#PHANTOMJS = os.path.join(PROJECT_PATH, 'alpha/process/phantomjs/bin/./phantomjs')
#PHANTOMJS_RASTERIZE = os.path.join(PROJECT_PATH, 'alpha/process/phantomjs/examples/rasterize.js')

########################################## CHOICES #####################################################################

# editable fields
USERPROFILE_EDITABLE_FIELDS = [
    'bio',
]

CONTENT_EDITABLE_FIELDS = [
    'text', 
    'full_text',
    'title',
]

# level of government
SCALE_CHOICES = (
    ('P', 'Personal'),
    ('L', 'Local'),
    ('S', 'State'),
    ('F', 'Federal'),
    ('W', 'World'),
    ('A', 'All')
)

# feed display types
FEED_DISPLAY_CHOICES = (
    ('P', 'pinterest'),
    ('L', 'linear')
)

# privacy setting types
PRIVACY_CHOICES = (
    ('PUB','Public'),
    ('PRI','Private')
    )

# content types
TYPE_CHOICES = (
    ('E','event'),
    ('P','petition'),
    ('N','news'),
    ('L','legislation'),
    ('Q','question'),
    ('R','response'),
    ('G','group'),
    ('C','comment'),
    ('I','image'),
    ('A','album'),
    ('Z','content-response'),
    ('D','discussion'),
    ('Y', 'persistent-debate'),
    ('M', 'motion'),
    )

# persitent debate types
DEBATE_CHOICES = (
    ('C','casual'),
    ('F','formal'),
    ('M', 'moderated')
    )

# types of notifications
NOTIFICATION_CHOICES = (
    ('C','comment'),
    ('M','message'),
    ('S','shared'),
    ('R', 'request'),    # friend request
    ('I', 'invitation'),    # for event
    ('D', 'debate')
    )

# types of user action (for display)
RELATIONSHIP_CHOICES = (
    ('CO','commented'),
    ('SH','shared'),
    ('CR', 'created'),
    ('ED', 'edited'),
    ('SI', 'signed'),
    ('SU', 'supported'),
    ('ME', 'messaged'),
    ('FC', 'followed content'),
    ('XX', 'deleted'),
    ('VO', 'voted'),                        # divided into like and dislike
    ('FO', 'followed'),                     # divided into request, invited, denied and following.
    ('JO', 'joined'),                       # divided into request, invited, denied and joined.
    ('AE', 'attended_event'),              # divided into request, invited, denied and attending.
    ('JD', 'joined_debate'),                # divided into request, invited, denied and joined.
    ('AC', 'admin_content'),                # divided into request, invited, denied and joined.
    ('OT', 'other'),
    ('MV','motion_voted'),
    ('DV','debate_voted'),
    ('DM', 'debate_messaged'),
    )

RELATIONSHIP_DICT = {}
for x in RELATIONSHIP_CHOICES:
    RELATIONSHIP_DICT[x[1]]=x[0]

# default, request, invite, deny, reject
ACTION_MODIFIERS = (
    ('D','default'), #Can also be dislike
    ('R','request'),
    ('I','invited'),
    ('X', 'rejected'),
    ('N', 'declined'),
    ('A', 'accepted'),
    ('S', 'stop'),
    ('L', 'like'),
    ('U', 'unvoted')
        )

# types of action which user should be notified about
NOTIFY_TYPES = ['FO','SI','JO','CO','VO','SH']
AGGREGATE_NOTIFY_TYPES = ['SI','VO','CO','SH']
NOTIFY_MODIFIERS = {
    'VO': ['L'],
    'JO': ['A','D','R','I'],
    'FO': ['A','D','R']
}



# Timedelta that it takes for aggregate notifications to go stale.
STALE_TIME_DELTA = datetime.timedelta(14)

# group privacy settings
GROUP_PRIVACY_CHOICES = (
    ('O','open'),
    ('P','private'),
    ('S','secret'),
)
CONTENT_PRIVACY_CHOICES = (
    ('O','open'),
    ('C','closed'),
    ('P','private'),
)

# types of groups
GROUP_TYPE_CHOICES = (
    ('N','network'),
    ('P','party'),
    ('U','user'),
    ('S', 'system')
)

# types of group government
GOVERNMENT_TYPE_CHOICES = (
    ('traditional','Traditional'),
    ('representative','Representative'),
    ('democratic','Democratic'),
)

NETWORK_TYPE = (
    ('D','default'),
    ('S','school'),
    ('L','location')
)

PARTY_TYPE = (
    ('A', 'pirate'),
    ('D', 'democrat'),
    ('G', 'green'),
    ('R', 'republican'),
    ('L', 'libertarian'),
    ('P', 'progressive'),
    ('I', 'independent'),
    ('T', 'tea')
)

# types of users
USER_CHOICES =  (
    ('U','user'),
    ('P','politician'),
    ('S','senator'),
    ('R','representative'),
    ('G', 'ghost')
)

# types of motions
MOTION_CHOICES = (
    ('other', 'Other'),
    ('charity', 'Charity'),
    ('add', 'Add moderator'),
    ('remove', 'Remove moderator'),
    ('coup', 'Coup')
)

# types of user permissions
PERMISSION_CHOICES = (
    ('N', 'normal'),
    ('P', 'politician'),
    ('C', 'campaign')
)

# type vals
TYPE_DICT = {'event':'E', 'petition':'P', 'news':'N', 'legislation':'L',
             'question':'Q','response':'R','group':'G','comment':'C',
             'image':'I','album':'A','content-response':'Z','debate':'D',
             'motion':'M', 'forum':'F'}

# bill types
BILL_TYPES = {
    's': 'Senate Bill',
    'h': 'House of Representatives Bill',
    'hr': 'House of Representatives Resolution',
    'sr': 'Senate Resolution',
    'hc': 'House of Representatives Committee Bill',
    'sc': 'Senate Committee Bill',
    'sj': 'Senate Joint Bill',
    'hj': 'House of Representatives Joint Bill',
}

# types of content that show up in the feed
FEED_CONTENT_TYPES = ['P','N','L','G']

# Facebook Stuff
FACEBOOK_SCOPE = 'email,user_education_history,user_location,user_birthday'

###################################### STATIC FILE URLS ################################################################

DEFAULT_IMAGE = os.path.join(PROJECT_PATH, 'frontend/static/images/profile_default.jpg')
DEFAULT_PROFILE_IMAGE_URL = '/static/images/profile_default.jpg'
DEFAULT_NEWS_IMAGE_URL = '/static/images/icons/content-big/news.png'
DEFAULT_PETITION_IMAGE_URL = '/static/images/icons/content-big/petition.png'
DEFAULT_GROUP_IMAGE_URL = '/static/images/icons/content-big/group.png'
DEFAULT_DISCUSSION_IMAGE_URL = '/static/images/icons/content-big/discussion.png'

STATIC_PATH = '/media/'

IMPORTANT_LEGISLATION = [
    ('112','h3'),
    ('110','h1592'),
    ('111','h3590'),
    ('111','s3072'),
    ('111','h4173'),
    ('109','hr921'),
    ('109','hj88'),
    ('111','h2965'),
    ('110','h3685'),
    ('110','h1424'),
    ('112','h1231'),
    ('111','h2454'),
    ('109','h6'),
    ('110','h2272'),
    ('110','h3221'),
    ('112','hj2'),
    ('109','hr6166'),
    ('109','s2611'),
    ('109','hr6061'),
    ('110','s5'),
    ('110','s30'),
    ('111','h4314'),
    ('111','h5175'),
    ('110','h4137'),
    ('110','h2'),
    ('112','h1229'),
    ('109','s2590'),
    ('112','h2021'),
    ('112','h1231'),
    ('112','h471'),
    ('111','h3246'),
]

IMPORTANT_AMENDMENTS = [
    ('109','h272'),
    ('110','h186'),
    ('111','h262'),
    ('111','h172'),
    ('109','h487'),
    ('109','h667'),
    ('111','h3701'),
    ('109','h278'),
    ('109','h427'),
    ('112','h41'),
    ('112','h800'),
    ('112','s183'),
    ('111','h266'),
    ('109','h88'),
    ('111','h220'),
    ('109','h650'),
    ('109','s4689'),

]

###################################### GAMIFICATION ####################################################################

PETITION_LEVELS = [0, 10, 50, 100, 500, 1000, 5000, 10000, 50000,
                   100000, 500000, 1000000, 5000000, 10000000,
                   50000000, 100000000, 500000000, 1000000000,
                   5000000000, 10000000000]

###################################### ACTIONS #########################################################################

ACTIONS = [
    'loadGroupUsers',
    'loadHistogram',
    'searchAutoComplete',
    'comment',
    'create',
    'invite',
    'editAccount',
    'editProfile',
    'editContent',
    'delete',
    'setPrivacy',
    'setFollowPrivacy',
    'vote',
    'hoverComparison',
    'sign',
    'finalize',
    'userFollowRequest',
    'userFollowResponse',
    'userFollowStop',
    'answer',
    'joinGroupRequest',
    'joinGroupResponse',
    'groupInviteResponse',
    'leaveGroup',
    'matchComparison',
    'posttogroup',
    'updateCompare',
    'viewCompare',
    'answerWeb',
    'feedback',
    'updateGroupView',
    'ajaxThread',
    'getNotifications',
    'getUserActions',
    'getUserGroups',
    'getGroupActions',
    'getGroupMembers',
    'ajaxGetFeed',
    'matchSection',
    'saveFilter',
    'deleteFilter',
    'getFilter',
    'shareContent',
    'blogAction',
    'flag',
    'updateHistogram',
    'getHistogramMembers',
    'getAllGroupMembers',
    'support',
    'messageRep',
    'submitAddress',
    'likeThis',
    'changeContentPrivacy',
    'updatePage',
    'getAggregateNotificationUsers',
    'getSigners',
    'setFirstLoginStage',
    'editGroup',
    'addAdmins',
    'removeAdmin',
    'groupInviteResponse',
    'groupInvite',
    'getLinkInfo',
    'removeMembers'
]

DEFAULT_PROHIBITED_ACTIONS = []

ANONYMOUS_PROHIBITED_ACTIONS = [
    #'loadGroupUsers',
    #'loadHistogram',
    #'searchAutoComplete',
    'comment',
    'create',
    'invite',
    'editAccount',
    'editProfile',
    'editContent',
    'delete',
    'setPrivacy',
    'setFollowPrivacy',
    'vote',
    #'hoverComparison',
    'sign',
    'finalize',
    'userFollowRequest',
    'userFollowResponse',
    'userFollowStop',
    'answer',
    'joinGroupRequest',
    'joinGroupResponse',
    'groupInviteResponse',
    'leaveGroup',
    'matchComparison',
    'posttogroup',
    'updateCompare',
    'viewCompare',
    'answerWeb',
    #'feedback',
    #'updateGroupView',
    #'ajaxThread',
    #'getNotifications',
    #'getUserActions',
    #'getUserGroups',
    #'getGroupActions',
    #'getGroupMembers',
    #'ajaxGetFeed',
    #'matchSection',
    'saveFilter',
    'deleteFilter',
    #'getFilter',
    'shareContent',
    #'blogAction',
    #'flag',
    #'updateHistogram',
    #'getHistogramMembers',
    #'getAllGroupMembers',
    'support',
    #'messageRep',
    'submitAddress',
    'likeThis',
    #'changeContentPrivacy',
    #'updatePage',
    #'getAggregateNotificationUsers',
    #'getSigners',
    #'setFirstLoginStage',
    'setFirstLoginStage',
    'editGroup',
    'addAdmins',
    'removeAdmin',
    'groupInviteResponse',
    'groupInvite'
]
