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
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic.simple import direct_to_template

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
    (r'^mission/$', viewWrapper(views.loginMission)),
    (r'^how_it_works/$', viewWrapper(views.loginHowItWorks)),
    (r'^sign_up/$', viewWrapper(views.loginSignUp)),
    (r'^presidential_matching/$', viewWrapper(views.presidentialMatching)),
    (r'^password_recovery/(\S*)/$', viewWrapper(views.passwordRecovery)),
    (r'^password_recovery/$', viewWrapper(views.passwordRecovery)),
    (r'^confirm/(?P<confirm_link>\S+)/$', viewWrapper(views.confirm)),
    (r'^need_email_confirmation/$', viewWrapper(views.needConfirmation)),
    (r'^claim_your_profile/(?P<claimed_by>\S+)/$', viewWrapper(views.loginSignUp)),
    (r'^register/$', views.redirect, {'page':"/sign_up/"}),
    (r'^hello/$', viewWrapper(views.hello)),
    (r'^privacy_policy/$', viewWrapper(views.privacyPolicy)),
    (r'^terms_of_use/$', viewWrapper(views.termsOfUse)),
    (r'^faq/$', viewWrapper(views.loginFAQ)),

    # fb authentication
    (r'^fb/redirect(\S*)$', views.facebookRedirect),                                    # redirects you to facebook
    (r'^fb/authorize/$', views.facebookAuthorize),
    (r'^fb/handle/$', viewWrapper(views.facebookHandle)),
    (r'^fb/connect/$', viewWrapper(views.facebookConnect, requires_login=True)),

    # twitter authentication
    (r'^twitter/redirect/$', viewWrapper(twitter.twitterTryLogin)),                      # redirect to twitter, and back to handle
    (r'^twitter/handle/$', viewWrapper(twitter.twitterHandle)),                          # handles return from twitter
    (r'^twitter/register/$', viewWrapper(views.twitterRegister)),                      # twitter form page

    # misc
    (r'^logout/$', viewWrapper(views.logout)),
    (r'^upgrade/$', views.upgrade),
    (r'^continue/$', views.continueAtOwnRisk),
    (r'^try/$', viewWrapper(views.tryLoveGov)),
    (r'^try/(\S+)/$', viewWrapper(views.tryLoveGov)),
    (r'^unsubscribe/(\S+)/$', views.unsubscribe),
    (r'^to_lovegov/(\d+)/$', views.goToLoveGov),
    (r'^lgalias/(?P<alias>\w+)/$', views.lgAlias),
    (r'^link/(\d+)/$', viewWrapper(views.linkRedirect, requires_login=True)),
    (r'^underconstruction/$', views.underConstruction),
    (r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html', 'extra_context': {'STATIC_URL': settings.STATIC_URL}}),
    (r'^404/$', views.error404),
    (r'^robots.txt', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt'}),
    (r'^update_hot_feed', viewWrapper(views.updateHotFeedPage, requires_login=True)),

    # new home page
    (r'^$', views.redirect, {'page':"/home/"}),
#    (r'^home/$', viewWrapper(views.match, requires_login=True), {'section':"getInvolved"}),
    (r'^match/(?P<section>\w+)/$', viewWrapper(views.match, requires_login=True)),
    (r'^match/$', viewWrapper(views.match, requires_login=True)),

    # home pages
    (r'^my_city/$', viewWrapper(views.myCity, requires_login=True)),
    (r'^my_state/$', viewWrapper(views.myState, requires_login=True)),
    (r'^welcome/$', viewWrapper(views.welcome, requires_login=True)),
    (r'^home/$', viewWrapper(views.home, requires_login=True)),
    (r'^groups/$', viewWrapper(views.browseGroups, requires_login=True)),
    (r'^elections/$', viewWrapper(views.browseElections, requires_login=True)),
    (r'^politicians/$', viewWrapper(views.browseElections, requires_login=True)),
    (r'^representatives/$', viewWrapper(views.representatives, requires_login=True)),
    (r'^friends/$', viewWrapper(views.friends, requires_login=True)),
    (r'^questions/$', viewWrapper(views.questions, requires_login=True)),
    (r'^discover/$', viewWrapper(views.match, requires_login=True)),
    (r'^my_groups/$', viewWrapper(views.myGroups, requires_login=True)),
    (r'^my_elections/$', viewWrapper(views.myElections, requires_login=True)),
    (r'^like_minded/$', viewWrapper(views.likeMinded, requires_login=True)),

    # other main pages
    (r'^home/$', viewWrapper(views.redirect, requires_login=True)),
    (r'^web/$', viewWrapper(views.web, requires_login=True)),
    (r'^about/$', viewWrapper(views.about, requires_login=True)),
    (r'^settings/$', viewWrapper(views.account,requires_login=True)),
    (r'^settings/(?P<section>\S+)/$', viewWrapper(views.account,requires_login=True)),
    (r'^search/(?P<term>.*)/$', viewWrapper(views.search, requires_login=True)),

    # detail pages
    (r'^(?P<type>\w+)/(?P<content_id>\d+)/comment/(?P<comment_id>\d+)/$', viewWrapper(views.commentDetail, requires_login=True)),
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

    # scorecards
    (r'^scorecard/(\d+)/$', viewWrapper(views.scorecardDetail, requires_login=True)),
    (r'^scorecard/(\d+)/edit/$', viewWrapper(views.scorecardEdit, requires_login=True)),
    (r'^scorecard/(\d+)/me/$', viewWrapper(views.scorecardMe, requires_login=True)),
    (r'^scorecard/(\d+)/(\S+)/$', viewWrapper(views.scorecardCompare, requires_login=True)),

    # special pages
    (r'^profile/web/(\S+)/$', viewWrapper(views.compareWeb, requires_login=True)),              # profile/comparison
    (r'^group/(\d+)/edit/$', viewWrapper(views.groupEdit, requires_login=True)),
    (r'^group/(\d+)/edit/(?P<section>\S+)/$', viewWrapper(views.groupEdit, requires_login=True)),

    # legislation
    (r'^legislation/$', viewWrapper(views.legislation, requires_login=True)),
    (r'^legislation/(\d+)/$', viewWrapper(views.legislationDetail, requires_login=True)),

    # ajax pages
    (r'^action/$', viewWrapper(posts.actionPOST, requires_login=True)),
    (r'^answer/$', viewWrapper(views.profile, requires_login=True)),
    (r'^fb/action/$', viewWrapper(views.facebookAction, requires_login=True)),

    # widget pages
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                                     # widget api access

    # test pages
    (r'^test/$', viewWrapper(tests.fbTest, requires_login=True)),                                 # test page, for whatever you want!
    (r'^test2/$', viewWrapper(tests.test2, requires_login=True)),                               # for testing logging
    (r'^test3/$', viewWrapper(tests.test3, requires_login=True)),
    (r'^test4/$', viewWrapper(tests.test4, requires_login=True)),
    (r'^css/$', viewWrapper(tests.css, requires_login=True)),
    (r'^force_error/$', viewWrapper(tests.lgExceptionTest, requires_login=True)),          # force error page

    #admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),

    # api
    (r'^api/(?P<model>\S+)/$', viewWrapper(api.handleRequest)),

    # urls based on alias
    (r'(?P<alias>\w+)/edit/$', views.aliasDowncastEdit),
    (r'^(?P<alias>\w+)/worldview/$', viewWrapper(views.worldview, requires_login=True)),                 # view breakdown of person
    (r'^(?P<alias>\w+)/histogram/$', viewWrapper(views.histogramDetail, requires_login=True)),           # histogram detail of group
    (r'^state/(?P<state>\w+)/$', viewWrapper(views.state, requires_login=True)),

    # REDIRECT
    (r'^popup_redirect/$', views.popupRedirect),
    (r'(?P<alias>\w+)/$', views.aliasDowncast),
    (r'.*/$', views.error404)


)
