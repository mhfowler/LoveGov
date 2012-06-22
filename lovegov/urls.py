# lovegov
from lovegov.frontend import views, tests, analytics
from lovegov.modernpolitics import actions, lgwidget
from lovegov.frontend.views import requiresLogin
from lovegov.frontend.views import viewWrapper
from lovegov.frontend import admin_views
from lovegov.local_manage import LOCAL

# django
from django.conf.urls.defaults import patterns, include, url
from django.contrib.admin import site
from django.contrib import admin
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',

    ## SPLASH ###
    (r'^comingsoon/$', views.splash),
    (r'^learnmore/$', views.learnmore),
    (r'^postEmail/$',views.postEmail))

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


# lovegov urls
urlpatterns += patterns('',


    # outside of login
    (r'^login/(?P<to_page>\S*)/$', viewWrapper(views.login)),                             # login
    (r'^confirm/(?P<confirm_link>\S+)/$', viewWrapper(views.confirm)),                   # confirm
    (r'^fb/authorize/$', views.facebookAuthorize ),
    (r'^fb/handle/$', viewWrapper(views.facebookHandle)),
    (r'^passwordRecovery/(\S*)$', viewWrapper(views.passwordRecovery)),
    (r'^twitter/redirect/$', viewWrapper(views.twitterRedirect)),
    (r'^twitter/handle/$', viewWrapper(views.twitterHandle)),

    (r'^blog/(?P<category>\S+)/(?P<number>\d+)/$', viewWrapper(views.blog)),
    (r'^blog/(?P<category>\S+)/$', viewWrapper(views.blog)),
    (r'^blog/$', viewWrapper(views.blog)),


    # under construction
    (r'^underconstruction/$', views.underConstruction),

    # main pages
    (r'^home/$', requiresLogin(viewWrapper(views.home))),                               # home page with feeds
    (r'^web/$', requiresLogin(viewWrapper(views.web))),                                 # big look at web
    (r'^about/$', requiresLogin(viewWrapper(views.about))),                             # about
    (r'^account/$', requiresLogin(viewWrapper(views.account))),                         # account/change password
    (r'^match/$', requiresLogin(viewWrapper(views.match))),                             # match page
    (r'^matchNew/$', requiresLogin(viewWrapper(views.matchNew))),

    # content pages
    (r'^question/(\d+)/$', requiresLogin(viewWrapper(views.questionDetail))),           # question detail
    (r'^topic/(\S+)/$', requiresLogin(viewWrapper(views.topicDetail))),                 # topic detail
    (r'^petition/(\d+)/$', requiresLogin(viewWrapper(views.petitionDetail))),           # petition detail
    (r'^news/(\d+)/$', requiresLogin(viewWrapper(views.newsDetail))),                   # news detail
    (r'^network/(\S+)/$', requiresLogin(viewWrapper(views.network))),                   # network page
    (r'^network/$', requiresLogin(viewWrapper(views.network))),                         # network page
    (r'^group/(\d+)/$', requiresLogin(viewWrapper(views.group))),
    (r'^feed/$', requiresLogin(viewWrapper(views.theFeed))),                            # the feed
    (r'^profile/web/(\S+)/$', requiresLogin(viewWrapper(views.compareWeb))),            # profile/comparison
    (r'^profile/(\S+)/$', requiresLogin(viewWrapper(views.profile))),                   # profile/comparison
    (r'^nextquestion/$', requiresLogin(viewWrapper(views.nextQuestion))),               # sensibly redirects to next question
    (r'^legislation/$', requiresLogin(viewWrapper(views.legislation))),
    (r'^legislation/(?P<session>\d+)/$', requiresLogin(viewWrapper(views.legislation))),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/$', requiresLogin(viewWrapper(views.legislation))),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/(?P<number>\d+)/$', requiresLogin(viewWrapper(views.legislation))),

    # ajax pages
    (r'^logout/$', requiresLogin(viewWrapper(views.logout))),                            # logout
    (r'^action/$', requiresLogin(viewWrapper(actions.actionPOST))),                      # comment and other actions
    (r'^answer/$', requiresLogin(viewWrapper(views.profile))),                           # comment and other actions
    (r'^fb/action/$', requiresLogin(viewWrapper(views.facebookAction)) ),

    # widget pages
    (r'^widget/about/$', views.widgetAbout),                                    # widget about page
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                     # widget api access

    # test pages
    (r'^test/$', requiresLogin(viewWrapper(tests.test))),                                    # test page, for whatever you want!
    (r'^test2/$', tests.test2 ),                                                # for testing logging

    #admin
    (r'^developer/$', requiresLogin(viewWrapper(admin_views.adminHome))),
    (r'^alpha/admin_action/$', requiresLogin(viewWrapper(admin_views.adminAction))),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),

    # analytics
    (r'^analytics/activity/(\d+)/$', analytics.dailyActivity),                   # analytics of daily activity
    (r'^analytics/activity/$', analytics.dailyActivity),                        # analytics of daily activity
    (r'^analytics/total/(\S+)/$', analytics.totalActivity),                     # analytics of total user activity
    (r'^analytics/total/$', analytics.totalActivity),                           # analytics of all activity

    # REDIRECT
    (r'.*/$', views.redirect),
    (r'^$', views.redirect))
