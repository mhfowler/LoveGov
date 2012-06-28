/***********************************************************************************************************************
 *
 *      ~Ajaxify
 *
 ***********************************************************************************************************************/
var rebind;

function rebindFunction()
{
    $(window).unbind('scroll');                                 // to unbind fix feed loading and qaweb scroll binding
    loadTopicSelect();                                          // topic select image functionality
    loadHoverComparison();                                      // hover comparison functionality
    loadAjaxifyAnchors();                                       // ajaxify all <a> tags with attribute "href"
    loadMenuToggles();                                          // menu toggles, have triangle, when clicked show menu child
    bindTooltips();                                             // bind all tooltip classes
    bindInlineEdits();
    switch (rebind)
    {
        case 'question':                                        // /question/#
            loadThread();
            loadQuestion();
            loadRightSideBar();
            break;
        case 'petition':                                        // /petition/#
            loadPetition();
            loadThread();
            loadRightSideBar();
            break;
        case 'news':                                            // /news/#
            loadThread();
            loadRightSideBar();
            break;
        case 'topic':                                           // /topic/<topic_name>
            loadRightSideBar();
            loadThread();
            break;
        case 'feed':                                            // /feed
            loadNewFeed();
            loadRightSideBar();
            break;
        case 'about':                                           // /about
            loadAbout();
            break;
        case 'match':                                           // /match
            loadUserList();
            loadGoogleMap();
            break;
        case 'qaweb':                                           // /web
            loadQAWeb();
            break;
        case 'profile':                                         // /profile/<alias>
            loadProfile();
            if( p_id != view_id )
            {
                loadProfileComparison();
            }
            break;
        case 'group':
            loadProfileComparison();
            loadGroup();
            break;
        case 'account':                                         // /account
            loadAccount();
            break;
        default:
            break
    }
}


/***********************************************************************************************************************
 *
 *      ~Bind popovers
 *
 ***********************************************************************************************************************/

function bindTooltips() {
    $(".tooltip-top").tooltip({'placement': 'top', 'animation': 'true'});
    $(".tooltip-bottom").tooltip({'placement': 'bottom', 'animation': 'true'});
    $(".tooltip-right").tooltip({'placement': 'right', 'animation': 'true'});
    $(".tooltip-left").tooltip({'placement': 'left', 'animation': 'true'});
}


/***********************************************************************************************************************
 *
 *      ~Menu and Icon Display
 *
 ***********************************************************************************************************************/
function loadMenuToggles() {

    $(".menu").hide();
    $(".menu_toggle").click(function(event) {
        if (!$(this).hasClass("clicked")) {
            var other_menu_toggles = $(".menu_toggle").not($(this));
            other_menu_toggles.removeClass("clicked");
            other_menu_toggles.children(".menu").hide();
        }
        $(this).children(".menu").toggle();
    });
    $(".menu_toggle").hover(
        function(event) {
            $(this).children(".triangle-selector").addClass("highlighted");
        },
        function(event) {
            if (!$(this).hasClass("clicked")) {
                $(this).children(".triangle-selector").removeClass("highlighted");
            }
        }
    );
    defaultHoverClick($(".menu_toggle"));
}

function defaultHoverClick(div) {
    div.click(function(event) {
        defaultClick($(this));
    });
    defaultHover(div);
}

function defaultHoverClickSingle(div) {
    div.click(function(event) {
        defaultClickSingle($(this), div);
    });
    defaultHover(div);
}

function defaultClickSingle(this_div, all_div) {
    var already = $(this).hasClass("clicked");
    all_div.removeClass("clicked");
    if (!already) {
        this_div.addClass("clicked");
    }
}

function defaultClick(this_div) {
    this_div.toggleClass("clicked");
}

function defaultHover(all_div) {
    all_div.hover(
        function(event) {
            $(this).addClass("hovered");
        },
        function(event) {
            $(this).removeClass("hovered");
        }
    );
}


/***********************************************************************************************************************
 *
 *      ~Following
 *
 ***********************************************************************************************************************/
/* user follower */
function userFollow(event,div,follow)
{
    event.preventDefault();
    div.unbind();
    var action = 'userfollow';
    if( !follow )
    {
        action = 'stopfollow';
    }
    ajaxPost({
            data: {
                'action': action,
                'p_id': p_id
            },
            success: function(data)
            {
                if( data == "follow success")
                {
                    div.html("unfollow");
                    div.click(
                        function(event)
                        {
                            userFollow(event,div,false);
                        }
                    );
                }
                else if( data == "follow request")
                {
                    div.html("un-request");
                    div.click(
                        function(event)
                        {
                            userFollow(event,div,false);
                        }
                    );
                }
                else if( data == "follow removed")
                {
                    div.html("follow");
                    div.click(
                        function(event)
                        {
                            userFollow(event,div,true);
                        }
                    );
                }
                else
                {
                    alert(data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        }
    );
}

function groupFollow(event,div,follow)
{
    event.preventDefault();
    div.unbind();
    var action = 'joingroup';
    if( !follow )
    {
        action = 'leavegroup';
    }
    ajaxPost({
            data: {
                'action': action,
                'g_id': g_id
            },
            success: function(data)
            {
                if( data == "follow success")
                {
                    div.html("unfollow");
                    div.click(
                        function(event)
                        {
                            groupFollow(event,div,false);
                        }
                    );
                }
                else if( data == "follow request")
                {
                    div.html("un-request");
                    div.click(
                        function(event)
                        {
                            groupFollow(event,div,false);
                        }
                    );
                }
                else if( data == "follow removed")
                {
                    div.html("follow");
                    div.click(
                        function(event)
                        {
                            groupFollow(event,div,true);
                        }
                    );
                }
                else
                {
                    alert(data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        }
    );
}

function userFollowResponse(event,response,div)
{
    event.preventDefault();
    var follow_id = div.siblings(".user-follow-id").val();
    ajaxPost({
            data: {
                'action':'followresponse',
                'p_id': follow_id,
                'response': response
            },
            success: function(data)
            {
                alert(data);
            },
            error: function(error, textStatus, errorThrown)
            {
                $('body').html(error.responseText);
            }
        }
    );
}

function groupInviteResponse(event,response,div)
{
    event.preventDefault();
    var g_id = div.siblings(".group-join-id").val();
    ajaxPost({
            data: {
                'action':'groupinviteresponse',
                'g_id': g_id,
                'response': response
            },
            success: function(data)
            {
                alert(data);
            },
            error: function(error, textStatus, errorThrown)
            {
                $('body').html(error.responseText);
            }
        }
    );
}

function setFollowPrivacy(event,private_follow,div)
{
    event.preventDefault();
    div.unbind();
    ajaxPost({
        data: {
            'action':'followprivacy',
            'p_id': p_id,
            'private_follow': private_follow
        },
        success: function(data)
        {
            if( data == "follow privacy set")
            {
                if( private_follow )
                {
                    div.html("private");
                    div.click(
                        function(event)
                        {
                            setFollowPrivacy(event,0,$(this));
                        }
                    );
                }
                else
                {
                    div.html("public");
                    div.click(
                        function(event)
                        {
                            setFollowPrivacy(event,1,$(this));
                        }
                    );
                }
            }
            else
            {
                alert(data);
            }

        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('body').html(jqXHR.responseText);
        }

    });
}

/***********************************************************************************************************************
 *
 *      ~InlineEdits
 *
 ***********************************************************************************************************************/
function editUserProfile(info,edit_div)
{
    var prof_data = info;
    prof_data.action = 'editprofile';

    ajaxPost({
        'data': prof_data,
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            if( obj.success )
            {
                edit_div.text(obj.value);
                edit_div.show();
            }
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('body').html(jqXHR.responseText);
        }
    });
}


function editContent(c_id,info,edit_div)
{
    var content_data = info;
    content_data.action = 'editcontent';
    content_data.c_id = c_id;

    ajaxPost({
        'data': content_data,
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            if( obj.success )
            {
                edit_div.text(obj.value);
                edit_div.show();
            }
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('body').html(jqXHR.responseText);
        }
    });
}

function bindInlineEdits()
{
    $(".edit_button").click(
        function(event)
        {
            event.preventDefault();
            $(this).siblings('.inline_hide').hide();
            $(this).hide();
            $(this).siblings('.inline_edit').show();
        }
    );

    $(".submit_inline_edit").click(
        function(event)
        {
            event.preventDefault();
            var input = $(this).siblings('.edit_input');
            var wrapper = $(this).parent();
            var name = input.attr('name');
            var value = input.val();
            var model = wrapper.data('model');
            var info = {
                'key':name,
                'val':value
            };
            var edit_div = $(this).parent().siblings('.inline_hide');

            if( model == "Content" )
            {
                var c_id = wrapper.data('id');
                editContent(c_id,info,edit_div);
            }
            else if( model == "UserProfile")
            {
                editUserProfile(info,edit_div);
            }

            $(this).parent().siblings('.edit_button').show();
            $(this).parent().hide();
        }
    );
}



/***********************************************************************************************************************
 *
 *      ~General
 *
 ***********************************************************************************************************************/
function loadHoverComparison()
{

    var hoverTimer;

    function clearHover()
    {
        $('#comparison-hover').empty();
        $('#comparison-hover-div').fadeOut(100);
    }

    $('#comparison-hover-div').hoverIntent
    (
        function() { clearTimeout(hoverTimer); },
        function() { hoverTimer = setTimeout(function(){clearHover();},100)}
    );

    function findHoverPosition(selector)
    {
        var top = selector.offset().top - $('#comparison-hover-div').height() - 30;
        if (top <= $(document).scrollTop())
        {
            // show below
            top = selector.offset().top + selector.height() + 30;
            $('#comparison-hover-pointer-up').show(); $('#comparison-hover-pointer-down').hide();
        }
        else
        {
            // show above
            $('#comparison-hover-pointer-up').hide(); $('#comparison-hover-pointer-down').show();
        }
        var left = selector.offset().left - ($('#comparison-hover-div').width()/2) + (selector.width()/2);
        return {top:top,left:left};
    }

    var to_hover = $('.has_hover_comparison').not('.already_hover');
    to_hover.addClass('already_hover');
    to_hover.hoverIntent
    (
        function(event)
        {
            var self = $(this);
            var href = $(this).data('href');
            var displayName = $(this).data("display_name");
            if (href != "")
            {
                clearTimeout(hoverTimer);
                $('#comparison-hover').empty();
                var offset = findHoverPosition(self);
                $('#comparison-hover-div p').text('You & ' + displayName);
                $('#comparison-hover-loading-img').show();
                $('#comparison-hover-div').fadeIn(100);
                $('#comparison-hover-div').offset(offset);
                ajaxPost({
                    'data': {'action':'hoverComparison','href':href},
                    'success': function(data)
                    {
                        var obj = eval('(' + data + ')');
                        $('#comparison-hover-loading-img').hide();
                        new VisualComparison('comparison-hover',obj).draw();
                    },
                    'error': function(jqXHR, textStatus, errorThrown)
                    {
                        $('#comparison-hover-div p').text('Sorry there was an error');
                    }
                });
            }
        },
        function(event)
        {
            hoverTimer = setTimeout(function()
            {
                $('#comparison-hover').empty();
                $('#comparison-hover-div').fadeOut(100);
            },500)
        }
    );
}



// loads topic bar select functionality
function loadTopicSelect()
{
    // hide all selected
    $(".selected").hide();

    // hover
    $(".topic-img").hover
        (
            function(event)
            {
                var wrapper = $(this).parents(".topic-icon-wrapper");
                wrapper.children(".normal").hide();
                wrapper.children(".selected").show();
            },
            function(event)
            {
                var wrapper = $(this).parents(".topic-icon-wrapper");
                if (!(wrapper.hasClass("chosen")))
                {
                    wrapper.children(".selected").hide();
                    wrapper.children(".normal").show();
                }
            }
        );
}

// selects a particular topic icon and deselects all others
function selectTopicSingle(wrapper)
{
    var icons_wrapper = wrapper.closest(".topic-icons-wrapper");
    clearTopicIcons(icons_wrapper);
    showTopicIcon(wrapper);
}

// clears all topic icons within an overall topic-icons-wrapper
function clearTopicIcons(icons_wrapper) {
    var icons = icons_wrapper.find(".topic-icon-wrapper");
    icons.each(function(index) {
        hideTopicIcon($(this));
    });
}

// toggles topic icon between being selected and unselected
function toggleTopicIcon(wrapper)
{
    if (wrapper.hasClass("chosen")) {
        hideTopicIcon(wrapper);
    }
    else {
        showTopicIcon(wrapper);
    }
}

function hideTopicIcon(wrapper) {
    wrapper.removeClass("chosen");
    wrapper.children(".selected").hide();
    wrapper.children(".normal").show();
}

function showTopicIcon(wrapper) {
    wrapper.addClass("chosen");
    wrapper.children(".selected").show();
    wrapper.children(".normal").hide();
}


function loadAjaxifyAnchors()
{
    $('.do-ajax-link').off('click',  ajaxClicked);
    var ajaxClicked = function(event) {
        var elem = event.target;
        var href = $(elem).attr('href');
        if (
            href != undefined &&
                href != "" &&
                href.indexOf("http://") == -1 &&
                href != "#")
        {
            event.preventDefault();
            if (!$(elem).parent().hasClass("top-links")) { $('.top-links').children('a').removeAttr('style'); }
            $('#comparison-hover').empty();
            $('#comparison-hover-div').hide();
            ajaxLink($(elem), true);
            return false;
        }
    }
    $('.do-ajax-link').on('click',  ajaxClicked);
}
/***********************************************************************************************************************
 *
 *      ~DocumentReady
 *
 ***********************************************************************************************************************/

$(document).ready(function()
{
    // csrf protect
    $.ajaxSetup({ data: {csrfmiddlewaretoken: csrf} });

    // Prepare
    var History = window.History; // Note: We are using a capital H instead of a lower h
    if ( !History.enabled )
    {
        // History.js is disabled for this browser.
        // This is because we can optionally choose to support HTML4 browsers or not.
        return false;
    }
    // Bind to StateChange Event
    History.Adapter.bind(window,'statechange',function()
    {
        // Note: We are using statechange instead of popstate
        var State = History.getState(); // Note: We are using History.getState() instead of event.state
        History.log(State.data, State.title, State.url);
    });

    // back button reload
    window.onpopstate = function(event)
    {
        if (event.state != null) { window.location.reload(); }
    };

    if (pageTitle != "")
    {
        document.title = pageTitle;
    }

    // universal frame binding
    rebindUniversalFrame();
    // page specific bindings
    rebindFunction()
});

// load universal frame
function rebindUniversalFrame()
{
    loadHeader();
    loadLeftSidebar();
}

/**
 * Ajaxifies a link.  Note this function can accept multiple input formats
 *
 * @param div       <a> jQuery object or a url as a String
 * @param loadimg   the loading image div
 */
function ajaxLink(div, loadimg)
{
    var link;
    if (div instanceof jQuery && div.attr('href')){ link = div.attr("href"); }
    else { link = div;}
    ajaxReload(link, loadimg);
}

// wrapper for ajax post
function ajaxPost(dict) {
    var data = dict['data'];
    var success_fun = dict['success'];
    var error_fun = dict['error'];
    if (error_fun == null) {
        error_fun = function(jqXHR, textStatus, errorThrown) { $('body').html(jqXHR.responseText); };
    }
    data['url'] = window.location.href;
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: data,
        success: success_fun,
        error: error_fun
    });
}

// ajax load home page
function ajaxReload(theurl, loadimg)
{
    $('#search-dropdown').hide();
    $('#main-content').hide();
    if (loadimg) { $("#loading").show(); }
    $.ajax
        ({
            url:theurl,
            type: 'GET',
            data: {'url':window.location.href},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                History.pushState( {k:1}, returned.title, returned.url);
                if (loadimg) { $("#loading").hide(); }
                replaceCenter(returned.html);
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
}

// for ajax loading of pages - this function only changes content in center of page
function replaceCenter(stuff)
{
    $('body').css("overflow","scroll");
    $('#main-content').css("top","0px");
    $("#main-content").html(stuff);
    $('#main-content').show();
    rebindFunction();
}


/***********************************************************************************************************************
 *
 *     ~Header
 *
 **********************************************************************************************************************/
function loadHeader()
{

    var timeout;
    var delay = 750;
    var isLoading = false;
    var currentSearch;
    $('#searchbar').bind('keyup',function()
    {
        var text = $(this).val();
        if (timeout) { clearTimeout(timeout); }
        if (!isLoading && text != currentSearch)
        {
            timeout = setTimeout(function()
            {
                isLoading = true;
                $("#autocomplete-loading-gif").show();
                ajaxPost({
                    data: {'action':'searchAutoComplete','string':text},
                    success: function(data)
                    {
                        var obj = eval('(' + data + ')');
                        $("#autocomplete-loading-gif").hide();
                        $('#search-dropdown').html(obj.html);
                        $('#search-dropdown').fadeIn('fast');
                    },
                    error: function(jqXHR, textStatus, errorThrown)
                    {
                        $("#autocomplete-loading-gif").hide();
                        $('#search-dropdown').empty();
                        $('#search-dropdown').hide();
                    }
                });
                // Simulate a real ajax call
                setTimeout(function() { isLoading = false; }, delay);
            }, delay);
        }
    });

    $('#search-dropdown').bind('clickoutside',function(event)
    {
        if (event.target.id != 'searchbar')
        {
            $(this).empty();
            $(this).hide();
        }
    });


    $('#searchbar').inputFade();


    var tempDropDownDiv = $('.notifications-dropdown-static-div');
    $('#notifications-dropdown-button').click(
        function(event)
        {
            var dropdown = $('#notifications-dropdown');
            dropdown.empty().append(tempDropDownDiv);
            $('.notifications-ajax-load').show();
            event.preventDefault();
            var pos = $(this).offset();
            dropdown.toggle();

            if( $('#notifications-dropdown').is(':visible') )
            {
                pos.left = (pos.left-dropdown.width()/2)+($(this).width()/2);
                pos.top = dropdown.offset().top;
                $('#notifications-dropdown').offset(pos);
                ajaxPost({
                    'data': {'action':'getnotifications',
                        'dropdown':'true'},
                    success: function(data)
                    {
                        var obj = eval('(' + data + ')');
                        $('.notifications-ajax-load').hide();
                        $('#notifications-dropdown').empty().append(tempDropDownDiv).append(obj.html);
                        unbindNotification();
                        loadNotification();
                        loadAjaxifyAnchors();
                    },
                    error: function(jqXHR, textStatus, errorThrown)
                    {
                        $('body').html(jqXHR.responseText);
                    }
                });
            }
            event.stopPropagation();
            hideOtherDropDowns(dropdown);
        }
    );

    function hideOtherDropDowns(exclude)
    {
        $('.drop_down').each(function()
        {
            if (!$(this).is(exclude))
            {
                $(this).hide();
            }
        });
    }

    $('#notifications-dropdown').bind('clickoutside',function(event)
    {
        if ($('#notifications-dropdown').css("display") != "none")
        {
            $('#notifications-dropdown').empty().append(tempDropDownDiv);
            $(this).hide();
        }
    });


    $('#logo-img').hover
    (
        function(){ $(this).attr('src','/static/images/top-logo-hover.png'); },
        function(){ $(this).attr('src','/static/images/top-logo-default.png'); }
    );

    function toggleUserMenu()
    {
        $('.user-menu').toggleClass("user-menu-unselected");
        $('.user-menu').toggleClass("user-menu-selected");
        $("#user-menu-dropdown").toggle('slide',{direction:'up'},10);
        hideOtherDropDowns($('#user-menu-dropdown'));
        var left = $('#user-menu-dropdown').width()-$('.user-menu').width()+$('.user-img').width()+$('#user-name').width()/2-$('.user-menu-pointer').width()/2;
        $('.user-menu-pointer').css('left',left);
    }

    $('#user-menu-dropdown').bind("clickoutside",function(event)
    {
        if ($('#user-menu-dropdown').css('display') != 'none')
        {
            $('#user-menu').removeClass("user-menu-selected");
            $('#user-menu').addClass("user-menu-unselected");
            $('#user-menu-dropdown').hide();
        }
    });

    $('.user_menu_dropdown').click(function(event)
    {
        toggleUserMenu();
        event.stopPropagation();
    });


    if ($.cookie('privacy'))
    {
        switch($.cookie('privacy'))
        {
        case "PUB":
            $.cookie('privacy','PUB', {path:'/'});
            $(".security_setting").each(function()
            {
                if ($(this).is('img')) { $(this).attr("src","/static/images/public.png") }

            });
            break;
        case "PRI":
            $.cookie('privacy','PRI', {path:'/'});
            $(".security_setting").each(function()
            {
                if ($(this).is('img')) { $(this).attr("src","/static/images/user-menu/lockgray.png") }
            });
            break;
        }
    }
    else
    {
        $.cookie('privacy','PUB', {path:'/'});
        $(".security_setting").each(function()
        {
            if ($(this).is('img')) { $(this).attr("src","/static/images/public.png") }

        });
    }



    $(".security_setting").click(function(event)
    {

        switch($.cookie('privacy'))
        {
            case "PUB":
                $.cookie('privacy','PRI', {path:'/'});
                $(".security_setting").each(function()
                {
                    if ($(this).is('img')) { $(this).attr("src","/static/images/user-menu/lockgray.png") }
                });
                break;
            case "PRI":
                $.cookie('privacy','PUB', {path:'/'});
                $(".security_setting").each(function()
                {
                    if ($(this).is('img')) { $(this).attr("src","/static/images/public.png") }
                });
                break;
        }
    });


    /**
     * Handles styling of header links
     *
     * @param linkElement
     */
    function applySelectLinkStyle(linkElement)
    {
        $('.top-links').children('a').removeAttr('style');
        linkElement.css({color:'#ffffff','padding-top':"10px",'padding-bottom':"6px",'background-color':'#f0503b'});
    }
    // ajax link home page
    $("#home-link").click(function(event)
    {
        $('.top-links').children('a').removeAttr('style');
        return false;
    });
    // ajax link home page
    $("#web-link").click(function(event)
    {
        applySelectLinkStyle($(this));
        return false;
    });
    // ajax link home page
    $("#about-link").click(function(event)
    {
        applySelectLinkStyle($(this));
        return false;
    });
    // ajax link match page
    $("#match-link").click(function(event)
    {
        applySelectLinkStyle($(this));
        return false;
    });
}

/***********************************************************************************************************************
 *
 *     ~LeftSidebar
 *
 **********************************************************************************************************************/
var regUrl = /^(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;

function convert(str)
{
    str = str.replace(/&amp;/g, "&");
    str = str.replace(/&gt;/g,">");
    str = str.replace(/&lt;/g,"<");
    str = str.replace(/&quot;/g,'"');
    str = str.replace(/&#039;/g,"'");
    return str;
}

function closeLeftSideWrapper(wrapper)
{
    if (wrapper.hasClass('clicked'))
    {
        wrapper.removeClass('clicked');
        if (wrapper.hasClass('create-wrapper-large')) { wrapper.animate({left:'-603px'},500); }
        else { wrapper.animate({left:'-493px'},500); }
        setTimeout(function()
        {
            wrapper.css({'z-index':'100'});
            wrapper.children('.create-img').css({'z-index':'101'});
        },500);
    }
}

function loadLeftSidebar()
{

    $('.left-side-img').click(function()
    {
        var parent = $(this).parent();
        if (parent.hasClass('clicked'))
        {
            closeLeftSideWrapper(parent);
        }
        else
        {
            parent.addClass('clicked');
            parent.css({'z-index':'101'});
            parent.children('.create-img').css({'z-index':'102'});
            parent.animate({left:'-1px'},500);
        }
    });

    $('.left-side-wrapper').bind('clickoutside',function()
    {
        var wrapper = $(this);
        if (wrapper.hasClass('clicked')) { closeLeftSideWrapper(wrapper); }
    });

    $('#feedback-submit').click(function(event)
    {
        event.preventDefault();
        var text = $('#feedback-text').val();
        var name = $('#feedback-name').val();
        ajaxPost({
            data: {'action':'feedback','text':text,'path':path,'name':name},
            success: function(data)
            {
                $('#feedback-name').val("");
                $('#feedback-text').val("");
                $('#feedback-response').css('display','block');
                $('#feedback-response').fadeOut(3000);
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                alert("failure");
            }
        });
    });

    function sendInvitation(event)
    {
        event.preventDefault();
        var email = $("#email-input").val();
        $("#invite-return-message").text("");
        $("#invite-return-loading-img").show();
        ajaxPost({
            data: {'action':'invite','email':email},
            success: function(data)
            {
                $("#invite-return-loading-img").hide();
                $("#invite-return-message").text("Invitation Sent!");
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("#invite-return-loading-img").hide();
                $("#invite-return-message").text("Server Error, Did Not Send.");
            }
        });
    }


    $('#email-input').keydown(function(event)
    {
        if (event.keyCode == 13)
        {
            sendInvitation(event);
        }
    });

    $("#invite-button").click(function(event)
    {
        sendInvitation(event);
    });
}

/***********************************************************************************************************************
 *
 *     ~Share Button
 *
 **********************************************************************************************************************/
function loadShareButton() {
    $('div.overdiv').appendTo('body');
    $('div.shareModal').appendTo('body');

    $('.share_button').bindOnce('click.share', function(event) {
        event.preventDefault();
        $("#share_id").data('share_id', $(this).data('share_id'));
        $('div.overdiv').fadeToggle("fast");
        $('div.shareModal').fadeToggle("fast");
    });

    $('div.overdiv').bindOnce('click.hide_overdiv', function() {
        $('div.overdiv').hide();
        $('div.shareModal').hide();
    });
}
/***********************************************************************************************************************
 *
 *     ~RightSidebar
 *
 **********************************************************************************************************************/
var right_sidebar_topic = 'all';

function loadRightSideBar()
{
    // select topic click function
    $(".q-topic-img").click(function(event) {
        var wrapper = $(this).parents(".topic-icon-wrapper");
        selectTopicSingle(wrapper);
    });

    // sidebar stuff, for question-topic select
    $(".topic-div").hide();

    // if page has a topic then show questions of that topic
    if (right_sidebar_topic!='all')
    {
        var alias_div = $('input[value="' + right_sidebar_topic + '"]');
        selectQuestionTopic(alias_div.siblings(".normal"));
    }
    // else show questions of all topics
    else
    {
        $("#topic-all").show();
    }

    // click and change topic question div
    $(".q-topic-img").click(function(event)
    {
        selectQuestionTopic($(this));
    });

    // hides all other topic divs, and shows random topic div
    $("#all-topics-button").click(function(event) {
        var wrapper =  $(".q-topics-wrapper");
        wrapper.find(".selected").hide();
        wrapper.find(".normal").show();
        $(".topic-div").hide();
        $("#topic-all").show();
        topics=[];

    });
}

// shows questions from the selected topic and calls select topic to adjust icons appropriately
function selectQuestionTopic(div)
{
    var t = div.siblings(".t-alias").val();
    $(".topic-div").hide();
    $("#topic-"+t).fadeIn();
}



/***********************************************************************************************************************
 *
 *      ~Question
 *
 ***********************************************************************************************************************/
function loadQuestion()
{
    // submit answer
    $("#submitquestion").click(function(event)
    {
        event.preventDefault();
        var checked = false;
        $('.answer-container').find('input').each(function()
        {
            if ($(this).prop("checked"))
            {
                checked = true;
            }
        });

        $("#questionform").submit();

    });

    // answer select
    $('.answer-container').find('input').each(function()
    {
        if ($(this).prop("checked"))
        {
            $(this).parent().parent().addClass("answer-container-selected");
        }
    });

    $('.answer-container').hover
        (
            function()
            {
                $(this).addClass("answer-container-hover");
            },
            function()
            {
                $(this).removeClass("answer-container-hover");
            }
        );

    // answer click
    $('input').click(function(event)
    {
        event.preventDefault();
    });

    $('.answer-container').click(function()
    {
        $('.answer-container').removeClass("answer-container-selected");

        if ($(this).find('input').prop('checked'))
        {
            $(this).find('input').prop("checked", false);
            $(this).removeClass("answer-container-selected");
            $(this).removeClass("answer-container-hover");
        }
        else
        {
            $(this).find('input').prop("checked", true);
            $(this).addClass("answer-container-selected");
        }

        // submit
        submitAnswer();
    });
}

function submitAnswer()
{
    var choice = $('input:radio[name=choice]:checked').val();
    var q_id = c_id;
    var explanation = "";
    var weight = 5;
    // var exp = $("#explanation").val();
    ajaxPost({
        data: {'action':'answer','q_id': q_id,'choice':choice,'weight':weight,'explanation':explanation},
        success: function(data) {
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}

/***********************************************************************************************************************
 *
 *      ~Thread
 *
 ***********************************************************************************************************************/
// binding for thread
function loadThread()
{ 
	heartButtons();
    // comment submit
    $(".submit-comment").unbind();
    $(".submit-comment").click(function(event)
    {
        event.preventDefault();
        $(this).parent().submit();
    });

    // new comment submit
    $('#commentform').unbind();
    $("#commentform").submit(function(event)
    {
        event.preventDefault();
        var comment_text = $(this).children(".comment-textarea").val();
        var comment_text_length = comment_text.length;
        if (comment_text_length <= 1000)
        {
            $(this).children(".comment-textarea").val("");
            var content_id = $("#content_id").val();
            ajaxPost({
                'data': {'action':'postcomment','c_id': content_id,'comment':comment_text},
                'success': function(data) {
                    ajaxThread();
                },
                'error': null
            });
        }
        else
        {
            alert("Please limit your response to 1000 characters.  You have currently typed " + comment_text_length + " characters.");
        }
    });

    // toggle reply form for comment
    $(".reply").click(function()
    {
        $(this).parent().siblings('.replyform').toggle();
    });
    
    // hide for "cancel" button
    $("input.tab-button.alt").click(function()
    {
        $(this).parent().hide();
    });

    // delete comment


    // like comment
    $(".commentlike").click(function(event)
    {
        event.preventDefault();
        var content_id = $(this).parent().parent().next().children(".hidden_id").val();
        $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
            function(data)
            {
                ajaxThread();
            });
    });

    // dislike comment
    $(".commentdislike").click(function(event)
    {
        event.preventDefault();
        var content_id = $(this).parent().parent().next().children(".hidden_id").val();
        $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
            function(data)
            {
                ajaxThread();
            });
    });

    // delete comment
    $(".commentdelete").click(function()
    {
        var content_id = $(this).children(".delete_id").val();
        $.post('/action/', {'action':'delete','c_id':content_id},
            function(data)
            {
                ajaxThread();
            });
    });


    // reply to comment
    $(".replyform").submit(function(event)
    {
        event.preventDefault();
        var comment_text = $(this).children(".comment-textarea").val();
        var comment_text_length = comment_text.length;
        if (comment_text_length <= 1000)
        {
            var content_id = $(this).children(".hidden_id").val();
            ajaxPost({
                data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
                success: function(data)
                {
                    ajaxThread();
                },
                error: null
            });
        }
        else
        {
            alert("Please limit your response to 1000 characters.  You have currently typed " + comment_text_length + " characters.");
        }
    });

    // comment text click function
    $(".comment-textarea").click(function()
    {
        if ($(this).val() == "what's your opinion?")
        {
            $(this).val("");
        }
    });

    $(".comment-textarea").bind("clickoutside", function(event)
    {
        if ($(this).val()=="")
        {
            $(this).val("what's your opinion?");
        }
        $(this).blur();
    });

    $('span.collapse').click(function(e) {
        var close = '[-]';
        var open = '[+]';
        if($(this).text()==close) { 
            $(this).text(open);
            $(this).next('div.threaddiv').children().hide();
        } else if($(this).text()==open) {
            $(this).text(close);
            $(this).next('div.threaddiv').children().show();
        }
    });

    $('span.flag').click(function(e) {
        var commentid = $(this).data('commentid');
        var comment = $(this).parent().children('div.comment-text').text();
        var conf = confirm("Are you sure you want to flag this comment?\n\n"+comment);
        if(conf) {
            ajaxPost({
                data: {'action': 'flag', 'c_id': commentid},
                success: function(data) {
                    alert(data);
                    $(this).css("color", "red");
                },
                error: function(data) {
                    alert("Flagging comment failed.");
                }
            });
        }
    });

    loadHoverComparison();
}

// ajax gets thread and replaces old thread
function ajaxThread()
{
    ajaxPost({
        data: {'action':'ajaxThread','type':'thread', 'c_id':c_id},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            $("#thread").html(returned.html);
            loadThread();
            return false;
        },
        error: null
    });
}

/***********************************************************************************************************************
 *
 *      ~UsersList
 *
 ***********************************************************************************************************************/
function loadUserList()
{
    $('.user-list-item').hover
        (
            function()
            {
                $(this).children('.user-list-item-name-big').addClass("user-list-item-hover");
            },
            function()
            {
                $(this).children('.user-list-item-name-big').removeClass("user-list-item-hover");
            }
        );
}

function loadGoogleMap()
{
    function createDistrictsOverlay(outlines_only, opacity, state, district)
    {
        return {
            getTileUrl: function(coord, zoom)
            {
                return "http://www.govtrack.us/perl/wms/wms.cgi?google_tile_template_values=" + coord.x + "," + coord.y + "," + zoom
                    + "&LAYERS=cd-110" + (outlines_only ? "-outlines" : "")
                    + (state ? ":http://www.rdfabout.com/rdf/usgov/geo/us/" + state
                    + (!district ? "%25"
                    : "/cd/110/" + district)
                    : "")
                    + "&FORMAT=image/png";
            },
            tileSize: new google.maps.Size(256,256),
            minZoom: 2,
            maxZoom: 28,
            opacity: opacity,
            isPng: true
        };
    }

    var map;

    function initialize()
    {
        var myOptions =
        {
            zoom: 10,
            center: new google.maps.LatLng(latitude, longtitude),
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            panControl: false,
            zoomControl: true,
            mapTypeControl: false,
            scaleControl: true,
            streetViewControl: false
        };
        map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

        overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(false, .2, state, district));
        map.overlayMapTypes.insertAt(0, overlayWMS);

        overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(true, .7, state, district));
        map.overlayMapTypes.insertAt(0, overlayWMS);
    }


    var map_canvas = "<div id='map_canvas' style='width:600px;height:750px'></div>";
    if (!$("#map_canvas").length) { $('#main-content').append(map_canvas); }
    initialize();
    if (!$('#map_canvas').hasClass('ui-dialog-content'))
    {
        $('#map_canvas').dialog
            ({
                height:600,
                width:750,
                resizable:false,
                autoOpen:false
            });
        $(".ui-dialog").bind("clickoutside", function(event) { if (event.target.id != 'see-congressional-map' && event.target.id != "map_canvas") { $("#map_canvas").dialog("close");  } });
    }

    $("#see-congressional-map").click(function(event)
    {
        if ($('#map_canvas').dialog("isOpen") == false)
        {
            $('#map_canvas').dialog('open');
            google.maps.event.trigger(map, 'resize');
        }
    });


}
/***********************************************************************************************************************
 *
 *      ~About
 *
 ***********************************************************************************************************************/
function loadAbout()
{
    $(".about-element").hover
        (
            function(){ $(this).css("background-color","#F0F0F0")},
            function(){ $(this).css("background-color","#FFFFFF")}
        );

    $(".about-hover-element").hover
        (
            function(){ $(this).css("background-color","#F0F0F0") },
            function(){ $(this).css("background-color","#FFFFFF") }
        );
}

/***********************************************************************************************************************
 *
 *      ~Notifications
 *
 ***********************************************************************************************************************/
function unbindNotification()
{
    $('.notification-user-follow').unbind();
    $('.notification-follow-response-y').unbind();
    $(".notificatton-follow-response-n").unbind();
}

function loadNotification()
{
    $(".notification-user-follow").click( function(event)
    {
        event.preventDefault();
        var follow_id = $(this).siblings(".user-follow-id").val();
        alert( follow_id );
        ajaxPost({
                data: {
                    'action':'userfollow',
                    'p_id': follow_id
                },
                success: function(data)
                {
                    alert(data);
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $('body').html(jqXHR.responseText);
                }
            }
        );
    });

    $(".notification-follow-response-y").click( function(event) {
        userFollowResponse(event,"Y",$(this));
    });

    $(".notification-follow-response-n").click( function(event) {
        userFollowResponse(event,"N",$(this));
    });

    $(".notification_group_response_y").click( function(event) {
        groupFollowResponse(event,"Y",$(this));
    });

    $(".notification_group_response_n").click( function(event) {
        groupFollowResponse(event,"N",$(this));
    });
}


/***********************************************************************************************************************
 *
 *      ~Profile
 *
 ***********************************************************************************************************************/
var prof_more_notifications = true;
var prof_more_actions = true;
var prof_more_groups = true;

function getMoreNotifications()
{
    if( prof_more_notifications )
    {
        prof_more_notifications = false;
        var num_notifications = $("#num_notifications").val();
        ajaxPost({
            'data': {'action':'getnotifications',
                'num_notifications':num_notifications },
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                $('#profile_notifications').append(obj.html);
                $('#num_notifications').val(obj.num_notifications);
                if( obj.hasOwnProperty('error') && obj.error == 'No more notifications' )
                {
                    $('#see_more_notifications').html('No more notifications');
                    $('#see_more_notifications').unbind();
                    $('#see_more_notifications').click( function(event)
                    {
                        event.preventDefault();
                    });
                }
                else if( obj.hasOwnProperty('error') )
                {
                    $('body').html(obj.error);
                }
                else
                {
                    prof_more_notifications = true;
                }
                unbindNotification();
                loadNotification();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
    }
}

function getMoreUserActions()
{
    if( prof_more_actions )
    {
        prof_more_actions = false;
        var num_actions = $("#num_actions").val();
        ajaxPost({
            'data': {'action':'getuseractions',
                'num_actions':num_actions,
                'p_id':p_id },
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                $('#profile_activity_feed').append(obj.html);
                $('#num_actions').val(obj.num_actions);
                if( obj.hasOwnProperty('error') && obj.error == 'No more actions' )
                {
                    $('#profile_more_actions').html('No more actions')
                    $('#profile_more_actions').unbind();
                    $('#profile_more_actions').click( function(event)
                    {
                        event.preventDefault();
                    });
                }
                else if( obj.hasOwnProperty('error') )
                {
                    $('body').html(obj.error);
                }
                else
                {
                    prof_more_actions = true;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
    }
}

function getMoreGroups()
{
    if( prof_more_groups )
    {
        prof_more_groups = false;
        var num_groups = $("#num_groups").val();
        ajaxPost({
            'data': {'action':'getusergroups',
                'num_groups':num_groups,
                'p_id':p_id },
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                $('#profile_activity_feed').append(obj.html);
                $('#num_groups').val(obj.num_groups);
                if( obj.hasOwnProperty('error') && obj.error == 'No more groups' )
                {

                    $('#profile_more_groups').html('No more groups');
                    $('#profile_more_groups').unbind();
                    $('#profile_more_groups').click( function(event)
                    {
                        event.preventDefault();
                    });
                }
                else if( obj.hasOwnProperty('error') )
                {
                    $('body').html(obj.error);
                }
                else
                {
                    prof_more_groups = true;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
    }
}

function loadProfile()
{
    unbindNotification();
    loadNotification();

    $("#user_follow_button").click( function(event)
    {
        userFollow(event,$(this),true);
    });

    $(".user-unfollow-button").click( function(event)
    {
        userFollow(event,$(this),false);
    });

    $(".user-follow-response-y").click( function(event) {
        userFollowResponse(event,"Y",$(this));
    });

    $(".user-follow-response-n").click( function(event) {
        userFollowResponse(event,"N",$(this));
    });

    $(".group-invite-response-y").click( function(event) {
        groupInviteResponse(event,"Y",$(this));
    });

    $(".group-invite-response-n").click( function(event) {
        groupInviteResponse(event,"N",$(this));
    });

    $(window).scroll(
        function()
        {
            if  (($(window).scrollTop() + $(window).height() + 5 >= $(document).height())) {

                if( p_id == view_id )
                {
                    getMoreNotifications();
                }
                getMoreUserActions();
                getMoreGroups();
            }
        }
    );

    $('#see_more_notifications').click(
        function(event)
        {
            event.preventDefault();
            getMoreNotifications();
        }
    );

    $('#profile_more_actions').click(
        function(event)
        {
            event.preventDefault();
            getMoreUserActions();
        }
    );

    $('#profile_more_groups').click(
        function(event)
        {
            event.preventDefault();
            getMoreGroups();
        }
    );

    $(".public-follow").click( function(event)
    {
        setFollowPrivacy(event,0,$(this));
    });

    $(".private-follow").click( function(event)
    {
        setFollowPrivacy(event,1,$(this));
    });
}


/***********************************************************************************************************************
 *
 *      ~Petition
 *
 ***********************************************************************************************************************/
function loadPetition()
{

    $("#sign-button").click(function(event)
    {
        event.preventDefault();
        ajaxPost({
            data: {'action':'sign','c_id':c_id},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (returned.success==true) {
                    $("#signer-names").append(returned.signer);
                    if ($('#be-first-signer-message').length > 0)
                    {
                        $('#be-first-signer-message').fadeOut('slow');
                    }
                    $('.sign').text("Thank you for signing!");
                    var num_signers = parseInt($('#num-signers').text().replace('signed',"").replace(/\s/g, ""));
                    num_signers = num_signers + 1;
                    $('#num-signers').text(num_signers + " " + "signed");
                    loadHoverComparison();
                }
                else {
                    $('.sign').text(returned.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

    $("#finalize-button").click(function(event)
    {
        event.preventDefault();
        ajaxPost({
            data: {'action':'finalize','c_id':c_id},
            success: function(data)
            {
                location.reload();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

}

/***********************************************************************************************************************
 *
 *      ~Petition
 *
 **********************************************************************************************************************/

function loadAccount()
{
    $('#choose-image input').attr("accept","image/jpg, image/gif, image/png, image/JPG, image/GIF, image/PNG, image/jpeg");

    $("#submitpassword").click(function(event)
    {
        event.preventDefault();
        $("#passwordform").submit();
    });

    $("#submitpic").click(function(event)
    {
        event.preventDefault();
        $("#picform").submit();
    });

    $('#new2').bind('keyup', function(event)
    {
        if (event.keyCode != 13)
        {
            var new1 = $('#new1').val();
            var new2 = $('#new2').val();
            if (new1 == "" && new2 == "")
            {
                $('.new').css({"background-color":"#FFFFFF"});
            }
            else if (new1==new2)
            {
                $('.new').css({"background-color":"#DBFFD6"});
            }
            else
            {
                $('.new').css({"background-color":"#FFD6D6"});
            }
        }
    });

    $('#new1').bind('keyup', function(event)
    {
        if (event.keyCode != 13 && $('#new2').val() != "")
        {
            var new1 = $('#new1').val();
            var new2 = $('#new2').val();
            if (new1 == "" && new2 == "")
            {
                $('.new').css({"background-color":"#FFFFFF"});
            }
            else if (new1==new2)
            {
                $('.new').css({"background-color":"#DBFFD6"});
            }
            else
            {
                $('.new').css({"background-color":"#FFD6D6"});
            }
        }
    });
}



/***********************************************************************************************************************
 *
 *      ~Group
 *
 **********************************************************************************************************************/
function bindGroupRequestsButton()
{
    $('#group_requests').click( function(event) {
        event.preventDefault();
        $('div.overdiv').fadeToggle("fast");
        $('div#group_requests_modal').fadeToggle("fast");
    });

    $('div.overdiv').click(function() {
        $('div.overdiv').hide();
        $('div#group_requests_modal').hide();
    });
}

function groupFollowResponse(event,response,div,g_id)
{
    event.preventDefault();
    var follow_id = div.siblings(".follow-id").val();
    var g_id = div.siblings(".group-id").val();
    ajaxPost({
            data: {
                'action':'joinresponse',
                'follow_id': follow_id,
                'g_id': g_id,
                'response': response
            },
            success: function(data)
            {
                alert(data);
            },
            error: function(error, textStatus, errorThrown)
            {
                $('body').html(error.responseText);
            }
        }
    );
}

var group_more_actions = true;
var group_more_members = true;

function getMoreGroupActions()
{
    if( group_more_actions )
    {
        group_more_actions = false;
        var num_actions = $("#num_actions").val();
        ajaxPost({
            'data': {'action':'getgroupactions',
                'num_actions':num_actions,
                'g_id':g_id },
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                $('#group_activity_feed').append(obj.html);
                $('#num_actions').val(obj.num_actions);
                if( 'error' in obj && obj.error == 'No more actions' )
                {
                    $('#group_more_actions').html('No more actions');
                    $('#group_more_actions').unbind();
                    $('#group_more_actions').click( function(event)
                    {
                        event.preventDefault();
                    });
                }
                else if( 'error' in obj )
                {
                    $('body').html(obj.error);
                }
                else
                {
                    group_more_actions = true;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
    }
}

function getMoreGroupMembers()
{
    if( group_more_members )
    {
        group_more_members = false;
        var num_members = $("#num_members").val();
        ajaxPost({
            'data': {'action':'getgroupmembers',
                'num_members':num_members,
                'g_id':g_id },
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                $('#group_members_container').append(obj.html);
                $('#num_members').val(obj.num_members);
                if( 'error' in obj && obj.error == 'No more members' )
                {
                    $('#group_more_members').html('No more members');
                    $('#group_more_members').unbind();
                    $('#group_more_members').click( function(event)
                    {
                        event.preventDefault();
                    });
                }
                else if( 'error' in obj )
                {
                    $('body').html(obj.error);
                }
                else
                {
                    group_more_members = true;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
    }
}

function loadGroup()
{
    var loadUsersLockout = false;
    var loadHistoLockout = false;

    bindGroupRequestsButton();
    // load more users for display
    function loadMoreUsers(event, replace)
    {
        if (replace == true) {
            $("#histogram-displayed-num").val(0);
        }
        event.preventDefault();
        var histogram_displayed_num = $('#histogram-displayed-num').val();
        var histogram_topic = $('#histogram-topic').val();
        var histogram_block = $('#histogram-block').val();
        var group_id = $('#group-id').val();
        if (!loadUsersLockout)
        {
            loadUsersLockout = true;
            ajaxPost({
                data: {'action':'loadGroupUsers','histogram_displayed_num':histogram_displayed_num,'group_id':group_id,
                    'histogram_topic':histogram_topic,'histogram_block':histogram_block },
                success: function(data)
                {
                    var returned = eval('(' + data + ')');
                    if (replace==true) {
                        $('#members-list').html(returned.html);
                    }
                    else {
                        $('#members-list').append(returned.html);
                    }
                    $('#histogram-displayed-num').val(returned.num);
                    loadHoverComparison();
                    loadAjaxifyAnchors();
                    bindNewDivs();
                    loadUsersLockout = false;
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $('body').html(jqXHR.responseText);
                }
            });
        }
    }

    // load new histogram data
    function getHistogram() {
        var histogram_topic = $('#histogram-topic').val();
        var group_id = $('#group-id').val();
        if (!loadHistoLockout)
        {
            loadHistoLockout = true;
            ajaxPost({
                data: {'action':'loadHistogram','group_id':group_id,
                    'histogram_topic':histogram_topic},
                success: function(data)
                {
                    var returned = eval('(' + data + ')');
                    $(".histogram-bars").html(returned.html);
                    loadHistoLockout = false;
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $('body').html(jqXHR.responseText);
                }
            });
        }
    }

    $(".group-response-y").click( function(event) {
        groupFollowResponse(event,"Y",$(this),g_id);
    });

    $(".group-response-n").click( function(event) {
        groupFollowResponse(event,"N",$(this),g_id);
    });

    $("#group_follow").click( function(event) {
        groupFollow(event,$(this),true);
    });
    $("#group_unfollow").click( function(event) {
        groupFollow(event,$(this),false);
    });

    // select histogram block
    $(".histogram-select-block").click(function(event) {
        event.preventDefault();
        var block = $(this).siblings(".block-val").val();
        var was = $("#histogram-block").val();
        if (block == was) {
            $("#histogram-block").val(-1);
        }
        else {
            $("#histogram-block").val(block);
        }
        loadMoreUsers(event, true);
    });

    // change histogram topic
    $(".h-topic-img").click(function(event) {
        var wrapper = $(this).parents(".topic-icon-wrapper");
        selectTopicSingle(wrapper);
        var topic = $(this).siblings(".t-alias").val();
        var was = $("#histogram-topic").val();
        if (topic == was) {
            $("#histogram-topic").val('general');
        }
        else {
            $("#histogram-topic").val(topic);
        }
        loadMoreUsers(event, true);
        getHistogram();
    });

    function bindNewDivs()
    {
        $('.group-member-div').hover
            (
                function(){ $(this).css("background-color","#EBEBEB") },
                function(){ $(this).css("background-color","#FFFFFF") }
            );

    }

    $('#group_more_actions').click(
        function(event)
        {
            event.preventDefault();
            getMoreGroupActions();
        }
    );

    $('#group_more_members').click(
        function(event)
        {
            event.preventDefault();
            getMoreGroupMembers();
        }
    );

    $(window).scroll(
        function()
        {
            if(($(window).scrollTop() + $(window).height() >= $(document).height() ))
            {
                getMoreGroupActions();
                getMoreGroupMembers();
            }
        }
    );

    /*
     $(window).scroll(function(event)
     {
     if  ($(window).scrollTop() == $(document).height() - $(window).height()) { loadMoreUsers(event); }
     });
     */

    $('#group-see-more-users').click(function(event)
    {
        loadMoreUsers(event, false);
    });

    bindNewDivs();

}

/***********************************************************************************************************************
 *
 *      ~NewFeed
 *
 **********************************************************************************************************************/

/*
 Sets the red bar to proper width.
 */
function petitionBar(wrapper) {
    var percent = wrapper.data('percent');
    wrapper.find('.red_bar').css("width", percent + "%");
}

/*
 Takes in a a value and the classname of an input which the value should
 either be added to or removed from that list (toggled).
 */
function listToggleHelper(list_values, value) {
    var index = $.inArray(value, list_values);
    if (index == -1) {
        list_values.push(value);
    }
    else {
        list_values.splice(index, 1);
    }
    return list_values
}

/*
 Replaces feed with all new items based on current parameters.
 */
function refreshFeed(num) {

    feed_metadata.feed_start = 0;
    var i =0;
    while (i < pinterest.length) {
        pinterest[i] = 0;
        i += 1;
    }
    getFeed(num);
}

/*
 if the start value is 0, then replace feed with all new items based on current parameters
 else get new feed items starting at start value and append them to the current feed.
 */
function getFeed(num)
{

    if (num==-1) {
        num = 18;
    }

    var feed_ranking = feed_metadata.ranking;
    var feed_display =  feed_metadata.display;
    var feed_submissions_only =  feed_metadata.submissions_only;
    var feed_topics = feed_metadata.topics;
    var feed_types =  feed_metadata.types;
    var feed_levels =  feed_metadata.levels;
    var feed_groups =  feed_metadata.groups;
    var feed_start = feed_metadata.feed_start;
    feed_topics = JSON.stringify(feed_topics);
    feed_types = JSON.stringify(feed_types);
    feed_levels = JSON.stringify(feed_levels);
    feed_groups = JSON.stringify(feed_groups);

    var feed_end =  feed_start + num;

    var feed_replace;
    if (feed_start==0) {
        feed_replace = true;
    }
    else {
        feed_replace = false;
    }

    ajaxPost({
        data: {'action':'ajaxGetFeed','feed_ranking': feed_ranking,'feed_topics':feed_topics,
            'feed_types':feed_types, 'feed_levels': feed_levels, 'feed_groups':feed_groups,
            'feed_submissions_only':feed_submissions_only,'feed_display':feed_display,
            'feed_start':feed_start, 'feed_end':feed_end
        },
        success: function(data) {
            var returned = eval('(' + data + ')');

            if (feed_replace == true) {
                $(".pinterest-wrapper").html(returned.html);
            }
            else {
                $(".pinterest-wrapper").append(returned.html);
            }

            feed_metadata.feed_start = feed_start + returned.num;

            if (feed_display == "P") {
                $(".right-sidebar").hide();
                pinterestRender($(".pinterest_unrendered"));
            }
            else {
                $(".right-sidebar").show();
            }

            heartButtons();
            loadShareButton();
            loadHoverComparison();

        },
        error: null
    });
}

/*
 makes a post to the server to save the current filter setting as the inputted name.
 */
function saveFilter(name) {

    var feed_name = name;
    var feed_ranking = feed_metadata.ranking;
    var feed_display =  feed_metadata.display;
    var feed_submissions_only =  feed_metadata.submissions_only;
    var feed_topics = feed_metadata.topics;
    var feed_types =  feed_metadata.types;
    var feed_levels =  feed_metadata.levels;
    var feed_groups =  feed_metadata.groups;
    feed_topics = JSON.stringify(feed_topics);
    feed_types = JSON.stringify(feed_types);
    feed_levels = JSON.stringify(feed_levels);
    feed_groups = JSON.stringify(feed_groups);

    ajaxPost({
        data: {'action':'saveFilter','feed_ranking': feed_ranking,'feed_topics':feed_topics,
            'feed_types':feed_types, 'feed_levels': feed_levels, 'feed_groups':feed_groups,
            'feed_submissions_only':feed_submissions_only,'feed_display':feed_display,
            'feed_name': feed_name
        },
        success: function(data) {
            $(".save_filter_input").val("saved: " + feed_name);
        },
        error: null
    });
}

/* deletes a filter from my_filters list */
function deleteFilter(name) {
    ajaxPost({
        data: {'action':'deleteFilter','f_name':name},
        success: function(data) {
            location.reload();
        },
        error: null
    });
}

/*
 retrives the filter setting with the inputted id from the server and refreshes feed.
 */
function getFilter(f_id) {
    ajaxPost({
        data: {'action':'getFilter', filter_id:f_id},
        success: function(data) {

            var returned = eval('('+data+')');

            feed_metadata.ranking = returned.ranking;
            feed_metadata.display = returned.display;
            feed_metadata.submissions_only = returned.submissions_only;
            feed_metadata.topics = $.parseJSON(returned.topics);
            feed_metadata.levels = $.parseJSON(returned.levels);
            feed_metadata.groups = $.parseJSON(returned.groups);
            feed_metadata.types = $.parseJSON(returned.types);

            updateFeedVisual();

            refreshFeed(-1);

        },
        error: null
    })
}

/* retrieves and sets defaults filter for user */
function getFilterByName(name) {
    $(".saved-filter-selector").removeClass("clicked");
    var this_filter = $(".saved-filter-selector[data-f_name=" + name + "]");
    this_filter.addClass("clicked");
    $(".save_filter_input").val(name);
    getFilter(this_filter.data('f_id'));
}

/* heart stuff */
function heartButtons()
{
    $(".heart_minus").bindOnce('click.vote', function(event) {
        var wrapper = $(this).parents(".hearts-wrapper");
        event.preventDefault();
        vote(wrapper, wrapper.data('c_id'), -1);
    });

    $(".heart_plus").bindOnce('click.vote', function(event) {
        var wrapper = $(this).parents(".hearts-wrapper");
        event.preventDefault();
        vote(wrapper, wrapper.data('c_id'), 1);
    });
}


function vote(wrapper, content_id, v)
{
    ajaxPost({
        data: {'action':'vote','c_id':content_id, 'vote':v},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            var my_vote = parseInt(returned.my_vote);
            var status = returned.status;
            if (my_vote==1) { like(wrapper); }
            if (my_vote==0) { neutral(wrapper); }
            if (my_vote==-1) { dislike(wrapper); }
            wrapper.find(".status").text(status);
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $("body").html(jqXHR.responseText);
        }
    });
}

function like(div)
{
    div.find(".heart_plus").addClass("clicked");
    div.find(".heart_minus").removeClass("clicked");
}
function dislike(div)
{
    div.find(".heart_plus").removeClass("clicked");
    div.find(".heart_minus").addClass("clicked");
}
function neutral(div)
{
    div.find(".heart_plus").removeClass("clicked");
    div.find(".heart_minus").removeClass("clicked");
}

/*
 visually and in data representation sets all feed parameters to defaults
 */
function clearFilterParameters() {

    feed_metadata.topics =  [];
    feed_metadata.types =  [];
    feed_metadata.levels =  [];
    feed_metadata.groups =  [];
    feed_metadata.ranking = 'N';
    updateFeedVisual();

    refreshFeed(-1);

}

/* updates the visual display of feed parameters based on javascript object representation */
function updateFeedVisual() {

    var feed_types = $(".feed-type-selector");
    feed_types.each(function(index) {
        var this_type = $(this).data('type');
        var i = $.inArray(this_type, feed_metadata.types);
        if (i != -1) {
            $(this).addClass("clicked");
        }
        else {
            $(this).removeClass("clicked");
        }
    });

    var feed_levels = $(".feed-level-selector");
    feed_levels.each(function(index) {
        var this_level = $(this).data('level');
        var i = $.inArray(this_level, feed_metadata.levels);
        if (i != -1) {
            $(this).addClass("clicked");
        }
        else {
            $(this).removeClass("clicked");
        }
    });

    var feed_groups = $(".feed_group_selector");
    feed_groups.each(function(index) {
        var this_group = $(this).data('level');
        var i = $.inArray(this_group, feed_metadata.groups);
        if (i != -1) {
            $(this).addClass("clicked");
        }
        else {
            $(this).removeClass("clicked");
        }
    });

    var feed_topics = $(".feed-topic-icon-wrapper");
    feed_topics.each(function(index) {
        var this_topic = $(this).data('t_id');
        var i = $.inArray(this_topic, feed_metadata.topics);
        if (i != -1) {
            showTopicIcon($(this));
        }
        else {
            hideTopicIcon($(this));
        }
    });

    setDisplay(feed_metadata.display);

    setRanking(feed_metadata.ranking);
}

function setDisplay(value) {
    feed_metadata.display = value;
    var visual_wrapper = $("div[data-display=" + value + "]");
    visualSelectDisplayWrapper(visual_wrapper);
}

function setRanking(value) {
    $(".feed-ranking-selector").removeClass("clicked");
    var ranking_wrapper = $(".feed-ranking-selector[data-ranking=" + value + "]");
    ranking_wrapper.addClass("clicked");
    $(".ranking_menu_title").text(ranking_wrapper.data('verbose'));
    feed_metadata.ranking = value;
}


var pinterest = [];
var current_col=0;
var total_cols=3;
var pinterest_width=(1000/total_cols)+8;
/* returns a list of pinterest cards, sorted by rank */
function pinterestRender(cards) {

    // if pinterest is empty, initialize it with as many elements as there are columns
    if (pinterest.length == 0) {
        // initialize variables
        var i = 0;
        while (i < total_cols) {
            pinterest.push(0);
            i += 1;
        }
    }

    cards.each(function(index) {
        if (current_col == total_cols) {
            current_col = 0;
        }
        var top = pinterest[current_col];
        var left = pinterest_width*current_col;
        var height = $(this).height() + 20;
        $(this).css("position", 'absolute');
        $(this).css("left", left);
        $(this).css({"top": top}, 1400);
        pinterest[current_col] = (top + height);
        current_col += 1;
        $(this).removeClass("pinterest_unrendered");
    });
}


var scrollLoadLockout=false;
function scrollFeed() {
    if  (($(window).scrollTop() >= $(document).height() - $(window).height())) {
        if (scrollLoadLockout==false) {
            getFeed(-1);
            scrollLoadLockout=true;
            setTimeout(function() { scrollLoadLockout=false}, 500);
        }
    }
}

/* shows display select appropriately */
function visualSelectDisplayWrapper(wrapper) {
    $(".display-red").hide();
    $(".display-gray").show();
    visualDisplayWrapperShow(wrapper);
}
function visualDisplayWrapperShow(wrapper) {
    wrapper.find(".display-gray").hide();
    wrapper.find(".display-red").show();
}
function visualDisplayWrapperHide(wrapper) {
    wrapper.find(".display-gray").show();
    wrapper.find(".display-red").hide();
}

/**
 * Binds feed items with UI functionality
 */
function bindFeedItems()
{
    /**
     * Binds link of news URL to the image for the URL
     */
    $('.link-img img').unbind();
    $('.link-img img').click(function(event)
    {
        var url = $(this).siblings('a').attr('href');
        // middle mouse button or control + leftclick will open new tab for link
        if(event.ctrlKey || (!$.browser.msie && event.button == 1) || ($.browser.msie && event.button == 4))
        {
            window.open(url, '_blank');
        }
        // normal leftclick on link
        else
        {
            window.location = url;
        }
    });

    /**
     * Adds border on hover to image
     */
    $('.link-img img').hover
        (
            function(event) { $(this).css("border-color","#f0503b"); }, // hover over
            function(event) { $(this).css('border-color','#FFFFFF'); }  // hover out
        );

    $('.feed-username').click(function(event)
    {
        var url = $(this).children('a').attr('href');
        // middle mouse button or control + leftclick will open new tab for link
        if(event.ctrlKey || (!$.browser.msie && event.button == 1) || ($.browser.msie && event.button == 4))
        {
            window.open(url, '_blank');
        }
        // normal leftclick on link
        else
        {
            ajaxLink(url,true);
        }
    });

    // bind newly loaded feed items with comparison hover over
    loadHoverComparison();
    loadAjaxifyAnchors();
}

/* binds everyting */
var feed_metadata;
function loadNewFeed() {

    // parse json for metadata
    feed_metadata = $("#feed_metadata").data('json');
    updateFeedVisual();

    $(".more-options-wrapper").css('height', '0px');
    $(".more_options").click(function(event) {
        event.preventDefault();
        $(this).toggleClass("clicked");
        var wrapper = $(".more-options-wrapper");
        if (wrapper.hasClass("out")) {
            wrapper.css("overflow", "hidden");
            wrapper.animate({"height": '0px'}, 1000);
            wrapper.removeClass("out");
            wrapper.find(".menu_toggle").removeClass("clicked");
            wrapper.find(".menu").hide();
        }
        else {
            wrapper.show();
            wrapper.animate({"height": '120px'}, 1000, function() { wrapper.css('overflow', 'visible')});
            wrapper.addClass("out");
        }
    });


    $(".get_feed").click(function(event) {
        event.preventDefault();;
        getFeed(-1);
    });

    $(".refresh_feed").click(function(event) {
        event.preventDefault();
        refreshFeed(-1);
    });

    $(".feed-topic-img").click(function(event) {
        var wrapper = $(this).parents(".topic-icon-wrapper");
        toggleTopicIcon(wrapper);
        var value = $(this).parents(".feed-topic-icon-wrapper").data('t_id');
        listToggleHelper(feed_metadata.topics, value);
        refreshFeed(-1);
    });

    $(".feed-display-selector").click(function(event) {
        event.preventDefault();
        var display = $(this).data("display");
        feed_metadata.display = display;
        refreshFeed(-1);
    });

    $(".save_filter_button").click(function(event) {
        event.preventDefault();
        var name = $(".save_filter_input").val();
        if (name!='' && name!='enter a name for your filter.') {
            saveFilter(name);
        }
        else {
            $(".save_filter_input").val('enter a name for your filter.');
        }
    });

    $(".delete_saved_filter").click(function(event) {
        event.preventDefault();
        var wrapper = $(this).parents(".saved-filter-selector");
        var f_name = wrapper.data('f_name');
        deleteFilter(f_name);
        event.stopPropagation();
    });

    $(".saved-filter-selector").click(function(event) {
        event.preventDefault();
        var value = $(this).data("f_id");
        getFilter(value);
        $(".save_filter_input").val($(this).data('f_name'));
    });

    $(".feed_clear").click(function(event) {
        event.preventDefault();
        clearFilterParameters();
    });

    /* display menu */
    $(".display-choice").click(function(event) {
        setDisplay($(this).data('display'));
        var num = 6;
        var already = feed_metadata.start;
        if (already > num) {
            num = already;
        }
        refreshFeed(num);
    });

    /* sort-by menu */
    $(".feed-ranking-selector").click(function(event) {
        event.preventDefault();
        setRanking($(this).data('ranking'));
        refreshFeed(-1);
    });

    /* group and network menu  visual */
    defaultHover($(".group-box"));
    $(".group-box").click(function(event) {
        event.preventDefault();
        defaultClick($(this));
        event.stopPropagation();
    });
    /* group menu  functional */
    $(".feed_group_selector").click(function(event) {
        var value = $(this).data('g_id');
        listToggleHelper(feed_metadata.groups, value);
        refreshFeed(-1);
    });

    /* levels menu */
    $(".feed-level-selector").click(function(event) {
        var value = $(this).data('level');
        listToggleHelper(feed_metadata.levels, value);
        refreshFeed(-1);
        event.stopPropagation();
    });

    /* types menu */
    $(".feed-type-selector").click(function(event) {
        var value = $(this).data('type');
        listToggleHelper(feed_metadata.types, value);
        refreshFeed(-1);
        event.stopPropagation();
    });

    /* gray hover for all dropdown menu options */
    defaultHoverClickSingle($(".menu-option.single"));
    defaultHoverClick($(".menu-option.multi"));


    $(".menu-option").hover(
        function(event) {
            event.stopPropagation();
        },
        function(event) {
            event.stopPropagation();
        });

    getFilterByName(feed_metadata.filter_name);

    $(window).scroll(scrollFeed);

    bindCreateButton();
    loadCreate();
}

/***********************************************************************************************************************
 *
 *      ~CreateModal
 *
 **********************************************************************************************************************/
function bindCreateButton()
{
    $('.create_button').click( function(event) {
        event.preventDefault();
        $('div.overdiv').fadeToggle("fast");
        $('div.create_modal').fadeToggle("fast");
    });

    $('div.overdiv').click(function() {
        $('div.overdiv').hide();
        $('div.create_modal').hide();
    });
}

function bindGroupPrivacyRadio()
{
    $("div.group_privacy_radio").unbind();
    $("div.group_privacy_radio").click(function(event)
    {
        var prev = $("input:radio[name=group_privacy]:checked");
        prev.attr('checked',false);
        prev.parent('.group_privacy_radio').removeClass("create-radio-selected");

        $(this).children("input:radio[name=group_privacy]").attr('checked',true);
        $(this).addClass("create-radio-selected");
    });
}

function bindScaleRadio()
{
    $("div.group_scale_radio").unbind();
    $("div.group_scale_radio").click(function(event)
    {
        var prev = $("input:radio.group_scale:checked");
        prev.attr('checked',false);
        prev.parent('.group_scale_radio').removeClass("create-radio-selected");

        $(this).children("input:radio.group_scale").attr('checked',true);
        $(this).addClass("create-radio-selected");
    });

    $("div.petition_scale_radio").unbind();
    $("div.petition_scale_radio").click(function(event)
    {
        var prev = $("input:radio.petition_scale:checked");
        prev.attr('checked',false);
        prev.parent('.petition_scale_radio').removeClass("create-radio-selected");

        $(this).children("input:radio.petition_scale").attr('checked',true);
        $(this).addClass("create-radio-selected");
    });

    $("div.news_scale_radio").unbind();
    $("div.news_scale_radio").click(function(event)
    {
        var prev = $("input:radio.news_scale:checked");
        prev.attr('checked',false);
        prev.parent('.news_scale_radio').removeClass("create-radio-selected");

        $(this).children("input:radio.news_scale").attr('checked',true);
        $(this).addClass("create-radio-selected");
    });
}

function createGroupValidation( event )
{
    event.preventDefault();
    var valid = true;

    /* Title */
    var title = $('#group_title').val();
    var title_error = $('#group_name_error');
    title = title.replace(" ","");
    if( title == "" )
    {
        title_error.text("Please enter a group title.");
        title_error.show();
        valid = false;
    }
    else
    {
        title_error.hide();
    }

    /* Description */
    var description = $('#group_description').val();
    var desc_error = $('#group_description_error');
    description = description.replace(" ","");
    if( description == "" )
    {
        desc_error.text("Please enter a group description.");
        desc_error.show();
        valid = false;
    }
    else
    {
        desc_error.hide();
    }

    /* Privacy */
    var privacy = $('input:radio[name=group_privacy]:checked').length;
    var privacy_error = $('#group_privacy_error');
    if( privacy < 1 )
    {
        privacy_error.text("Please select a group privacy.");
        privacy_error.show();
        valid = false;
    }
    else if( privacy > 1 )
    {
        privacy_error.text("You have selected multiple group privacy settings.");
        privacy_error.show();
        valid = false;
    }
    else
    {
        privacy_error.hide();
    }

    /* Scale */
    var scale = $('input:radio.group_scale:checked').length;
    var scale_error = $('#group_scale_error');
    if( scale < 1 )
    {
        scale_error.text("Please select a group scale.");
        scale_error.show();
        valid = false;
    }
    else if( scale > 1 )
    {
        scale_error.text("You have selected multiple group scales.");
        scale_error.show();
        valid = false;
    }
    else
    {
        scale_error.hide();
    }

    /* Image */
    var image = $('input#group_image').val();
    var image_error = $('#group_image_error');
    if( image == "" )
    {
        image_error.text("Please select a group image.");
        image_error.show();
        valid = false;
    }
    else
    {
        image_error.hide();
    }

    /* Topics */
    var topic = $('#group_input_topic').find('input:radio[name=topics]:checked').length;
    var topic_error = $('#group_topic_error');
    if( topic < 1 )
    {
        topic_error.text("Please select a group topic.");
        topic_error.show();
        valid = false;
    }
    else if( topic > 1 )
    {
        topic_error.text("You have selected multiple group topics.");
        topic_error.show();
        valid = false;
    }
    else
    {
        topic_error.hide();
    }

    /* submit if valid! */
    if( valid )
    {
        $('#group_form').submit();
    }
}

function createPetitionValidation( event )
{
    event.preventDefault();
    var valid = true;

    /* Title */
    var title = $('#petition_title').val();
    var title_error = $('#petition_name_error');
    title = title.replace(" ","");
    if( title == "" )
    {
        title_error.text("Please enter a petition title.");
        title_error.show();
        valid = false;
    }
    else
    {
        title_error.hide();
    }

    /* Description */
    var description = $('#petition_description').val();
    var desc_error = $('#petition_description_error');
    description = description.replace(" ","");
    if( description == "" )
    {
        desc_error.text("Please enter a petition description.");
        desc_error.show();
        valid = false;
    }
    else
    {
        desc_error.hide();
    }

    /* Scale */
    var scale = $('input:radio.petition_scale:checked').length;
    var scale_error = $('#petition_scale_error');
    if( scale < 1 )
    {
        scale_error.text("Please select a petition scale.");
        scale_error.show();
        valid = false;
    }
    else if( scale > 1 )
    {
        scale_error.text("You have selected multiple petition scales.");
        scale_error.show();
        valid = false;
    }
    else
    {
        scale_error.hide();
    }

    /* Topics */
    var topic = $('#petition_input_topic').find('input:radio[name=topics]:checked').length;
    var topic_error = $('#petition_topic_error');
    if( topic < 1 )
    {
        topic_error.text("Please select a petition topic.");
        topic_error.show();
        valid = false;
    }
    else if( topic > 1 )
    {
        topic_error.text("You have selected multiple petition topics.");
        topic_error.show();
        valid = false;
    }
    else
    {
        topic_error.hide();
    }

    /* submit if valid! */
    if( valid )
    {
        $('#petition_form').submit();
    }
}

function createNewsValidation( event )
{
    event.preventDefault();
    var valid = true;

    /* Title */
    var title = $('#news-input-link').val();
    var title_error = $('#news_name_error');
    title = title.replace(" ","");
    if( title == "" )
    {
        title_error.text("Please enter a news link.");
        title_error.show();
        valid = false;
    }
    else
    {
        title_error.hide();
    }

    /* Scale */
    var scale = $('input:radio.news_scale:checked').length;
    var scale_error = $('#news_scale_error');
    if( scale < 1 )
    {
        scale_error.text("Please select a news scale.");
        scale_error.show();
        valid = false;
    }
    else if( scale > 1 )
    {
        scale_error.text("You have selected multiple news scales.");
        scale_error.show();
        valid = false;
    }
    else
    {
        scale_error.hide();
    }

    /* Topics */
    var topic = $('#news_input_topic').find('input:radio[name=topics]:checked').length;
    var topic_error = $('#news_topic_error');
    if( topic < 1 )
    {
        topic_error.text("Please select a news topic.");
        topic_error.show();
        valid = false;
    }
    else if( topic > 1 )
    {
        topic_error.text("You have selected multiple news topics.");
        topic_error.show();
        valid = false;
    }
    else
    {
        topic_error.hide();
    }

    /* submit if valid! */
    if( valid )
    {
        postNews();
    }
}

function postNews()
{
    var title = $('#news-input-title').val();
    var summary = $('#news-input-summary').val();
    var link = $('#news-input-link').val();
    var description = $('#news-link-generation-description').text();
    var screenshot = $('#news-link-image-src').attr("src");
    var scale = $('input:radio.news_scale:checked').val();
    var topic = $('input:radio[name=topics]:checked').val();
    ajaxPost({
        data: {'action':'create','title':title,'summary':summary,'link':link,
            'type':'N', 'description':description, 'screenshot':screenshot, 'topics':topic, 'scale':scale },
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            if (returned.success == false)
            {
                $("#news-errors-link").html(returned.errors.link);
                $("#news-errors-title").html(returned.errors.title);
                $("#news-errors-summary").html(returned.errors.summary);
                $("#news-errors-topic").html(returned.errors.topics);
                $("#news-errors-non_field").html(returned.errors.non_field_errors);
            }
            else
            {
                window.location=returned.url;
            }
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $("body").html(jqXHR.responseText);
        }
    });
}

function loadCreate()
{
    $('#create_petition_button').click(function()
    {
        $('.create_content_div').hide();
        $('#create_petition_div').show();
    });

    $('#create_news_button').click(function()
    {
        $('.create_content_div').hide();
        $('#create_news_div').show();
    });

    $('#create_group_button').click(function()
    {
        $('.create_content_div').hide();
        $('#create_group_div').show();
    });

    bindGroupPrivacyRadio();
    bindScaleRadio();

    $('#submit_group_button').click(
        function(event)
        {
            createGroupValidation(event);
        }
    );

    $('#submit_petition_button').click(
        function(event)
        {
            createPetitionValidation(event);
        }
    );

    $('#submit_news_button').click(
        function(event)
        {
            createNewsValidation( event );
        }
    );


    var timeout;
    var delay = 750;
    var isLoading = false;
    var currentURL;
    var currentLink = 0;
    var returned;

    $('#news-input-link').bind('keyup',function()
    {
        var text = $(this).val();
        if (timeout)
        {
            clearTimeout(timeout);
        }

        if (!isLoading && text != currentURL)
        {
            timeout = setTimeout(function()
            {
                isLoading = true;
                if (regUrl.test(text))
                {
                    $('#news-link-generation-wrapper').empty();
                    $('#news-link-generation').show();
                    $('#news-link-generation-wrapper').append('<div style="width:530px;margin-bottom:25px"><img style="width:75px;height:75px;margin-left:235px;" id="loading-img" src="/static/images/ajax-loader.gif"></div>');
                    $('#news-summary').show();
                    ajaxPost({
                        data: {'action':'getLinkInfo','remote_url':text},
                        success: function(data)
                        {
                            returned = eval('(' + data + ')');
                            $('#news-link-generation-wrapper').html(returned.html);
                            $('#cycle-img-left').bind('click',function()
                            {
                                if (currentLink-1 < 0) { currentLink = returned.imglink.length-1; }
                                else { currentLink--; }
                                $('#cycle-img-span').text((currentLink+1) + " / " + returned.imglink.length);
                                $('#news-link-image-src').attr("src",returned.imglink[currentLink].path);
                            });
                            $('#cycle-img-right').bind('click',function()
                            {
                                if (currentLink+1 >= returned.imglink.length) { currentLink = 0; }
                                else { currentLink++; }
                                $('#cycle-img-span').text((currentLink+1) + " / " + returned.imglink.length);
                                $('#news-link-image-src').attr("src",returned.imglink[currentLink].path);
                            });
                            currentURL = text;
                        },
                        error: null
                        /*
                         function(jqXHR, textStatus, errorThrown)
                         {

                         $('#news-link-generation').hide();
                         $('#news-summary').hide();
                         } */
                    });
                }
                else
                {
                    $('#news-link-generation').hide();
                    $('#news-summary').hide();
                }
                // Simulate a real ajax call
                setTimeout(function() { isLoading = false; }, delay);
            }, delay);
        }
    });

    /**
     * Handles selecting topic image for content creation
     */
    $(".create-topic-img").click(function(event)
    {

        var wrapper = $(this).parents(".topic-icon-wrapper");
        var icons_wrapper = wrapper.parents(".topic-icons-wrapper");

        icons_wrapper.find('.topic-radio').attr('checked',false);

        if (!wrapper.hasClass('chosen'))
        {
            wrapper.find(".topic-radio").attr("checked",true);
        }
        selectTopicSingle(wrapper);
    });

    function clearPetitionErrors()
    {
        $("#errors-title").empty();
        $("#errors-summary").empty();
        $("#errors-full_text").empty();
        $("#errors-topic").empty();
        $("#errors-non_field").empty();
    }
}
