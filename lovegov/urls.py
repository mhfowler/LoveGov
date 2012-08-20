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

# lovegov urls
urlpatterns += patterns('',

    # login page
    (r'^login/(?P<to_page>\S*)/$', viewWrapper(views.login)),
    (r'^login/$', viewWrapper(views.login)),
    (r'^passwordRecovery/(\S*)$', viewWrapper(views.passwordRecovery)),
    (r'^confirm/(?P<confirm_link>\S+)/$', viewWrapper(views.confirm)),
    (r'^need_email_confirmation/$', viewWrapper(views.needConfirmation)),

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

    # home pages
    (r'^home/$', viewWrapper(views.home, requires_login=True)),
    (r'^groups/$', viewWrapper(views.groups, requires_login=True)),
    (r'^elections/$', viewWrapper(views.elections, requires_login=True)),
    (r'^politicians/$', viewWrapper(views.politicians, requires_login=True)),
    (r'^presidential/$', viewWrapper(views.presidential, requires_login=True)),
    (r'^representatives/$', viewWrapper(views.representatives, requires_login=True)),
    (r'^friends/$', viewWrapper(views.friends, requires_login=True)),
    (r'^questions/$', viewWrapper(views.questions, requires_login=True)),

    # browse-all
    (r'^browse_groups/$', viewWrapper(views.browseGroups, requires_login=True)),
    #(r'^browse_people/$', viewWrapper(views.browsePeople, requires_login=True)),
    #(r'^browse_friends/$', viewWrapper(views.browseFriends, requires_login=True)),
    #(r'^browse_politicians/$', viewWrapper(views.browsePoliticians, requires_login=True)),

    # other main pages
    (r'^home/$', viewWrapper(views.redirect, requires_login=True)),
    (r'^web/$', viewWrapper(views.web, requires_login=True)),
    (r'^about/$', viewWrapper(views.about, requires_login=True)),
    (r'^about/(\w+)/$', viewWrapper(views.about, requires_login=True)),
    (r'^settings/$', viewWrapper(views.account,requires_login=True)),
    (r'^settings/(?P<section>\S+)/$', viewWrapper(views.account,requires_login=True)),
    (r'^search/(?P<term>.*)/$', viewWrapper(views.search, requires_login=True)),

    # detail pages
    (r'^profile/$', viewWrapper(views.profile, requires_login=True)),
    (r'^profile/(\S+)/$', viewWrapper(views.profile, requires_login=True)),
    (r'^question/(\d+)/$', viewWrapper(views.questionDetail, requires_login=True)),
    (r'^news/(\d+)/$', viewWrapper(views.newsDetail, requires_login=True)),
    (r'^poll/(\d+)/$', viewWrapper(views.pollDetail, requires_login=True)),
    (r'^petition/(\d+)/$', viewWrapper(views.petitionDetail, requires_login=True)),
    (r'^discussion/(\d+)/$', viewWrapper(views.discussionDetail, requires_login=True)),
    (r'^motion/(\d+)/$', viewWrapper(views.motionDetail, requires_login=True)),
    (r'^group/(\d+)/$', viewWrapper(views.groupPage, requires_login=True)),
    (r'^thread/(\d+)/$', viewWrapper(views.thread, requires_login=True)),

    # special pages
    (r'^profile/web/(\S+)/$', viewWrapper(views.compareWeb, requires_login=True)),              # profile/comparison
    (r'^group/(\d+)/edit/$', viewWrapper(views.groupEdit, requires_login=True)),
    (r'^group/(\d+)/edit/(?P<section>\S+)/$', viewWrapper(views.groupEdit, requires_login=True)),

    # legislation
    (r'^legislation/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(?P<session>\d+)/(?P<type>\w+)/(?P<number>\d+)/$', viewWrapper(views.legislation, requires_login=True)),

    # ajax pages
    (r'^action/$', viewWrapper(posts.actionPOST, requires_login=True)),
    (r'^answer/$', viewWrapper(views.profile, requires_login=True)),
    (r'^fb/action/$', viewWrapper(views.facebookAction, requires_login=True)),

    # widget pages
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                                     # widget api access

    # test pages
    (r'^test/$', viewWrapper(tests.test, requires_login=True)),                                 # test page, for whatever you want!
    (r'^test2/$', viewWrapper(tests.test2, requires_login=True)),                               # for testing logging
    (r'^test3/$', viewWrapper(tests.test3, requires_login=True)),
    (r'^css/$', viewWrapper(tests.css, requires_login=True)),

    #admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),

    # analytics
    (r'^analytics/activity/(\d+)/$', viewWrapper(analytics.dailyActivity, requires_login=True)),
    (r'^analytics/activity/$', viewWrapper(analytics.dailyActivity, requires_login=True)),
    (r'^analytics/total/(\S+)/$', viewWrapper(analytics.totalActivity, requires_login=True)),
    (r'^analytics/total/$', viewWrapper(analytics.totalActivity, requires_login=True)),

    # api
    (r'^api/(?P<model>\S+)/$', viewWrapper(api.handleRequest)),

    # urls based on alias
    (r'(?P<alias>\w+)/edit/$', views.aliasDowncastEdit),
    (r'^(?P<alias>\w+)/worldview/$', viewWrapper(views.worldview, requires_login=True)),                 # view breakdown of person
    (r'^(?P<alias>\w+)/histogram/$', viewWrapper(views.histogramDetail, requires_login=True)),           # histogram detail of group

    # REDIRECT
    (r'(?P<alias>\w+)/$', views.aliasDowncast),
    (r'.*/$', views.redirect),
    (r'^$', views.redirect)
)
