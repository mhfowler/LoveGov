#################################################################### everything below will never be reached ############

urlpatterns += patterns('',
    # BETA

    (r'^create_content/$', developmentWrapper(requiresLogin(createContent))),

    # register and login pages
    (r'^$', developmentWrapper(redirect_to), {'url': '/home'}),
    (r'^(\S+)/login/$', developmentWrapper(universalLogin)),
    (r'^login/$', developmentWrapper(universalLogin)),
    (r'^logout/$', developmentWrapper(requiresLogin(logout))),
    (r'^register/$', developmentWrapper(register)),
    (r'^confirm/(\S+)$', confirm),
    (r'^development/(\S+)$', developmentLogin),
    (r'^development/$', developmentLogin),
    (r'^login/success/$', developmentWrapper(requiresLogin(displayProfile))),


    # pages
    (r'^profile/(\w+)/(\d+)/$', developmentWrapper(requiresLogin(displayProfile))),
    (r'^display/(\d+)/$',developmentWrapper(requiresLogin(displayContent))),
    (r'^questions/$',developmentWrapper(requiresLogin(qaweb))),
    (r'^create/$', developmentWrapper(requiresLogin(createSimple))),
    (r'^create_content/(\w+)/$', developmentWrapper(requiresLogin(createContent))),
    (r'^novavote/$', developmentWrapper(requiresLogin(aboutNovavote))),
    (r'^compare/(\d+)/(\d+)/$', developmentWrapper(requiresLogin(displayUserComparison))),
    (r'^worldview/(\d+)/$', developmentWrapper(requiresLogin(displayWorldView))),
    (r'^editinfo/$', developmentWrapper(requiresLogin(editInfo))),

    # user specific pages
    (r'^myinvolvement/$', developmentWrapper(requiresLogin(myInvolvement))),
    (r'^mygovernment/$', developmentWrapper(requiresLogin(myGovernment))),
    (r'^myprofile/$', developmentWrapper(requiresLogin(myProfile))),
    (r'^home/$', developmentWrapper(requiresLogin(testHome))),

    # actions
    (r'^action/$',developmentWrapper(requiresLogin(actionsPOST.actionPOST))),
    (r'^actionPOST/$',developmentWrapper(requiresLogin(actionsPOST.actionPOST))),

    # accesses
    (r'^actionGET/$', developmentWrapper(requiresLogin(actionsGET.actionGET))),

    # debug
    (r'^debug/debugUsers/$', developmentWrapper(debugUsers)),
    (r'^debug/actionGET/$',developmentWrapper(requiresLogin(viewAccess))),
    (r'^debug/cookies/$', developmentWrapper(viewCookies)),
    (r'^debug/debugLinked/$', developmentWrapper(debugLinked)),
    (r'^debug/debugFriends/$', developmentWrapper(debugFriends)),
    (r'^debug/debugRelationships/$', developmentWrapper(debugRelationships)),
    (r'^debug/debugFeedback/$', developmentWrapper(debugFeedback)),
    (r'^debug/debugNotifications/$', developmentWrapper(requiresLogin(debugNotifications))),

    # search
    (r'^search/', include('haystack.urls')),

    # new test pages
    (r'^deploy/register$', developmentWrapper(deployRegister)),
    (r'^deploy/search$', developmentWrapper(deploySearch)),

    # test pages
    (r'^testFacebook/$',developmentWrapper(facebookRegister)),
    (r'^test_image/$',developmentWrapper(testImage)),
    (r'^test_thread/(\d+)$', developmentWrapper(displayThread)),
    (r'^test_ajax/$', developmentWrapper(test_ajax)),
    (r'^login_old/$', developmentWrapper(loginUser_old)),
    (r'^test_home/$', developmentWrapper(testHome)),
    (r'^test_data/$', developmentWrapper(testSaveData)),
    (r'^time/$', developmentWrapper(current_datetime)),
    (r'^zero/$', developmentWrapper(iterate_num)),
    (r'^form/$', developmentWrapper(form)),
    (r'^search/$', developmentWrapper(searchret)),
    (r'^zero/$', developmentWrapper(iterate_num)),
    (r'^inherit/$', developmentWrapper(test_inherit)),
    (r'^time/$', developmentWrapper(current_datetime)),
    (r'^feed/$', developmentWrapper(feed)),
    (r'^getFeed/$', developmentWrapper(actionsGET.getFeed)),
    (r'^qaweb/$', developmentWrapper(qaweb)),
    (r'^getQuestion/$', developmentWrapper(actionsGET.getQuestion)),
    (r'^debates/(\d+)/$', developmentWrapper(requiresLogin(debates))),
    (r'^testfeed/$', developmentWrapper(testfeed)),
    (r'^testJ/$', testJ),
    (r'^rolls/$', billroll),


)
