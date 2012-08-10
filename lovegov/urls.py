# lovegov
from lovegov.frontend import views, tests, analytics
from lovegov.modernpolitics import posts, lgwidget, api, twitter
from lovegov.frontend.views import viewWrapper

# django
from django.conf.urls import patterns, include, url
from django.contrib.admin import site
from django.contrib import admin
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

LOCAL = settings.LOCAL

admin.autodiscover()


urlpatterns = patterns('',

    # blog
    (r'^blog/(?P<category>\S+)/(?P<number>\d+)/$', viewWrapper(views.blog)),
    (r'^blog/(?P<category>\S+)/$', viewWrapper(views.blog)),
    (r'^blog/$', viewWrapper(views.blog)))

# locally serve static and media
if LOCAL:
    urlpatterns += staticfiles_urlpatterns()
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
    urlpatterns += patterns('', (r'^%s(?P<path>.*)$' % _media_url,serve,
                                     {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)


# Users and groups are prevented from generating aliases which match these strings
# Be liberal about this list - it should include potential app URLs in addition to those actually being used
URL_SPECIAL_NAMES = set([
    'login',
    'passwordRecovery',
    'confirm',
    'need_email_confirmation',
    'fb',
    'twitter',
    'logout',
    'underconstruction',
    'upgrade',
    'continue',
    'try',
    'home',
    'web',
    'about',
    'account',
    'match',
    'search',
    'question',
    'topic',
    'petition',
    'news',
    'networks',
    'action',
    'answer',
    'widget',
    'test'
    'test2',
    'test3',
    'css',
    'images',
    'static',
    'javascript',
    'js',
    'jquery',
    'developer',
    'alpha',
    'beta',
    'analytics',
    'api',
    'motion'
])

# lovegov urls
urlpatterns += patterns('',

    # login page
    (r'^login/(?P<to_page>\S*)/$', viewWrapper(views.login)),                            # login
    (r'^login/$', viewWrapper(views.login)),
    (r'^passwordRecovery/(\S*)$', viewWrapper(views.passwordRecovery)),                  # password recovery
    (r'^confirm/(?P<confirm_link>\S+)/$', viewWrapper(views.confirm)),                   # confirm
    (r'^need_email_confirmation/$', viewWrapper(views.needConfirmation)),                # need confirmation

    # fb authentication
    (r'^fb/authorize/$', views.facebookAuthorize),
    (r'^fb/handle/$', viewWrapper(views.facebookHandle)),

    # twitter authentication
    (r'^twitter/redirect/$', viewWrapper(twitter.twitterTryLogin)),                      # redirect to twitter, and back to handle
    (r'^twitter/handle/$', viewWrapper(twitter.twitterHandle)),                          # handles return from twitter
    (r'^twitter/register/$', viewWrapper(twitter.twitterRegister)),                      # twitter form page

    # misc
    (r'^logout/$', viewWrapper(views.logout)),
    (r'^underconstruction/$', views.underConstruction),
    (r'^upgrade/$', views.upgrade),
    (r'^continue/$', views.continueAtOwnRisk),
    (r'^try/$', viewWrapper(views.tryLoveGov)),
    (r'^try/(\S+)/$', viewWrapper(views.tryLoveGov)),

    # main pages
    (r'^home/$', viewWrapper(views.feed, requires_login=True)),                            # home page with feeds
    (r'^web/$', viewWrapper(views.web, requires_login=True)),                                 # big look at web
    (r'^about/$', viewWrapper(views.about, requires_login=True)),                                                   # about
    (r'^about/(\w+)/$', viewWrapper(views.about, requires_login=True)),                       # about
    (r'^account/$', viewWrapper(views.account,requires_login=True)),                          # account/change password
    (r'^account/(?P<section>\S+)/$', viewWrapper(views.account,requires_login=True)),         # account/change password
    (r'^match/$', viewWrapper(views.newMatch, requires_login=True)),                           # match page
    (r'^match/(\w+)/$', viewWrapper(views.newMatch, requires_login=True)),                    # match page
    (r'^search/(?P<term>.*)/$', viewWrapper(views.search, requires_login=True)),


    # content pages
    (r'^question/(\d+)/$', viewWrapper(views.questionDetail, requires_login=True)),           # question detail
    (r'^petition/(\d+)/$', viewWrapper(views.petitionDetail, requires_login=True)),           # petition detail
    (r'^news/(\d+)/$', viewWrapper(views.newsDetail, requires_login=True)),                   # news detail
    (r'^network/(\S+)/$', viewWrapper(views.network, requires_login=True)),                   # network page
    (r'^network/$', viewWrapper(views.network, requires_login=True)),                         # network page
    (r'^group/(\d+)/edit/$', viewWrapper(views.groupEdit, requires_login=True)),
    (r'^group/(\d+)/edit/(?P<section>\S+)/$', viewWrapper(views.groupEdit, requires_login=True)),
    (r'^group/(\d+)/$', viewWrapper(views.group, requires_login=True)),
    (r'^histogram/(\d+)/$', viewWrapper(views.histogramDetail, requires_login=True)),               # histogram detail of group
    (r'^feed/$', viewWrapper(views.feed, requires_login=True)),                            # the feed
    (r'^profile/web/(\S+)/$', viewWrapper(views.compareWeb, requires_login=True)),            # profile/comparison
    (r'^profile/(\S+)/$', viewWrapper(views.profile, requires_login=True)),                   # profile/comparison
    (r'^nextquestion/$', viewWrapper(views.nextQuestion, requires_login=True)),               # sensibly redirects to next question
    (r'^legislation/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/(?P<number>\d+)/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^friends/$', viewWrapper(views.iFollow, requires_login=True)),
    (r'^groups/$', viewWrapper(views.groups, requires_login=True)),
    (r'^networks/$', viewWrapper(views.networks, requires_login=True)),
    (r'^motion/(\d+)/$', viewWrapper(views.motionDetail, requires_login=True)),

    # ajax pages
    (r'^action/$', viewWrapper(posts.actionPOST, requires_login=True)),                      # comment and other actions
    (r'^answer/$', viewWrapper(views.profile, requires_login=True)),                           # comment and other actions
    (r'^fb/action/$', viewWrapper(views.facebookAction, requires_login=True)),

    # widget pages
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                     # widget api access

    # test pages
    (r'^test/$', viewWrapper(tests.test, requires_login=True)),                                    # test page, for whatever you want!
    (r'^test2/$', viewWrapper(tests.test2, requires_login=True)),                                  # for testing logging
    (r'^test3/$', viewWrapper(tests.test3, requires_login=True)),
    (r'^css/$', viewWrapper(tests.css, requires_login=True)),

    #admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),

    # analytics
    (r'^analytics/activity/(\d+)/$', viewWrapper(analytics.dailyActivity, requires_login=True)),                   # analytics of daily activity
    (r'^analytics/activity/$', viewWrapper(analytics.dailyActivity, requires_login=True)),                        # analytics of daily activity
    (r'^analytics/total/(\S+)/$', viewWrapper(analytics.totalActivity, requires_login=True)),                     # analytics of total user activity
    (r'^analytics/total/$', viewWrapper(analytics.totalActivity, requires_login=True)),                           # analytics of all activity

    # api
    (r'^api/(?P<model>\S+)/$', viewWrapper(api.handleRequest)),

    # REDIRECT
    (r'(?P<alias>\S+)/$', views.aliasDowncast),
    (r'.*/$', views.redirect),
    (r'^$', views.redirect)
)
