# lovegov
from lovegov.frontend import views, tests, analytics
from lovegov.modernpolitics import actions, lgwidget
from lovegov.frontend.views import requiresLogin
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
    (r'^login/(?P<to_page>\S*)/$',views.login),                             # login
    (r'^confirm/(?P<confirm_link>\S+)/$', views.confirm),                   # confirm
    (r'^privacypolicy/$', views.privacyPolicy),                             # privacy
    (r'^fb/authorize/$', views.facebookAuthorize ),
    (r'^fb/handle/$', views.facebookHandle),
    (r'^passwordRecovery/(\S*)$', views.passwordRecovery),
    (r'^twitter/redirect/$', views.twitterRedirect),
    (r'^twitter/handle/$', views.twitterHandle),

    # under construction
    (r'^underconstruction/$', views.underConstruction),

    # main pages
    (r'^home/$', requiresLogin(views.home)),                               # home page with feeds
    (r'^web/$', requiresLogin(views.web)),                                 # big look at web
    (r'^about/$', requiresLogin(views.about)),                             # about
    (r'^account/$', requiresLogin(views.account)),                         # account/change password
    (r'^match/$', requiresLogin(views.match)),                             # match page
    (r'^matchNew/$', requiresLogin(views.matchNew)),

    # content pages
    (r'^question/(\d+)/$', requiresLogin(views.questionDetail)),           # question detail
    (r'^topic/(\S+)/$', requiresLogin(views.topicDetail)),                 # topic detail
    (r'^petition/(\d+)/$', requiresLogin(views.petitionDetail)),           # petition detail
    (r'^news/(\d+)/$', requiresLogin(views.newsDetail)),                   # news detail
    (r'^network/(\S+)/$', requiresLogin(views.network)),                   # network page
    (r'^network/$', requiresLogin(views.network)),                         # network page
    (r'^group/(\d+)/$', requiresLogin(views.group)),
    (r'^profile/web/(\S+)/$', requiresLogin(views.compareWeb)),            # profile/comparison
    (r'^profile/(\S+)/$', requiresLogin(views.profile)),                   # profile/comparison
    (r'^nextquestion/$', requiresLogin(views.nextQuestion)),               # sensibly redirects to next question
    (r'^legislation/$', requiresLogin(views.legislation)),
    (r'^legislation/(?P<session>\d+)/$', requiresLogin(views.legislation)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/$', requiresLogin(views.legislation)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/(?P<number>\d+)/$', requiresLogin(views.legislation)),

    # ajax pages
    (r'^logout/$', requiresLogin(views.logout)),                            # logout
    (r'^action/$', requiresLogin(actions.actionPOST)),                      # comment and other actions
    (r'^answer/$', requiresLogin(views.profile)),                           # comment and other actions
    (r'^fb/action/$', requiresLogin(views.facebookAction) ),

    # widget pages
    (r'^widget/about/$', views.widgetAbout),                                    # widget about page
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                     # widget api access

    # test pages
    (r'^test/$', requiresLogin(tests.test)),                                    # test page, for whatever you want!
    (r'^test2/$', tests.test2 ),                                                # for testing logging

    #admin
    (r'^developer/$', requiresLogin(admin_views.adminHome)),
    (r'^alpha/admin_action/$', requiresLogin(admin_views.adminAction)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),

    # analytics
    (r'^analytics/activity/$', analytics.dailyActivity),                        # analytics of daily activity

    # REDIRECT
    (r'.*/$', views.redirect),
    (r'^$', views.redirect))
