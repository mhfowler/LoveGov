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
        case 'home':                                            // /home
            loadFeed();
            break;
        case 'feed':                                            // /feed
            loadNewFeed();
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
        case 'login':
            loadLogin();
            break;
        default:
            break
    }
}

/***********************************************************************************************************************
 *
 *      ~Auxiliary
 *
 ***********************************************************************************************************************/
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
                if( data == "now following this person")
                {
                    div.html("unfollow");
                    div.click(
                        function(event)
                        {
                            userFollow(event,$(this),false);
                        }
                    );
                }
                else if( data == "requested to follow this person")
                {
                    div.html("un-request");
                    div.click(
                        function(event)
                        {
                            userFollow(event,$(this),false);
                        }
                    );
                }
                else if( data == "removed")
                {
                    div.html("follow");
                    div.click(
                        function(event)
                        {
                            userFollow(event,$(this),true);
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

    $('.feed-username').hoverIntent
        (
            // hover over
            function(event)
            {
                var self = $(this);
                var a = $(this).find('a');
                if (a.attr('href') != undefined)
                {
                    clearTimeout(hoverTimer);
                    $('#comparison-hover').empty();
                    var alias = a.attr('href').split('/')[2].toString();
                    var top = self.offset().top - ($('#comparison-hover-div').height()) - 40;
                    if (top <= $(document).scrollTop())
                    {
                        top = self.offset().top + 70;
                        $('#comparison-hover-pointer-up').show(); $('#comparison-hover-pointer-down').hide();
                    }
                    else
                    {
                        $('#comparison-hover-pointer-up').hide(); $('#comparison-hover-pointer-down').show();
                    }
                    var left = self.offset().left - ($('#comparison-hover-div').width()/2) + 21;
                    var offset = {top:top,left:left};
                    $('#comparison-hover-div p').text('You & ' + a.text());
                    $('#comparison-hover-loading-img').show();
                    $('#comparison-hover-div').fadeIn(100);
                    $('#comparison-hover-div').offset(offset);
                    ajaxPost({
                        'data': {'action':'hoverComparison','alias':alias},
                        'success': function(data) {
                            var obj = eval('(' + data + ')');
                            $('#comparison-hover-loading-img').hide();
                            new VisualComparison('comparison-hover',obj).draw();
                        },
                        'error': function(jqXHR, textStatus, errorThrown) {
                            $('#comparison-hover-div p').text('Sorry there was an error');
                        }
                    });
                }
            },
            // hover out
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
    var ajaxClicked = function(event)
    {
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

    $('#searchbar').focusin(function()
    {
        if ($(this).val()=="Search Users")
        {
            $(this).val('');
        }
        $(this).css("color","#000000")
    });

    $("#searchbar").bind("clickoutside", function(event)
    {
        if ($(this).val()=="")
        {
            $(this).val('Search Users');
            $(this).css("color",'#959595');
        }
        $(this).blur();
    });

    $('#notifications-dropdown-button').click(
        function(event)
        {
            event.preventDefault();
            $('#notifications-dropdown').toggle('fast');
            if( $('#notifications-dropdown').is(':visible') )
            {
                ajaxPost({
                    'data': {'action':'getnotifications',
                            'dropdown':'true'},
                    success: function(data)
                    {
                        var obj = eval('(' + data + ')');
                        $('#notifications-dropdown').empty();
                        $('#notifications-dropdown').html(obj.html);
                        unbindNotification();
                        loadNotification();
                    },
                    error: function(jqXHR, textStatus, errorThrown)
                    {
                        $('body').html(jqXHR.responseText);
                    }
                });
            }
            else
            {
                $('#notifications-dropdown').empty();
            }
            return false;
        }
    );

    $('#notifications-dropdown').bind('clickoutside',function(event)
    {
        $(this).empty();
        $(this).hide();
    });

    $('#logo-img').hover
        (
            function(){ $(this).attr('src','/static/images/top-logo-hover.png'); },
            function(){ $(this).attr('src','/static/images/top-logo-default.png'); }
        );

    function toggleUserMenu()
    {
        $('#user-menu').toggleClass("user-menu-unselected");
        $('#user-menu').toggleClass("user-menu-selected");
        $("#user-menu-dropdown").toggle('slide',{direction:'up'},10);
    }

    $('#user-menu-container').bind("clickoutside",function(event)
    {
        if ($('#user-menu-dropdown').css('display') != 'none')
        {
            $('#user-menu').removeClass("user-menu-selected");
            $('#user-menu').addClass("user-menu-unselected");
            $('#user-menu-dropdown').hide();
        }
    });

    $('#down-arrow').click(toggleUserMenu);

    $('#user-menu-account').click(function(event)
    {
        event.preventDefault();
        $(this).children('a').click();
        return false;
    });

    $('#user-menu-account').children('a').click(function(event)
    {
        toggleUserMenu();
        return false;
    });

    $('#user-menu-logout').click(function()
    {
        window.location = '/logout/'
    });

    /**
     * Handles style change for hover and selection in the user's dropdown menu.
     *
     * @param div$      jQuery object with class user-menu-dropdown-div
     */
    function userMenuDropDownColors(div$,color)
    {
        var replaceColor; var hexColor;
        if (color == "white") {hexColor = "#FFFFFF"; replaceColor = 'gray'}
        else { hexColor = "#000000"; replaceColor = 'white'}
        var src = div$.children('img').attr('src').replace(replaceColor,color);
        div$.children('img').attr('src',src);
        div$.children('a').css("color",hexColor)
    }

    $('.user-menu-dropdown-div').hover
        (
            function()
            {
                if (!$(this).hasClass("user-menu-dropdown-div-selected"))
                {
                    $(this).addClass('user-menu-dropdown-div-hover');
                    userMenuDropDownColors($(this),'white');
                }
            },
            function()
            {
                if (!$(this).hasClass("user-menu-dropdown-div-selected"))
                {
                    $(this).removeClass('user-menu-dropdown-div-hover');
                    userMenuDropDownColors($(this),'gray');
                }
            }
        );
    /**
     * Handles style change for selecting a security mode.
     *
     * @param security$     jQuery object for user-menu-security-<mode> div objects
     */
    function selectSecuritySetting(security$)
    {
        $('.user-menu-security').each(function()
        {
            $(this).removeClass('user-menu-dropdown-div-selected');
            $(this).removeClass('user-menu-dropdown-div-hover');
            userMenuDropDownColors($(this),'gray');
        });
        userMenuDropDownColors(security$,'white');
        security$.addClass("user-menu-dropdown-div-selected");
    }

    /**
     * Handles initial styling for security mode
     */
    switch($.cookie('privacy'))
    {
        case "PUB":
            selectSecuritySetting($('#user-menu-security-public'));
            break;
        case "PRI":
            selectSecuritySetting($('#user-menu-security-private'));
            break;
        default:
            $.cookie('privacy','PUB', {path:'/'});
            selectSecuritySetting($('#user-menu-security-public'));
            break;
    }

    /**
     * Set cookie for various security modes.  !LEARNING POINT: path of cookie is important
     */
    $("#user-menu-security-public").click(function(event)
    {
        $.cookie('privacy','PUB', {path:'/'});
        selectSecuritySetting($(this));
    });
    $("#user-menu-security-private").click( function(event)
    {
        $.cookie('privacy','PRI', {path:'/'});
        selectSecuritySetting($(this));
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

    $('.create-img').click(function()
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

    $('.create-wrapper').bind('clickoutside',function()
    {
        var wrapper = $(this);
        if (wrapper.hasClass('clicked')) { closeLeftSideWrapper(wrapper); }
    });

    $('#create-petition-button').click(function()
    {
        $('.create-content-div').hide();
        $('#create-petition-div').show();
    });

    $('#create-news-button').click(function()
    {
        $('.create-content-div').hide();
        $('#create-news-div').show();
    });

    $('#create-group-button').click(function()
    {
        $('.create-content-div').hide();
        $('#create-group-div').show();
    });

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
                    $('#news-link-generation').empty();
                    $('#news-link-generation').show();
                    $('#news-link-generation').append('<div style="width:530px;margin-bottom:25px"><img style="width:75px;height:75px;margin-left:235px;" id="loading-img" src="/static/images/ajax-loader.gif"></div>');
                    $('#news-summary').show();
                    ajaxPost({
                        data: {'action':'getLinkInfo','url':text},
                        success: function(data)
                        {
                            returned = eval('(' + data + ')');
                            $('#news-link-generation').html(returned.html);
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


    $('#create-petition').click(function(event)
    {
        event.preventDefault();
        var title = $('#input-title').val();
        var summary = $('#input-summary').val();
        var full_text = $('#input-full_text').val();
        var link = $('#input-link').val();
        var topic = $('input:radio[name=topics]:checked').val();
        ajaxPost({
            data: {'action':'create','title':title,'summary':summary, 'full_text':full_text,'link':link, 'topics':topic, 'type':'P'},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (returned.success == false)
                {
                    $("#errors-title").html(returned.errors.title);
                    $("#errors-summary").html(returned.errors.summary);
                    $("#errors-full_text").html(returned.errors.full_text);
                    $("#errors-topic").html(returned.errors.topics);
                    $("#errors-non_field").html(returned.errors.non_field_errors);
                }
                else
                {
                    $('.normal').show();
                    $('');
                    clearPetitionErrors();
                    History.pushState( {k:1}, returned.title, returned.url);
                    rebind = returned.rebind;
                    closeLeftSideWrapper($('.create-wrapper.clicked'));
                    replaceCenter(returned.html);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

    $('#create-group').click(function(event)
    {
        event.preventDefault();
        var title = $('#group-input-title').val();
        var full_text = $('#group-input-full_text').val();
        var privacy = $('input:radio[name=privacy]:checked').val();
        var topic = $('input:radio[name=topics]:checked').val();
        ajaxPost({
            data: {'action':'create',
                'title':title,
                'full_text':full_text,
                'topics':topic,
                'group_type':'U',
                'group_privacy':privacy,
                'type':'G'
            },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (returned.success == false)
                {
                    alert('errors')
                    $("#errors-title").html(returned.errors.title);
                    $("#errors-full_text").html(returned.errors.full_text);
                    $("#errors-topic").html(returned.errors.topics);
                    $("#errors-non_field").html(returned.errors.non_field_errors);
                }
                else
                {
                    window.location.href = returned.url;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

    $('#share-button').click(function(event)
    {
        event.preventDefault();
        var title = $('#news-input-title').val();
        var summary = $('#news-input-summary').val();
        var link = $('#news-input-link').val();
        var description = $('#news-link-generation-description').text();
        var screenshot = $('#news-link-image-src').attr("src");
        var topic = $('input:radio[name=topics]:checked').val();
        ajaxPost({
            data: {'action':'create','title':title,'summary':summary,'link':link,
                'type':'N', 'description':description, 'screenshot':screenshot, 'topics':topic},
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
 *      ~Feeds
 *
 ***********************************************************************************************************************/
/* feed buttons */
var feed_type = 'H';
var topics = [];
function scrollLoadFeed() { if  ($(window).scrollTop() == $(document).height() - $(window).height()) { getMore(feed_type);}}

function loadFeed()
{

    // feed
    $(".feed").hide();
    $("#hotfeed").show();
    $("#hot_button").css('background-color','#f0503b');

    // topic filters
    // select topic click function
    $(".filter-topic-img").click(function(event) {
        var wrapper = $(this).parents(".topic-icon-wrapper");
        toggleTopicIcon(wrapper);
    });

    // set heart buttons
    heartButtons();
    // heart display
    heartDisplay();

    /* set feed buttons */
    $('#new_button').click(function()
    {
        clearButtons();
        $("#newfeed").show();
        $("#new_button").css('background-color','#f0503b');
        feed_type = 'N';
    });

    $('#hot_button').click(function()
    {
        clearButtons();
        $("#hotfeed").show();
        $("#hot_button").css('background-color','#f0503b');
        feed_type = 'H';
    });

    $('#best_button').click(function() {
        clearButtons();
        $("#bestfeed").show();
        $("#best_button").css('background-color','#f0503b');
        feed_type = 'B';
    });

    // click topic icons to filter by topic (and get new feeds)
    $(".topic-filter").click(function() {
        var t = $(this).children(".t-alias").val();
        var index = $.inArray(t, topics);
        // if not in array, then append
        if (index == -1) {
            topics.push(t);
        }
        // else remove found item
        else {
            topics.splice(index, 1);
        }
        refreshFeeds();
    });

    // all topics button, refresh feeds
    $("#all-topics-button").click(function(event) {
        var wrapper = $(this).parent();
        wrapper.find(".chosen").removeClass("chosen");
        wrapper.find(".selected").hide();
        wrapper.find(".normal").show();
        topics = ["all"];
        refreshFeeds();
    });

    bindFeedItems();

    $(window).scroll(scrollLoadFeed);

    // more button
    $(".more-button").click(function(event)
    {
        event.preventDefault();
        getMore(feed_type);
    });
}

/**
 * Refreshes all feeds.
 */
function refreshFeeds()
{
    getNew('N');
    getNew('H');
    getNew('B');
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

/* feed stuff */
function clearButtons()
{
    $(".feed").hide();
    $(".dialogue-buttons").css('background-color','#ccc');
}


// append more items to the feed list
function getMore(feed_type)
{
    var s= parseInt($("#length" + feed_type).val());
    ajaxFeed(feed_type, topics, s, 5, false);
}

// refresh and replace the feed list
function getNew(feed_type)
{
    ajaxFeed(feed_type, topics, 0, 10, true);
}


function ajaxFeed(feed_type, topics, start, how_many, force_replace)
{
    var topics_serialized = JSON.stringify(topics);
    ajaxPost({
        data: {'action': 'ajaxFeed', 'feed_type':feed_type, 'topics':topics_serialized, 'start':start, 'how_many':how_many},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            // update position in feed
            $("#length" + feed_type).val(returned.position);
            // return feed html
            var feed = returned.feed;
            if (force_replace) { $("#" + feed_type).html(feed); }
            else { $("#" + feed_type).append(feed); }
            heartButtons();
            heartDisplay();
            bindFeedItems();
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            alert("failure");
            $("body").html(jqXHR.responseText);
        }
    });
}



////////////////////////////////////////////////////////////


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

    $('.heart').hover
        (
            function(event)
            {
                if (!$(this).hasClass('blue'))
                {
                    var src = $(this).attr('src');
                    src = src.replace('Grey','Blue');
                    $(this).attr('src',src);
                }
            },
            function(event)
            {
                if (!$(this).hasClass('blue'))
                {
                    var src = $(this).attr('src');
                    src = src.replace('Blue','Grey');
                    $(this).attr('src',src);
                }
            }
        );
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
}


/***********************************************************************************************************************
 *
 *      ~Profile
 *
 ***********************************************************************************************************************/
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

    $('#see_more_notifications').click(
        function(event)
        {
            event.preventDefault();
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
                    else if( obj.hasOwnPropery('error') )
                    {
                        $('body').html(obj.error);
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
    );

    $('#see_more_actions').click(
        function(event)
        {
            event.preventDefault();
            var num_actions = $("#num_actions").val();
            ajaxPost({
                'data': {'action':'getactions',
                    'num_actions':num_actions,
                    'p_id':p_id },
                success: function(data)
                {
                    var obj = eval('(' + data + ')');
                    $('#profile_activity_feed').append(obj.html);
                    $('#num_actions').val(obj.num_actions);
                    if( 'error' in obj && obj.error == 'No more actions' )
                    {
                        $('#see_more_actions').html('No more actions')
                        $('#see_more_actions').unbind();
                        $('#see_more_actions').click( function(event)
                        {
                            event.preventDefault();
                        });
                    }
                    else if( 'error' in obj )
                    {
                        $('body').html(obj.error);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $('body').html(jqXHR.responseText);
                }
            });
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
function groupFollowResponse(event,response,div,g_id)
{
    event.preventDefault();
    var follow_id = div.siblings(".follow-id").val();
    alert( follow_id );
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

function loadGroup()
{
    var loadUsersLockout = false;
    var loadHistoLockout = false;

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

    $("#group-follow").click( function(event) {
        event.preventDefault();
        ajaxPost({
                data: {
                    'action':'joingroup',
                    'g_id': g_id
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
    $("#group-unfollow").click( function(event) {
        event.preventDefault();
        ajaxPost({
                data: {
                    'action':'leavegroup',
                    'g_id': g_id
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
 Takes in a a value and the classname of an input which the value should
 either be added to or removed from that list (toggled).
 */
function listSelectHelper(value, list_input_name) {
    var list_input = $("." + list_input_name);
    var list_values = $.parseJSON(list_input.val());
    var index = $.inArray(value, list_values);
    if (index == -1) {
        list_values.push(value);
    }
    else {
        list_values.splice(index, 1);
    }
    list_input.val(JSON.stringify(list_values));
}

/*
 Replaces feed with all new items based on current parameters.
 */
function refreshFeed(num) {
    $(".feed_start").val(0);
    getFeed(num);
}

/*
 if the start value is 0, then replace feed with all new items based on current parameters
 else get new feed items starting at start value and append them to the current feed.
 */
function getFeed(num)
{

    if (num==-1) {
        num = 3;
    }

    var feed_ranking = $(".feed_ranking").val();
    var feed_display =  $(".feed_display").val();
    var feed_submissions_only =  $(".feed_submissions_only").val();     // limit to content created by members of selected groups
    var feed_topics = $.parseJSON($(".feed_topics").val());
    var feed_types =  $.parseJSON($(".feed_types").val());
    var feed_levels =  $.parseJSON($(".feed_levels").val());
    var feed_groups =  $.parseJSON($(".feed_groups").val());
    feed_topics = JSON.stringify(feed_topics);
    feed_types = JSON.stringify(feed_types);
    feed_levels = JSON.stringify(feed_levels);
    feed_groups = JSON.stringify(feed_groups);

    var feed_start = parseInt($(".feed_start").val());
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

            $(".feed_start").val(feed_start + returned.num);

            if (feed_display == "P") {
                pinterestRender($(".pinterest_unrendered"));
            }

            heartButtons();
            heartDisplay();

        },
        error: null
    });

}

/*
 makes a post to the server to save the current filter setting as the inputted name.
 */
function saveFilter() {

    var feed_name = $(".save-filter-name").val();

    var feed_ranking = $(".feed_ranking").val();
    var feed_display =  $(".feed_display").val();
    var feed_submissions_only =  $(".feed_submissions_only").val();     // limit to content created by members of selected groups
    var feed_topics = $.parseJSON($(".feed_topics").val());
    var feed_types =  $.parseJSON($(".feed_types").val());
    var feed_levels =  $.parseJSON($(".feed_levels").val());
    var feed_groups =  $.parseJSON($(".feed_groups").val());
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

            alert("success!");

            var returned = eval('(' + data + ')');

            clearFilterParameters();

            setRanking(returned.ranking);
            setDisplay(returned.display);
            setSubmissionOnly(returned.submissions_only);

            var feed_topics = $.parseJSON($(".feed_topics").val());
            var feed_types =  $.parseJSON($(".feed_types").val());
            var feed_levels =  $.parseJSON($(".feed_levels").val());
            var feed_groups =  $.parseJSON($(".feed_groups").val());


            feed_types.each(function(index) {
                alert($(this));
                addType($(this));
            });

            feed_topics.each(function(index) {
                addTopic($(this));
            });

            feed_groups.each(function(index) {
                addGroup($(this));
            });

            feed_levels.each(function(index) {
                addLevel($(this));
            });

        },
        error: null
    })
}

/* heart stuff */
function heartButtons()
{
    var container = $(".not-processed");
    container.hide();

    container.find(".heart").hover
        (
            function()
            {
                $(this).parent().children(".grey").hide();
                $(this).parent().children(".blue").show();

            },
            function()
            {
                var blue = $(this).parent().children(".blue");
                if (blue.hasClass("hide"))
                {
                    blue.hide();
                    $(this).parent().children(".grey").show();
                }
            }
        );

    container.find(".plus").click(function()
    {
        var content_id = $(this).parent().siblings(".c_id").val();
        var v='L';
        vote($(this),content_id, v);
    });

    container.find(".minus").click(function()
    {
        var content_id = $(this).parent().siblings(".c_id").val();
        var v='D';
        vote($(this),content_id, v);
    });

    container.removeClass("not-processed");
    container.show();
}

function heartDisplay()
{
    $(".hide").hide();
    $(".show").show();
}

function vote(div, content_id, v)
{
    ajaxPost({
        data: {'action':'vote','c_id':content_id, 'vote':v},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            var my_vote = parseInt(returned.my_vote);
            var status = returned.status;
            if (my_vote==1) { like(div); }
            if (my_vote==0) { neutral(div); }
            if (my_vote==-1) { dislike(div); }
            heartDisplay();
            // change status
            div.parent().parent().find(".post-score").text(status);
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $("body").html(jqXHR.responseText);
        }
    });
}

function like(div)
{
    var plus_blue = div.parent().parent().find(".plus.blue");
    var plus_grey = div.parent().parent().find(".plus.grey");
    var minus_blue = div.parent().parent().find(".minus.blue");
    var minus_grey = div.parent().parent().find(".minus.grey");
    show(plus_blue);
    hide(plus_grey);
    hide(minus_blue);
    show(minus_grey);
}
function dislike(div)
{
    var plus_blue = div.parent().parent().find(".plus.blue");
    var plus_grey = div.parent().parent().find(".plus.grey");
    var minus_blue = div.parent().parent().find(".minus.blue");
    var minus_grey = div.parent().parent().find(".minus.grey");
    hide(plus_blue);
    show(plus_grey);
    show(minus_blue);
    hide(minus_grey);
}
function neutral(div)
{
    var blue = div.parent().parent().find(".blue");
    var grey = div.parent().parent().find(".grey");
    hide(blue);
    show(grey);
}

function show(div)
{
    div.addClass("show");
    div.removeClass("hide");
}
function hide(div)
{
    div.addClass("hide");
    div.removeClass("show");
}

/*
 visually and in data representation sets all feed parameters to defaults
 */
function clearFilterParameters() {

    $(".feed_topics").val(JSON.stringify([]));
    var topic_icon_wrapper = $(".feed-topic-selector-wrapper");
    clearTopicIcons(topic_icon_wrapper);

    $(".feed_types").val(JSON.stringify([]));
    $(".feed-type-selector").attr("checked", false);

    $(".feed_levels").val(JSON.stringify([]));
    $(".feed-level-selector").attr("checked", false);

    $(".feed_groups").val(JSON.stringify([]));
    $(".feed-group-selector").attr("checked", false);

}


/*
 the following methods are helpers for get filter which apply the retrieved parameters to the page.
 */
function addTopic(t_id) {
    var t_wrapper = $(".feed-topic-icon-wrapper[data-id=" + t_id + "]");
    showTopicIcon(t_wrapper);
    listSelectHelper(t_id, 'feed_topics');
}

function addType(type) {
    listSelectHelper(type, 'feed_types');
    $(".feed-type-selector[value=" + type + "]").attr("checked", true);
}

function addLevel(level) {
    listSelectHelper(level, 'feed_levels');
    $(".feed-level-selector[value=" + level + "]").attr("checked", true);
}

function addGroup(g_id) {
    listSelectHelper(g_id, 'feed_groups');
    $(".feed-group-selector[value=" + g_id + "]").attr("checked", true);
}

function setSubmissionOnly(value) {
    $(".feed_submissions_only").val(value);
}

function setRanking(value) {
    $(".feed_ranking").val(value);
}

function setDisplay(value) {
    $(".feed_display").val(value);
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
        var height = $(this).find(".pinterest").height() + 20;
        $(this).css("position", 'absolute');
        $(this).css("left", left);
        $(this).animate({"top": top}, 1400);
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


/* binds everyting */
function loadNewFeed() {

    $(".get_feed").click(function(event) {
        event.preventDefault();
        getFeed(-1);
    });

    $(".refresh_feed").click(function(event) {
        event.preventDefault();
        refreshFeed(-1);
    });

    $(".feed-topic-img").click(function(event) {
        var wrapper = $(this).parents(".topic-icon-wrapper");
        toggleTopicIcon(wrapper);
        var value = $(this).parents(".feed-topic-icon-wrapper").attr("data-id");
        listSelectHelper(value, 'feed_topics');
        refreshFeed(-1);
    });

    $(".feed-type-selector").click(function(event) {
        var value = $(this).val();
        listSelectHelper(value, 'feed_types');
        refreshFeed(-1);
    });

    $(".feed-level-selector").click(function(event) {
        var value = $(this).val();
        listSelectHelper(value, 'feed_levels');
        refreshFeed(-1);
    });

    $(".feed-group-selector").click(function(event) {
        var value = $(this).val();
        listSelectHelper(value, 'feed_groups');
        refreshFeed(-1);
    });

    $(".feed-ranking-selector").click(function(event) {
        event.preventDefault();
        var ranking = $(this).attr("data-ranking");
        $(".feed_ranking").val(ranking);
        refreshFeed(-1);
    });

    $(".feed-display-selector").click(function(event) {
        event.preventDefault();
        var display = $(this).attr("data-display");
        $(".feed_display").val(display);
        refreshFeed(-1);
    });

    $(".save-filter-button").click(function(event) {
        event.preventDefault();
        saveFilter();
    });

    $(".my-filter-selector").click(function(event) {
        event.preventDefault();
        var value = $(this).attr("data-id");
        getFilter(value);
    });

    $(".feed-clear").click(function(event) {
        clearFilterParameters();
    });

    refreshFeed(6);

    //$(window).scroll(scrollFeed);


}
