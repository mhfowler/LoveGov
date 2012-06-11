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
            loadProfileComparison();
            break;
        case 'network':
            loadProfileComparison();
            loadNetwork();
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
 *      ~General
 *
 ***********************************************************************************************************************/

function loadHoverComparison()
{
    $('.feed-username').hoverIntent
    (
        // hover over
        function(event)
        {
            var self = $(this);
            var a = $(this).find('a');
            if (a.attr('href') != undefined)
            {
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
                $.ajax
                    ({
                        url:'/action/',
                        type:'POST',
                        data: {'action':'hoverComparison','alias':alias},
                        success: function(data)
                        {
                            var obj = eval('(' + data + ')');
                            $('#comparison-hover-loading-img').hide();
                            new VisualComparison('comparison-hover',obj).draw();
                        },
                        error: function(jqXHR, textStatus, errorThrown)
                        {
                            $('#comparison-hover-div p').text('Sorry there was an error');
                        }
                    });
            }
        },
        // hover out
        function(event)
        {
            $('#comparison-hover').empty();
            $('#comparison-hover-div').fadeOut(100);
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
            $(this).parent().children(".normal").hide();
            $(this).parent().children(".selected").show();
        },
        function(event)
        {
            var selected = $(this).parent().children(".selected");
            if (!(selected.hasClass("chosen")))
            {
                $(this).parent().children(".selected").hide();
                $(this).parent().children(".normal").show();
            }
        }
    );
}

// adjusts icons appropriately for topic selection, only one topic can be chosen at a time
function selectTopicSingle(div)
{
    var wrapper = div.closest(".topic-icons-wrapper");
    // unselect all others
    wrapper.find(".selected").hide();
    wrapper.find(".normal").show();
    // select this
    div.parent().children(".normal").hide();
    div.parent().children(".selected").show();
    // class chosen
    wrapper.find(".selected").removeClass("chosen");
    div.parent().children(".selected").addClass("chosen");
}

// adjusts icons appropriately for topic selection, multiple can be selected
function selectTopicMultiple(div)
{
    var wrapper = div.closest(".topic-icons-wrapper");
    // if this topic already selected, then remove chosen, else add chosen
    var selected =  div.parent().children(".selected");
    if (selected.hasClass("chosen")) {
        selected.removeClass("chosen");
        div.parent().children(".selected").hide();
        div.parent().children(".normal").show();
    }
    else {
        selected.addClass("chosen");
        div.parent().children(".selected").show();
        div.parent().children(".normal").normal();
    }
}

function loadAjaxifyAnchors()
{
    // Jquery's '.one' binds the handler to each link once
    // This prevents the function from being called multiple times
    $('.do-ajax-link').one('click',  function(event)
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
    });

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
        data: {},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            History.pushState( {k:1}, returned.title, returned.url);
            rebind = returned.rebind;
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
                $.ajax
                ({
                    type: 'GET',
                    url:'/actionGET/',
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
                    $.ajax
                    ({
                        type: 'GET',
                        url:'/actionGET/',
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
                        error: function(jqXHR, textStatus, errorThrown)
                        {
                            $('#news-link-generation').hide();
                            $('#news-summary').hide();
                        }
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
        // node references
        var thisNode = $(this);
        var chosen = $(this).hasClass('chosen');
        var wrapper = $(this).parent().parent();
        // clears topic choice by unchecking every radio button
        wrapper.find('.topic-radio').attr('checked',false);
        // removes class 'chosen' from current chosen and shows unselected topic image for every topic
        wrapper.find('.chosen').removeClass('chosen').hide().siblings('.normal').show();
        // if new topic was selected (or clicked topic image wasn't already chosen)
        if (!chosen)
        {
            // handles choosing new topic.
            thisNode.addClass('chosen');
            thisNode.siblings(".topic-radio").attr("checked","checked");
        }
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
        $.ajax
        ({
            type:'POST',
            url:'/action/',
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
                    $('')
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

    $('#share-button').click(function(event)
    {
        event.preventDefault();
        var title = $('#news-input-title').val();
        var summary = $('#news-input-summary').val();
        var link = $('#news-input-link').val();
        var description = $('#news-link-generation-description').text();
        var screenshot = $('#news-link-image-src').attr("src");
        var topic = $('input:radio[name=topics]:checked').val();
        $.ajax
        ({
            type:'POST',
            url:'/action/',
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
        $.ajax
        ({
            type:'POST',
            url:'/action/',
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
        $.ajax
        ({
            type:'POST',
            url:'/action/',
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
        selectTopicSingle($(this));
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
        selectTopicMultiple($(this));
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
    $.ajax
    ({
        url:'/action/',
        type: 'POST',
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
            //location.reload()
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
    $.ajax
    ({
        url:'/ajax/feed',
        type: 'POST',
        data: {'feed_type':feed_type, 'topics':topics_serialized, 'start':start, 'how_many':how_many},
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
    $.ajax
    ({
        url:'/action/',
        type: 'POST',
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
            $.ajax
            ({
                url:'/action/',
                type: 'POST',
                data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
                success: function(data)
                {
                    ajaxThread();
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    alert("Oops we made an error.  Try submitting again.")
                }
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
            $.ajax({
                url:'/action/',
                type: 'POST',
                data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
                success: function(data)
                {
                    ajaxThread();
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    alert("failed to submit");
                    $('body').replace(jqXHR.responseText);
                }
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
    $.ajax
    ({
        url:'/ajax/',
        type: 'POST',
        data: {'type':'thread', 'c_id':c_id},
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            $("#thread").html(returned.html);
            loadThread();
            return false;
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            alert("Failed to reload thread!  Sorry!")
        }
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
 *      ~Petition
 *
 ***********************************************************************************************************************/
function loadPetition()
{

    $("#sign-button").click(function(event)
    {
        event.preventDefault();
        $.ajax
            ({
                type:'POST',
                url:'/action/',
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
        $.ajax
        ({
            type:'POST',
            url:'/action/',
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


function loadNetwork()
{
    var loadingLockout = false;

    function loadMoreUsers(event)
    {
        event.preventDefault();
        var num = $('#network-displaynum').val();
        var id = $('#network-id').val();
        if (!loadingLockout)
        {
            loadingLockout = true;
            $.ajax
            ({
                url:'/actionGET/',
                type: 'GET',
                data: {'action':'loadNetworkUsers','num':num,'id':id},
                success: function(data)
                {
                    var returned = eval('(' + data + ')');
                    $('#members-list').append(returned.html);
                    $('#network-displaynum').val(returned.num);
                    loadHoverComparison();
                    loadAjaxifyAnchors();
                    bindNewDivs();
                    loadingLockout = false;
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    alert("failed to submit");
                }
            });
        }
    }

    function bindNewDivs()
    {
        $('.network-member-div').hover
        (
            function(){ $(this).css("background-color","#EBEBEB") },
            function(){ $(this).css("background-color","#FFFFFF") }
        );

    }


    $(window).scroll(function(event)
    {
        if  ($(window).scrollTop() == $(document).height() - $(window).height()) { loadMoreUsers(event); }
    });

    $('#network-see-more-users').click(function(event)
    {
        loadMoreUsers(event);
    });

    bindNewDivs();




}