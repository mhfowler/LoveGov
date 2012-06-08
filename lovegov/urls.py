# external
from django.conf.urls.defaults import patterns, include, url
from django.contrib.admin import site
from django.contrib import admin
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic.simple import redirect_to

import haystack

# internal
from lovegov.beta.modernpolitics import actionsPOST
from lovegov.alpha.splash import views as alphaviews
from lovegov.alpha.splash import views_admin as splash_admin
from lovegov.beta.modernpolitics import actionsGET
from lovegov.alpha.splash import tests
from lovegov.alpha.splash.views import requiresLogin
from lovegov.beta.modernpolitics import lgwidget
from lovegov.local_manage import LOCAL



admin.autodiscover()


urlpatterns = patterns('',

    ## SPLASH ###
    (r'^comingsoon/$', alphaviews.splash),
    (r'^learnmore/$', alphaviews.learnmore),
    (r'^postEmail/$',alphaviews.postEmail))

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


    ### outside of login ###
    (r'^register/$',alphaviews.register),                                       # register page
    (r'^login/(?P<to_page>\S*)$',alphaviews.login),                             # login
    (r'^confirm/(?P<confirm_link>\S+)$', alphaviews.confirm),                   # confirm
    (r'^privacypolicy/$', alphaviews.privacyPolicy),                            # privacy
    (r'^fb/action/$', requiresLogin(alphaviews.facebookAction) ),
    (r'^fb/authorize/$', alphaviews.facebookAuthorize ),
    (r'^fb/handle/$', alphaviews.facebookHandle),

    ### main pages ###
    (r'^home/$', requiresLogin(alphaviews.home)),                               # home page with feeds
    (r'^web/$', requiresLogin(alphaviews.web)),                                 # big look at web
    (r'^about/$', requiresLogin(alphaviews.about)),                             # about
    (r'^account/$', requiresLogin(alphaviews.account)),                         # account/change password
    (r'^match/$', requiresLogin(alphaviews.match)),                             # match page
    (r'^matchNew/$', requiresLogin(alphaviews.matchNew)),
    (r'^loginNew/$', requiresLogin(alphaviews.loginNew)),

    ### content pages ####
    (r'^question/(\d+)/$', requiresLogin(alphaviews.questionDetail)),           # question detail
    (r'^topic/(\S+)/$', requiresLogin(alphaviews.topicDetail)),                 # topic detail
    (r'^petition/(\d+)/$', requiresLogin(alphaviews.petitionDetail)),           # petition detail
    (r'^news/(\d+)/$', requiresLogin(alphaviews.newsDetail)),                   # news detail
    (r'^network/(\S+)/$', requiresLogin(alphaviews.network)),                   # network page
    (r'^network/$', requiresLogin(alphaviews.network)),                         # network page
    (r'^profile/web/(\S+)/$', requiresLogin(alphaviews.compareWeb)),            # profile/comparison
    (r'^profile/(\S+)/$', requiresLogin(alphaviews.profile)),                   # profile/comparison
    (r'^nextquestion/$', requiresLogin(alphaviews.nextQuestion)),               # sensibly redirects to next question

    # ajax pages
    (r'^logout/$', requiresLogin(alphaviews.logout)),                           # logout
    (r'^action/$', requiresLogin(actionsPOST.actionPOST)),                      # comment and other actions
    (r'^actionGET/$', requiresLogin(actionsGET.actionGET)),                     # comment and other actions
    (r'^answer/$', requiresLogin(alphaviews.profile)),                          # comment and other actions
    (r'^ajax/feed$', requiresLogin(alphaviews.ajaxFeed)),                       # ajax get feed
    (r'^ajax/$', requiresLogin(alphaviews.ajaxSwitch)),                         # ajax switcher

    # widget pages
    (r'^widget/about/$', alphaviews.widgetAbout),                               # widget about page
    (r'^widget/$', redirect_to, {'url':"/widget/about/"}),                      # widget about page
    (r'^widget/access/$', lgwidget.access),                                     # widget api access

    # test pages
    (r'^test/$', requiresLogin(tests.test)),                                    # test page, for whatever you want!
    (r'^test2/$', tests.test2 ),                                                # for testing logging

    #admin
    (r'^developer/$', requiresLogin(splash_admin.adminHome)),
    (r'^alpha/admin_action/$', requiresLogin(splash_admin.adminAction)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(site.urls)),


    ## REDIRECT
    (r'.*', alphaviews.redirect))


