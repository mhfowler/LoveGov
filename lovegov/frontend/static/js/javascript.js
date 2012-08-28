/***********************************************************************************************************************
 *
 *     ~init js, does stuff that delegated can't!
 *
 ***********************************************************************************************************************/
var rebind;
function bindOnReload() {

    // things that get bound on items loaded by feeds and such (everything)
    bindOnNewElements();

    // ajax get fb friends for sidebar after page load
    getFBInviteFriends();

    // any feeds on the page, go get themselves
    refreshFeeds();

    // for all home pages
    navSectionOpenAll();
    initHomePage();

    // for reps page
    loadGoogleMap();

    // misc
    bindNotificationsDropdownClickOutside();

    switch (rebind) {
        case "home":
            break;
        case "profile":
            break;
        case "groupedit":
            loadGroupEdit();
            break;
        case 'questions':
            break;
        case 'question_detail':
            updateQuestionStubsDisplay();
            break;
        case 'poll_detail':
            updateQuestionStubsDisplay();
            break;
        case 'browse':
            break;
    }
}

/* gets called on all new elements appended to dom */
function bindOnNewElements() {

    // dummy_links are prevent defaulted
    undelegated();

    // hover comparison popup
    loadHoverComparison();

    // all histogram go get themselves  (because there is a feed of groups, this must be here)
    loadHistograms();

    // all expandable headers set themselves to correct starting height
    $.each($(".expandable_wrapper"), function(i,e) {
        setInfoHeight($(this));
    });

    // poll feed items autoswitch
    pollAutoSwitch();

    // comparison webs initialize
    comparisonWebs();

    // bind select2s
    bindSelect2s();

    // question stubs
    bindImportanceSliders();

    // tool tips
    bindTooltips();
}

/***********************************************************************************************************************
 *
 *     ~document.ready() of initial page load
 *
 ***********************************************************************************************************************/




var auto_update_page;

$(document).ready(function()
{
    // csrf protect
    $.ajaxSetup({ data: {csrfmiddlewaretoken: csrf} });

    // check browser compatability
    checkCompatability();

    // Prepare
    var History = window.History; // Note: We are using a capital H instead of a lower h
    if ( !History.enabled )
    {
        // History.js is disabled for this browser.
        // This is because we can optionally choose to support HTML4 browsers or not.
        return false;
    }
    // Bind to StateChange Eveent
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

    // init page with js
    bindOnReload();

    // auto page update every minute (check for notifications)
    clearInterval(auto_update_page);
    auto_update_page= setInterval(function()
    {
        updatePage();
    }, 60000);
});

var auto_update_page;


/***********************************************************************************************************************
 *
 *     ~Delegated binding function, similar to jquery's deprecated ".live()"
 *
 ***********************************************************************************************************************/
function bind(selector, events, data, handler) {
    $(document).on(events, selector, data, handler);
}

var current_page_nonce=0;
function action(dict) {
    var data = dict['data'];
    var pre_page_nonce = current_page_nonce;
    var success_fun = function(data) {
        if (pre_page_nonce == current_page_nonce) {
            var super_success = dict['success'];
            if (super_success) {
                super_success(data);
            }
            undelegated();
        }
    };
    var error_fun = function(jqXHR, textStatus, errorThrown) {
        if (pre_page_nonce == current_page_nonce) {
            if(jqXHR.status==403) {
                //launch403Modal(jqXHR.responseText);
                return;
            }
            var super_error = dict['error'];
            if (super_error) {
                super_error();
            } else {
                $("body").html(jqXHR.responseText);
            }
        }
    };
    var complete_fun = dict['complete'];
    data['url'] = window.location.href;
    $.ajax({
        url: '/action/',
        type: 'POST',
        data: data,
        success: success_fun,
        error: error_fun,
        complete: complete_fun
    });
}

function smoothTransition(element, fun, time) {
    var old_height = element.height();
    fun();
    var new_height = element.height();
    element.css("height", old_height);
    element.css('height', old_height);
    element.animate({"height":new_height}, {"duration":time, "complete":function(){element.css("height", "auto");}});
}


function updatePage() {
    action({
        'data': {'action':'updatePage', 'log-ignore':true},
        success: function(data)
        {
            var obj = eval('(' + data + ')');

            // update notifications num
            $(".notifications_dropdown_button").text(obj.notifications_num);
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('body').html(jqXHR.responseText);
        }
    });
}

/***********************************************************************************************************************
 *
 *      ~Ajax links
 *
 ***********************************************************************************************************************/
bind(".header_link", 'click', null, function(event) {
    $(".header_link").removeClass("clicked");
    $(this).addClass("clicked");
});

bind(".do_ajax_link", 'click', null, function(event) {
    ajaxReload($(this).attr("href"), true);
});

function ajaxReload(theurl, loadimg)
{
    current_page_nonce += 1;
    var pre_page_nonce = current_page_nonce;
    $('#search-dropdown').hide();
    $('.main_content').hide();
    if (loadimg) { var timeout = setTimeout(function(){$("#loading").show();},0); }
    $.ajax
        ({
            url:theurl,
            type: 'GET',
            data: {'url':window.location.href},
            success: function(data)
            {
                if (pre_page_nonce == current_page_nonce) {
                    var returned = eval('(' + data + ')');
                    History.pushState( {k:1}, "LoveGov: Beta", returned.url);
                    if (loadimg) { clearTimeout(timeout); $("#loading").hide(); }
                    $('body').css("overflow","scroll");
                    $('.main_content').css("top","0px");
                    $(".main_content").html(returned.html);
                    $('.main_content').show();
                    rebind = returned.rebind;
                    path = returned.url;
                    bindOnReload();
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                if (pre_page_nonce == current_page_nonce) {
                    $('body').html(jqXHR.responseText);
                }
            }
        });
}

/***********************************************************************************************************************
 *
 *     ~random helpers/bindings
 *
 ***********************************************************************************************************************/
function undelegated() {
    var undelegated = $('.dummy_link');
    undelegated.bindOnce('click.undelegate', function(event) {
        event.preventDefault();
    });
}

var poll_autoswitch;
function pollAutoSwitch() {
    clearInterval(poll_autoswitch);
    /*
     poll_autoswitch= setInterval(function()
     {
     cyclePollQuestions();
     }, 5000); */
}

function comparisonWebs() {
    $.each($(".web_comparison"), function(i,e) {
        $(this).visualComparison();
    });
}

/* does some javascript manipulation of home page */
function initHomePage() {
    var navlink = getNavLink(path);
    selectNavLink(navlink);
    initFeedParameters();
}

/* sets feed parameters pased on js variables */
function initFeedParameters() {
    selectRank(feed_rank);
    selectQuestionRank(question_rank);
    $.each(feed_types, function(i, e) {
        selectType(e);
    });
}

/* does a get request for all feeds on page */
function refreshFeeds() {
    $.each($(".feed_main"), function(i,e) {
        refreshFeed($(this));
    });
}

/* check browser compatability using modernizer */
function checkCompatability() {
    var compatability_cookie =  $.cookie('compatability');
    if (compatability_cookie == null) {
        var incompatible = [];
        $.each(Modernizr, function(index, element) {
            if (!element) {
                incompatible.push(index);
            }
        });
        var incompatible_json = JSON.stringify(incompatible);
        action({
                data: {'action': 'logCompatability', 'incompatible': incompatible_json},
                success: function(data) {
                    $.cookie('compatability', incompatible_json);
                }}
        );
    }
}

/* binds all select 2s */
function bindSelect2s() {
    $.each($('.select_2'), function(i,e) {
        var placeholder = $(this).data("placeholder");
        $(this).select2({
            placeholder: placeholder
        });
    });
}

/***********************************************************************************************************************
 *
 *      ~Bind popovers
 *
 ***********************************************************************************************************************/

function bindTooltips() {
    /*
     $('body').tooltip({'selector': '.tooltip-top', 'placement': 'top'});
     $("body").tooltip({'selector': '.tooltip-right', 'placement': 'right'});
     $("body").tooltip({'selector': '.tooltip-left', 'placement': 'left'});
     $("body").tooltip({'selector': '.tooltip-bottom', 'placement': 'bottom'});
     */

    $(".tooltip-top").tooltip({'placement': 'top', 'animation': 'true'});
    $(".tooltip-bottom").tooltip({'placement': 'bottom', 'animation': 'true'});
    $(".tooltip-right").tooltip({'placement': 'right', 'animation': 'true'});
    $(".tooltip-left").tooltip({'placement': 'left', 'animation': 'true'});
}

bind(".bind_link", "click", null, function(event) {
    event.preventDefault();
    var url = $(this).data('url');
    window.location.href = url;
});


/***********************************************************************************************************************
 *
 *      ~Home
 *
 ***********************************************************************************************************************/
/* ajax load home sections */
function homeReload(theurl) {
    current_page_nonce += 1;
    var pre_page_nonce = current_page_nonce;
    $('#search-dropdown').hide();
    $(".home_reloading").show();
    $.ajax
        ({
            url:theurl,
            type: 'POST',
            data: {'url':window.location.href},
            success: function(data)
            {
                if (pre_page_nonce == current_page_nonce) {
                    $(".home_reloading").hide();
                    var returned = eval('(' + data + ')');
                    History.pushState( {k:1}, "LoveGov: Beta", returned.url);
                    path = returned.url;
                    $(".home_focus").html(returned.focus_html);
                    bindOnReload();
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                if (pre_page_nonce == current_page_nonce) {
                    $('body').html(jqXHR.responseText);
                }
            }
        });
}

/* move asterisk, when section is selected */
function moveAsterisk(to_where) {
    if (to_where.length!=0) {
        if (to_where.hasClass("navbar_link")) {
            var offset = -4;
        } else {
            offset = to_where.height()/2;
        }
        var position = to_where.offset();
        var top = position.top - offset;
        var left = position.left - 40;
        $(".asterisk_pointer").animate({'top':top, 'left':left}, 100);
    }
}

/* fill fb invite sidebar after page load */
function getFBInviteFriends() {
    var invite_wrapper = $(".fb_friends_wrapper");
    if (invite_wrapper.length!=0) {
        action({
            data: {'action':'getFBInviteFriends' },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                invite_wrapper.html(returned.html)
            }
        });
    }
}

/* red triangle toggles navsection options */
bind(".red_triangle", 'click', null, function(event) {
    var navbar_section = $(this).parents(".navbar_section");
    event.preventDefault();
    if ($(this).hasClass("clicked")) {
        navSectionToggle(navbar_section, false, true);
    } else {
        navSectionToggle(navbar_section, true, true);
    }
});

/* reload home page, by just replacing focus */
bind(".home_link", 'click', null, function(event) {
    var navbar_section = $(this).parents(".navbar_section");
    event.preventDefault();
    if (!$(this).hasClass("clicked")) {
        selectNavLink($(this));
        //closeAllNavBarSections();
        //navSectionToggle(navbar_section, true, true);
        homeReload($(this).attr("href"));
    } else {
        /*
         if (navbar_section.hasClass("section_shown")) {
         navSectionToggle(navbar_section, false, true);
         } else {
         navSectionToggle(navbar_section, true, true);
         } */
    }
});

function closeAllNavBarSections() {
    $.each($(".navbar_section"), function(i,e) {
        var navbar_section = $(this);
        navSectionToggle(navbar_section, false, false);
    });
}

/* reload home page, by just replacing focus */
bind(null, 'keydown', null, function(event) {
    var change = 0;
    var active = $(document.activeElement);
    if (!active.is("textarea")) {
        switch (event.which) {
            case 38: change=-1; break;
            case 40: change=1; break;
        }
    }
    if (change) {
        event.preventDefault();
        var current_selected = $(".home_link.clicked");
        if (current_selected) {
            var current_sequence = current_selected.data('sequence');
            var next_sequence = current_sequence + change;
            var navlink = $('.home_link[data-sequence="' + next_sequence + '"]');
            if (navlink.length) {
                selectNavLink(navlink);
                homeReload(navlink.attr("href"));
            }
        }
    }
});


// opens all navbar sections
function navSectionOpenAll() {
    $.each($(".navbar_section"), function(i,e) {
        navSectionToggle($(this), true, true);
    });
}


function navSectionToggle(navbar_section, show, animate) {
    if (animate) {
        var animation_time = 100;
    } else {
        animation_time = 0;
    }
    if (show) {
        navSectionShow(navbar_section, animation_time);
    } else {
        navSectionHide(navbar_section, animation_time);
    }
}

function selectNavLink(navlink) {
    if (navlink.length!=0) {
        $(".home_link").removeClass("clicked");
        navlink.addClass("clicked");
        if (navlink.hasClass("navbar_link")) {
            var navbar_section = navlink.parents(".navbar_section");
            navSectionToggle(navbar_section, true, false);
        }
        //moveAsterisk(navlink);
    }
}

/* helper to get navlink element from url */
function getNavLink(url) {
    return $('.home_link[href="' + url + '"]');
}

function navSectionHide(navbar_section, animation_time) {
    // red triangle
    var redtriangle = navbar_section.find(".red_triangle");
    if (redtriangle.length!=0) {
        redtriangle.removeClass("red-triangle-down");
        redtriangle.removeClass("clicked");
    }
    // nav bar links
    var navbarlinks = navbar_section.find(".navbar_links_wrapper");
    if (navbarlinks.length!=0) {
        navbarlinks.animate({"height":'0px'}, animation_time);
    }
    navbar_section.removeClass("section_shown");
    // check if currently selected link is in section being hidden, in which case asterisk moves
    /*
     var current_link = getNavLink(path);
     if (current_link) {
     var current_wrapper = current_link.parents(".navbar_links_wrapper");
     if (current_wrapper.attr("class") == navbarlinks.attr("class")) {
     var to_where = current_link.parents(".navbar_section").find(".section_title");
     moveAsterisk(to_where);
     }
     } */
}
function navSectionShow(navbar_section, animation_time) {
    if (!navbar_section.hasClass("section_shown")) {
        navbar_section.addClass("section_shown");
        var redtriangle = navbar_section.find(".red_triangle");
        var navbarlinks = redtriangle.siblings(".navbar_links_wrapper");
        redtriangle.addClass("red-triangle-down");
        navbarlinks.css('height', 'auto');
        var autoHeight = navbarlinks.height();
        navbarlinks.css('height', '0px');
        navbarlinks.animate({"height":autoHeight}, {"duration":animation_time, "complete":function(){navbarlinks.css("height", "auto");}});
        redtriangle.addClass("clicked");
        // check if currently selected link is in section being hidden
        var current_link = getNavLink(path);
        if (current_link) {
            var current_wrapper = current_link.parents(".navbar_links_wrapper");
            if (current_wrapper.attr("class") == navbarlinks.attr("class")) {
                moveAsterisk(current_link);
            }
        }
    }
}

/* expands home header to show expanded info */
bind(".expand_info", 'click', null, function(event) {
    var wrapper = $(this).parents(".expandable_wrapper");
    expandInfoToggle(wrapper, true);
});

bind(".hide_info", 'click', null, function(event) {
    var wrapper = $(this).parents(".expandable_wrapper");
    hideInfoToggle(wrapper, true);
});

/* toggles the info's expanded state */
function expandInfoToggle(wrapper, animate)
{
    if (animate) {
        var animation_time = 100;
    } else {
        animation_time = 0;
    }

    var info_div = wrapper.find(".home_header_info");
    var info_hidden = wrapper.data('info_hidden');
    var info_expanded = wrapper.data('info_expanded');
    var reduced_height = info_div.data("height");

    // If info is hidden, expand the info to it's previous expanded state
    if( info_hidden )
    {   // Set info hidden to false
        wrapper.data('info_hidden', false);
        wrapper.find(".hide_info").text('- minimize info');
        // If the info was un-expanded, show it at un-expanded form
        if( !info_expanded )
        {
            info_div.animate({"height":reduced_height}, animation_time);
            wrapper.find(".expand_info").text('+ expand info');
        } // If the info was expanded, show the full expanded form
        else
        {
            expandAnimation(info_div,animation_time);
            wrapper.find(".expand_info").text('- reduce info');
        }
    }
    // Otherwise, toggle the info expanded property
    else if( info_expanded )
    {   // Set expanded to false and un-expand the info
        wrapper.data('info_expanded', false);
        info_div.animate({"height":reduced_height}, animation_time);
        wrapper.find(".expand_info").text('+ expand info');
    }
    else
    {   // Otherwise set expanded to true and expand the info
        wrapper.data('info_expanded', true);
        expandAnimation(info_div,animation_time);
        wrapper.find(".expand_info").text('- reduce info');
    }
}

/* toggles the info's hidden state */
function hideInfoToggle(wrapper, animate)
{
    if (animate) {
        var animation_time = 100;
    } else {
        animation_time = 0;
    }

    var info_div = wrapper.find(".home_header_info");
    var info_hidden = wrapper.data('info_hidden');
    var info_expanded = wrapper.data('info_expanded');

    if( info_hidden )
    {
        expandInfoToggle(wrapper, animate);
    }
    else
    {
        wrapper.data('info_hidden', true);
        info_div.animate({"height":'0px'}, animation_time);
        wrapper.find(".expand_info").text('+ show info');
        wrapper.find(".hide_info").text('+ show info');
    }

}

/* checks and sets the proper info state based on the two info booleans */
function setInfoHeight(wrapper)
{
    var info_div = wrapper.find(".home_header_info");
    var info_hidden = wrapper.data('info_hidden');
    var info_expanded = wrapper.data('info_expanded');
    var reduced_height=info_div.data("height");

    if( info_hidden )
    {
        info_div.css("height",'0px');
        info_div.css("overflow",'hidden');
    }
    else if( info_expanded )
    {
        info_div.css("height",'auto');
        info_div.css("overflow",'hidden');
    }
    else
    {
        info_div.css("height",reduced_height);
        info_div.css("overflow",'hidden');
    }
}

/* expands a div from it's current height to the "auto" height */
function expandAnimation( div , animation_time)
{
    var beforeHeight = div.height();
    div.css('height', 'auto');
    var autoHeight = div.height();
    div.css('height', beforeHeight + 'px');
    div.animate( { "height" : autoHeight } , animation_time);
}

/***********************************************************************************************************************
 *
 *      ~Sign In Dialogue
 *
 **********************************************************************************************************************/
bind(".sign-in-input", 'focusin', null, function(event) {
    $(this).val("");
    $(this).css('color', 'black');
});

bind(".sign-in-input", 'focusout', null, function(event) {
    var entered = $(this).val();
    if (entered == "") {
        $(this).val($(this).data('orig'));
        $(this).css('color', '#adadad');
    }
});

bind(null, "click", null, function(event) {
    if ((event.target.id != "sign_in_button")) {
        $(".sign_in_dialogue").hide();
    }
});

bind(".sign_in_button", 'click', null, function(event) {
    $(".sign_in_dialogue").toggle();
});

bind(".sign_in_dialogue", 'click', null, function(event) {
    event.stopPropagation();
});


/***********************************************************************************************************************
 *
 *      ~Feed
 *
 **********************************************************************************************************************/

// Votes on the feed Binding
bind( "div.heart_plus" , "click" , null , function(event)
{
    var wrapper = $(this).parent();
    var c_id = wrapper.data('c_id');
    vote( wrapper , c_id , 1 );
});

bind( "div.heart_minus" , "click" , null , function(event)
{
    var wrapper = $(this).parent();
    var c_id = wrapper.data('c_id');
    vote( wrapper , c_id , -1 );
});

// Vote for the feed AJAX request
function vote(wrapper, content_id, v)
{
    action({
        data: {'action':'vote','c_id':content_id, 'vote':v },
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            var my_vote = parseInt( returned.my_vote );
            var status = returned.status;

            if ( my_vote==1 ) { like(wrapper); }
            if ( my_vote==0 ) { neutral(wrapper); }
            if ( my_vote==-1 ) { dislike(wrapper); }

            wrapper.find(".heart_number").text(status);
        }
    });
}

// Vote for the feed GUI update functions
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

/* click through poll sample */
bind(".poll_arrow", 'click', null, function(event) {
    var direction = $(this).data("direction");
    nextPollQuestion($(this).parents(".sample_question"), direction);
});

function nextPollQuestion(sample_question, direction) {
    var p_id = sample_question.data('p_id');
    var which = sample_question.data("which");
    var data = {'action':'getNextPollQuestion', 'p_id':p_id, 'which':which, 'direction':direction};
    action({
        data:data,
        success:function(data) {
            var returned = eval('(' + data + ')');
            sample_question.replaceWith(returned.html);
        }
    });
}

function cyclePollQuestions() {
    $.each($(".sample_question"), function(i,e) {
        nextPollQuestion($(this), 1);
    });
}

/* filter buttons */
bind(".rank_button" , "click" , null , function(event) {
    selectRank($(this).data('rank'));
});

/* filter buttons */
bind(".topic_button" , "click" , null , function(event) {
    event.preventDefault();
    if (!$(this).hasClass("clicked")) {
        $(".topic_button").removeClass("clicked");
        $(this).addClass("clicked");
        feed_topic=$(this).data("t_alias");
    }
    else {
        $(this).removeClass("clicked");
        feed_topic=null;
    }
});

/* filter buttons */
bind(".question_button" , "click" , null , function(event) {
    selectQuestionRank($(this).data('rank'));
});

function selectRank(rank) {
    var which = $('.rank_button[data-rank="' + rank + '"]');
    $(".rank_button").removeClass("clicked");
    which.addClass("clicked");
    feed_rank = rank;
}

function selectQuestionRank(rank) {
    var which = $('.question_button[data-rank="' + rank + '"]');
    $(".question_button").removeClass("clicked");
    which.addClass("clicked");
    question_rank = rank;
}

bind(".type_button" , "click" , null , function(event) {
    if (!$(this).hasClass("clicked")) {
        selectType($(this).data('type'));
    }
    else {
        removeType($(this).data('type'));
    }
});

function selectType(type) {
    var which = $('.type_button[data-type="' + type + '"]');
    which.addClass("clicked");
    var index = $.inArray(type, feed_types);
    if (index == -1) {
        feed_types.push(type);
    }
}

function removeType(type) {
    var which = $('.type_button[data-type="' + type + '"]');
    which.removeClass("clicked");
    var index = $.inArray(type, feed_types);
    if (index != -1) {
        feed_types.splice(index, 1);
    }
}

/* clicking any feed button, regets the feed */
bind(".feed_button" , "click" , null , function(event) {
    event.preventDefault();
    var container = $(this).parents(".feed_main");
    refreshFeed(container);
});

/* replaces feed, rather than appendin */
function refreshFeed(container) {
    container.data('feed_start', 0);
    getFeed(container);
}

var feed_types = [];
var feed_rank = 'H';
var feed_topic = null;
var question_rank = "R";
function getFeed(container) {
    var feed_start = container.data('feed_start');
    var replace = (feed_start==0);
    if (replace) {
        var old_height = $("body").height();
        $("body").css('min-height', old_height);
        container.find(".feed_content").empty();
        container.find(".load_more").show();
        container.find(".everything_loaded_wrapper").hide();
    }
    var feed_types_json = JSON.stringify(feed_types);
    var feed = container.data('feed');
    var time = 10;
    var feed_timeout = setTimeout(function(){
        container.find(".feed_fetching").show();
    },time);
    var data;
    if (feed == 'getFeed')
    {
        data = {'action': 'getFeed', 'path': path, 'feed_rank':feed_rank, 'feed_start':feed_start, 'feed_types':feed_types_json};
    }
    else if (feed == 'getQuestions')
    {
        var default_display = container.data("default_display");
        data = {'action': 'getQuestions', 'feed_rank':feed_rank, 'question_rank':question_rank,
            'feed_start':feed_start, 'feed_topic':feed_topic, 'default_display':default_display};
        // if feed is comparing responses with other user
        var to_compare_id = container.data("to_compare_id");
        if (typeof(to_compare_id) != 'undefined') {
            data['to_compare_id'] = to_compare_id;
        }
        // only unanswered
        var only_unanswered = container.data('only_unanswered');
        if (typeof(only_unanswered) == 'undefined') {
            only_unanswered = false;
        }
        data['only_unanswered'] = only_unanswered;
        // if this feed appears on a poll
        var p_id = container.data('p_id');
        if (typeof(p_id) != 'undefined') {
            data['p_id'] = p_id;
        }
        // if this feed appears on a scorecard
        var scorecard_id = container.data("scorecard_id");
        if (typeof(scorecard_id) != 'undefined') {
            data['scorecard_id'] = scorecard_id;
        }
    }
    else if (feed == 'getUserActivity')
    {
        var p_id = container.data('p_id');
        data = { 'action': 'getUserActivity', 'feed_start':feed_start, 'p_id':p_id };
    }
    else if (feed == 'getElections')
    {
        data = {'action': 'getElections','feed_rank':feed_rank, 'feed_start':feed_start};
    }
    else if (feed == 'getGroups') {
        data = {'action': 'getGroups','feed_rank':feed_rank, 'feed_start':feed_start};
    }
    action({
            data: data,
            success: function(data) {
                var returned = eval('(' + data + ')');
                if (replace) {
                    container.find(".feed_content").html(returned.html);
                }
                else {
                    container.find(".feed_content").append(returned.html);
                }
                container.data( 'feed_start' , feed_start + returned.num_items );
                clearTimeout(feed_timeout);
                container.find(".feed_fetching").hide();
                if (returned.num_items == 0) {
                    container.find(".load_more").hide();
                    var everything_loaded = container.find(".everything_loaded_wrapper");
                    everything_loaded.find(".everything_loaded_image_wrapper").html(returned.everything_loaded);
                    everything_loaded.show();
                    everything_loaded.find(".everything_loaded_header").hide();
                    if (feed_start==0) {
                        everything_loaded.find(".nothing_there").show();
                    }
                    else {
                        everything_loaded.find(".reached_the_end").show();
                    }
                }
                updateQuestionStubsDisplay();
                bindOnNewElements();
                //container.css("min-height", container.height());
            }}
    );
}

/* load more feed items */
bind(".load_more" , "click" , null , function(event) {
    var container = $(this).parents(".feed_main");
    getFeed(container);
});


/***********************************************************************************************************************
 *
 *      ~About page
 *
 **********************************************************************************************************************/
bind("div.about-div-button", "click",
    function(e) {
        $('div.about-div-button').removeClass("active");
        $("div.about-section").hide();
        var section = ($(this).data('show'));
        $('div#'+section).fadeIn(250);
        $(this).toggleClass('active');
        teamSection();
    });

function teamSection()
{

    var developerDivs = $('.who-are-we-circle-div');
    var h3 = $('.who-are-we-circle-div-center h3');

    var text = $('.mission p').text();

    developerDivs.each(function()
    {
        var json = $(this).data('json');
        $(this).animate({'left':json.x,'top':json.y});
    });

    developerDivs.each(function()
    {
        $(this).hover
            (
                function()
                {
                    var json = $(this).data('json');
                    $(this).addClass($(this).attr("class") + '-hover');
                    $('.who-are-we-circle-div-center').css('background-color','white');
                    $('.who-are-we-circle-div-center div').show();
                    $('.who-are-we-circle-div-center div').children('h5').text(json['first_name'] + " " + json['last_name']);
                    $('.who-are-we-circle-div-center div').children('h6').text(json['user_title']);
                    h3.hide();
                },
                function()
                {
                    $(this).removeClass($(this).attr("class").split(' ')[1] + '-hover');
                    $('.who-are-we-circle-div-center').css('background-color','');
                    $('.who-are-we-circle-div-center div').hide();
                    h3.show();
                });

    });
}

/***********************************************************************************************************************
 *
 *      ~Left sidebar
 *
 **********************************************************************************************************************/


bind('.left-side-img', 'click', function()
{
    var parent = $(this).parent();
    leftSideToggle(parent);
});

bind('#feedback-submit', 'click', function(event)
{
    event.preventDefault();
    var text = $('#feedback-text').val();
    var name = $('#feedback-name').val();
    action({


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
            //alert("failure");
        }
    });
});

function sendInvitation(event)
{
    event.preventDefault();
    var email = $("#email-input").val();
    $("#invite-return-message").text("");
    $("#invite-return-loading-img").show();
    action({
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


bind('#email-input','keydown', function(event)
{
    if (event.keyCode == 13)
    {
        sendInvitation(event);
    }
});

bind("#invite-button",'click',function(event)
{
    sendInvitation(event);
});



function closeLeftSideWrapper(wrapper)
{

    if (wrapper.hasClass('create-wrapper-large')) { wrapper.animate({left:'-603px'},500); }
    else { wrapper.animate({left:'-493px'},500); }
    setTimeout(function()
    {
        wrapper.css({'z-index':'100'});
        wrapper.children('.create' +
            'e-img').css({'z-index':'101'});
    },500);

    wrapper.removeClass('clicked');
}

function leftSideToggle(wrapper)
{
    if (wrapper.hasClass('clicked'))
    {
        closeLeftSideWrapper(wrapper);
    }
    else
    {
        wrapper.addClass('clicked');
        wrapper.css({'z-index':'101'});
        wrapper.children('.create-img').css({'z-index':'102'});
        wrapper.animate({left:'-1px'},500);

        wrapper.bindOnce('clickoutside',function(event)
        {
            if (event.target.className != "footer_button") {
                closeLeftSideWrapper(wrapper);
            }
        });
    }

}


/***********************************************************************************************************************
 *
 *      ~User menu
 *
 ***********************************************************************************************************************/
bind(".user_menu_toggle", "click", function(event) {
    $('div.user-menu').fadeToggle(50);
    event.stopPropagation();
});

bind(null, "click", function(e) {
    $('div.user-menu').hide();
});

bind('div.user-menu', "click", function(event) {
    event.stopPropagation();
});

function toggleUserMenu()
{
    $('.user-menu').toggleClass("user-menu-unselected");
    $('.user-menu').toggleClass("user-menu-selected");
    $("#user-menu-dropdown").toggle('slide',{direction:'up'},10);
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

/***********************************************************************************************************************
 *
 *      ~Comment threads
 *
 ***********************************************************************************************************************/

    // Cancel button click
bind("div.reply .tab-button.cancel", "click", function(event) {

    $(this).parent("div.reply").hide();
});


bind("div.reply .tab-button.save", "click", function(event) {
    var reply = $(this).parent("div.reply");
    var textarea = $(this).siblings("textarea.comment-textarea");
    var text = textarea.val();
    var content_id = reply.data("reply-to");
    var depth = reply.data("depth") + 1;
    if(goodLength(text)) {
        if(reply.hasClass("reply-reply") || reply.hasClass("reply-new")) {
            action({
                'data': {'action':'comment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    if(depth > 0) {
                        reply.hide();
                        $(data).hide().appendTo(reply.closest('div.threaddiv')).fadeIn(500);
                    } else {
                        textarea.val('');
                        $(data).hide().prependTo('div.thread').fadeIn(500);
                    }
                }
            });
        } else if(reply.hasClass("reply-append")) {
            action({
                'data': {'action':'appendComment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    reply.closest('div.comment').find('div.comment-text').html(data);
                    reply.hide();
                }
            });
        }
    }

});

// Returns true if text length is short enough
// Otherwise alerts warning and returns false
function goodLength(text) {
    var len = text.length;
    if (len < 10000) {
        return true;
    } else {
        alert("Please limit your response to 10,000 characters.  You have currently typed " + len + " characters.");
        return false;
    }
}


function incNumComments() {
    var ncspan = $('span.num_comments');
    var num_comments = parseInt(ncspan.text());
    ncspan.text(num_comments + 1);
}

// bind("#commentform","submit",function(event)
//      {
//          event.preventDefault();
//          var comment_text = $(this).children(".comment-textarea").val();
//          var comment_text_length = comment_text.length;
//          if (comment_text_length <= 10000)
//          {
//              $(this).children(".comment-textarea").val("");
//              var content_id = $("#content_id").val();
//              action({
//                  'data': {'action':'comment','c_id': content_id,'comment':comment_text},
//                  'success': function(data) {
//                      ajaxThread();
//                      incNumComments();
//                  },
//                  'error': null
//              });
//          }
//          else
//          {
//              alert("Please limit your response to 10,000 characters.  You have currently typed " + comment_text_length + " characters.");
//          }
//      });

bind("div.comment-actions div.reply-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-reply').toggle();
});

bind("div.comment-actions div.delete-action", "click",function()
{
    var comment = $(this).closest("div.comment");
    var content_id = $(this).data('cid');
    action({
        'data': {'action':'delete','c_id':content_id},
        'success': function(data) {
            comment.html("Comment deleted.");
        }
    });
});

bind("div.comment-actions div.append-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-append').toggle();
});


// bind("input.tab-button.alt","click",function()
//      {
//          $(this).parent().hide();
//      });


// bind(".commentlike","click",function(event)
//      {
//          event.preventDefault();
//          var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//          $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
//              function(data)
//              {
//                  ajaxThread();
//              });
//      });

// bind('commentdislike', 'click', function(event)
//      {
//          event.preventDefault();
//          var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//          $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
//              function(data)
//              {
//                  ajaxThread();
//              });
//      });



// // Collapse a thread (a comment and all its children)
// bind('span.collapse','click',function(e) {
//          var close = '[-]';
//          var open = '[+]';
//          if($(this).text()==close) {
//              $(this).text(open);
//              $(this).next('div.threaddiv').children().hide();
//          } else if($(this).text()==open) {
//              $(this).text(close);
//              $(this).next('div.threaddiv').children().show();
//          }
//      });

// Flag a comment
// bind('span.flag',"click", function(e) {
//          var commentid = $(this).data('commentid');
//          var comment = $(this).parent().children('div.comment-text').text();
//          var conf = confirm("Are you sure you want to flag this comment?\n\n"+comment);
//          if(conf) {
//              action({
//                  data: {'action': 'flag', 'c_id': commentid},
//                  success: function(data) {
//                      alert(data);
//                      $(this).css("color", "red");
//                  },
//                  error: function(data) {
//                      alert("Flagging comment failed.");
//                  }
//              });
//          }
//      });

bind('div.load-more-comments', 'click', function(e) {
    var num_to_load = 1;
    var thread = $(this).siblings('div.thread');
    if(thread.length) {
        var cid = thread.data('cid');
        var next_start = thread.data('num-showing');
        action({
            data: {'action': 'ajaxThread', 'c_id': cid, 'limit': num_to_load, 'start': next_start},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                $(returned.html).hide().appendTo('div.thread').fadeIn(500);
                $('div.thread').data('num-showing', next_start + returned.top_count);
            }
        });
    }
});


/***********************************************************************************************************************
 *
 *      ~InlineEdits
 *
 ***********************************************************************************************************************/
function editUserProfile(info,being_edited, not_editing_display)
{
    var prof_data = info;
    prof_data.action = 'editProfile';

    action({
        'data': prof_data,
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            being_edited.text(obj.value);
            not_editing_display.show();
        }
    });
}


function editContent( c_id , info , being_edited, not_editing_display )
{
    var content_data = info;
    content_data.action = 'editContent';
    content_data.c_id = c_id;

    action({
        'data': content_data,

        success: function(data)
        {
            var obj = eval('(' + data + ')');
            being_edited.html(obj.value);
            not_editing_display.show();
        }
    });
}

function editExplanation(r_id, q_id, explanation, being_edited, not_editing_display) {
    if (explanation == 'I think..') {
        explanation = "";
    }
    action({
        'data': {'action':'editExplanation', 'q_id':q_id, 'r_id':r_id, 'explanation':explanation},
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            being_edited.html('"' + obj.explanation + '"');
            not_editing_display.show();
        }
    });
}


function editPetitionFullText(p_id, full_text, being_edited, not_editing_display )
{
    action({
        'data': {'action':'editPetitionFullText', 'p_id':p_id, 'full_text':full_text},

        success: function(data)
        {
            var obj = eval('(' + data + ')');
            being_edited.html(obj.value);
            not_editing_display.show();
        }
    });
}

bind( ".edit_button" , 'click', null , function(event)
{
    var wrapper = $(this).parents(".inline_editable");
    var not_editing_display = wrapper.find(".not_editing_display");
    var doing_editing_display = wrapper.find(".doing_editing_display");
    not_editing_display.hide();
    doing_editing_display.show();
});

bind( ".cancel_inline_edit" , 'click' , null , function(event)
{
    var wrapper = $(this).parents(".inline_editable");
    var not_editing_display = wrapper.find(".not_editing_display");
    var doing_editing_display = wrapper.find(".doing_editing_display");
    doing_editing_display.hide();
    not_editing_display.show();
});

bind( ".submit_inline_edit" , 'click' , null , function(event)
{
    /* fucking wrapper */
    var wrapper = $(this).parents(".inline_editable");

    /* values of what is being edited */
    var input = wrapper.find('.edit_input');
    var name = input.attr('name');
    var value = input.val();
    var model = wrapper.data('model');
    var info = {
        'key':name,
        'val':value
    };

    /* what visually should be shown while editing or not editing */
    var being_edited = wrapper.find('.being_edited');
    var not_editing_display = wrapper.find(".not_editing_display");
    var doing_editing_display = wrapper.find(".doing_editing_display");
    doing_editing_display.hide();

    /* which edit are we calling */
    if( model == "Content" )
    {
        var c_id = wrapper.data('id');
        editContent(c_id,info,being_edited, not_editing_display);
    }
    else if( model == "UserProfile")
    {
        editUserProfile(info,being_edited, not_editing_display);
    }
    else if( model == "Explanation")
    {
        var r_id = wrapper.data("r_id");
        var q_id = wrapper.data('q_id');
        var explanation = value;
        editExplanation(r_id, q_id, explanation, being_edited, not_editing_display);
    }
    else if (model == "Petition")
    {
        var p_id = wrapper.data("p_id");
        var full_text = value;
        editPetitionFullText(p_id, full_text, being_edited, not_editing_display);
    }

    $(this).parent().siblings('.edit_button').show();
    $(this).parent().hide();
});

/***********************************************************************************************************************
 *
 *      ~login
 *
 **********************************************************************************************************************/
var login_state;
function loadLogin() {
    bind(".no_login_link", "click", null, function(e)
    {
        e.preventDefault();
        var target = $(this).data('link');

        $('#modal_browse_anyways_login').bindOnce("click.browse_anyways_modal", function(e)
        {
            e.preventDefault();
            window.location = target;
        });

        $('.no_login_modal').show();
        $('.overdiv').show();
    });

    bind(".no_login_modal_hide", "click", null, function(e)
    {
        $(this).hide();
        $('.no_login_modal').hide();
    });

    bind(".no_login_modal_close", "click", null, function(e)
    {
        $('.overdiv').hide();
        $('.no_login_modal').hide();
    });
}
loadLogin();

bind('.privacy_policy', 'click', null, function(e)
{
    $('._fade').fadeOut(300);
    $('#privacy-div').fadeToggle(300);
});

bind('#why-facebook', 'click', null, function(e)
{
    $('#why-facebook-hover').fadeToggle(300);
    return false;
});

bind('#why-facebook-hover', 'click', null, function(e)
{
    if (event.target.id != "why-facebook-hover") {
        $(this).fadeOut(300);
    }
});

bind("#why-facebook-hover a", 'click', null, function()
{
    $('#why-facebook-hover').fadeOut(300);
});

bind('#create-account', 'click', null, function(event)
{
    event.preventDefault();
    $('#login-div').hide();
    $('#register-div').show();
});

bind('#no-facebook', 'click', null, function()
{
    $('#fb-div').hide();
    $('#login-div').show();
});

bind(".create_account_button", 'click' ,null, function(event) {
    event.preventDefault();
    $("#create-account-div").hide();
    $("#sign-up-div").show();
});

bind(".sign_up_with_email_button", 'click', null, function(event) {
    event.preventDefault();
    $("#sign-up-div").hide();
    $("#register-div").show();
});


bind(".r_register", 'click', null, function(event) {
    var form = $(this).parents(".r_register_form");
    var form_type = form.data("form_type");
    form.find(".register_gif").show();
    var name = form.find(".name_input").val();
    var email = form.find(".email_input").val();
    var email2 = form.find(".email2_input").val();
    var day = form.find(".day_input").val();
    var month = form.find(".month_input").val();
    var year = form.find(".year_input").val();
    var zip = form.find(".zip_input").val();
    var privacy_check = form.find(".privacy_input");
    var privacy = 0;
    if (privacy_check.is(":checked")) {
        privacy = 1;
    }
    var password = '';
    if (form_type == 'email_register') {
        password = form.find(".password_input").val();
    }
    var data = {'action':'newRegister', 'name':name,'email':email,
        'email2':email2,'password':password,'day':day,'month':month,'year':year,
        'zip':zip,'privacy':privacy, 'form_type':form_type};
    action({
        data: data,
        success: function(data)
        {
            form.find(".register_gif").hide();
            var returned = eval('(' + data + ')');
            if (returned.success) {
                window.location.href = "/welcome/";
            }
            else {
                form.replaceWith(returned.html);
            }
        }
    });
});


/***********************************************************************************************************************
 *
 *      ~Profile
 *
 **********************************************************************************************************************/

bind(".message_politician", 'click', null, function(event) {
    var p_id = $(this).data("p_id");
    getModal("message_politician", {'p_id':p_id});
});

bind(".send_message", 'click', null, function(event) {
    var wrapper = $(this).parents(".message_politician_wrapper");
    var p_id = wrapper.data("p_id");
    var message = wrapper.find(".message_textarea").val();
    action({
            data: {
                'action': 'messagePolitician',
                'p_id': p_id,
                'message': message
            },
            success: function(data)
            {
                var old_height = wrapper.height();
                var old_width = wrapper.width();
                wrapper.css({"height":old_height,"width":old_width});
                wrapper.find(".send_a_message").hide();
                wrapper.find(".message_success").fadeIn(100);
                //setTimeout(hideModal(null),1000);
            }
        }
    );
});

/* mouse over text change for some buttons */
bind(".hover_text", 'mouseenter', null, function(event) {
    var hover_text = $(this).data("hover_text");
    $(this).text(hover_text);
});
bind(".hover_text", 'mouseout', null, function(event) {
    var original_text = $(this).data("original_text");
    $(this).text(original_text);
});

/* profile tabs */
bind(".profile_tab", 'click', null, function(event) {
    $(".profile_tab").removeClass("clicked");
    $(this).addClass("clicked");
});

bind(".questions_tab", 'click', null, function(event) {
    $(".profile_focus").hide();
    $(".questions_focus").show();
    var container = $(".posts_focus").find(".feed_main");
    getFeed(container);
});
bind(".posts_tab", 'click', null, function(event) {
    $(".profile_focus").hide();
    $(".posts_focus").show();
    var container = $(".posts_focus").find(".feed_main");
    getFeed(container);
});
bind(".activity_tab", 'click', null, function(event) {
    $(".profile_focus").hide();
    $(".activity_focus").show();
});

bind(".follow_requests_modal" , 'click' , null , function(event)
{
    getModal('follow_requests_modal');
});

bind(".group_invited_modal" , 'click' , null , function(event)
{
    getModal('group_invited_modal');
});


/***********************************************************************************************************************
 *
 *      ~Following, Supporting and other Actions
 *
 ***********************************************************************************************************************/
bind('div.user_follow' , 'click' , null , function(event)
{
    var p_id = $(this).data("p_id");
    userFollow(event,$(this),true,p_id);
});

bind('div.user_unfollow' , 'click' , null , function(event)
{
    var p_id = $(this).data("p_id");
    userFollow(event,$(this),false,p_id);
});

bind('div.user_unrequest' , 'click' , null , function(event)
{
    var p_id = $(this).data("p_id");
    userFollow(event,$(this),false,p_id);
});

/* user follower */
function userFollow(event,div,follow,p_id)
{
    event.preventDefault();
    // If follow is true, request to follow
    // If follow is false, stop following
    var follow_action = 'userFollowRequest';
    if( !follow )
    {
        follow_action = 'userFollowStop';
    }
    action({
            data: {
                'action': follow_action,
                'p_id': p_id
            },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                var response = returned.response;

                if( response == "followed")
                {
                    div.html("following");
                    div.removeClass('user_follow');
                    div.addClass('user_unfollow');
                    div.removeClass('user-follow');
                    div.addClass('user-unfollow');
                }
                else if( response == "requested")
                {
                    div.html("requested");
                    div.removeClass('user_follow');
                    div.addClass('user_unrequest');
                    div.removeClass('user-follow');
                    div.addClass('user-unfollow');
                }
                else if( response == "removed")
                {
                    div.html("follow");
                    div.removeClass('user_unfollow');
                    div.removeClass('user_unrequest');
                    div.addClass('user_follow');
                    div.removeClass('user-unfollow');
                    div.addClass('user-follow');
                }
                updateStats();
            }
        }
    );
}

bind('div.support_politician' , 'click' , null , function(event)
{
    var p_id = $(this).data("p_id");
    supportPolitician($(this),true,p_id);
});

bind('div.unsupport_politician' , 'click' , null , function(event)
{
    var p_id = $(this).data("p_id");
    supportPolitician($(this),false,p_id);
});

/* user follower */
function supportPolitician(div,support,p_id)
{
    // If support is true, start supporting
    // If support is false, stop supporting
    action({
            data: {
                'action': 'supportPolitician',
                'support': support,
                'p_id': p_id
            },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                div.replaceWith(returned.html);
                updateStats();
            }
        }
    );
}


bind( 'div.group_join' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    groupJoin(event,$(this),true,g_id);
});

bind( 'div.group_leave' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    groupJoin(event,$(this),false,g_id);
});

function groupJoin(event,div,follow,g_id)
{
    event.preventDefault();
    // If follow is true, this is a join request
    // Otherwise they are leaving the group
    var follow_action = 'joinGroupRequest';
    if( !follow )
    {
        follow_action = 'leaveGroup';
    }
    action(
        {
            data:
            {
                'action': follow_action,
                'g_id': g_id
            },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (follow) {
                    var follow_button = div.siblings(".group_follow_button");
                    followGroup(follow_button, follow, g_id);
                }
                div.replaceWith(returned.html);
            }
        });
}

bind(".follow_response_y" , 'click' , function(event)
{
    var wrapper = $(this).parent(".follow_response_buttons");
    wrapper.fadeOut(600);
    userFollowResponse(event,"Y",wrapper);
    wrapper.siblings(".follow_response_text").children('.follow_response_append_y').fadeIn(600);
});

bind(".follow_response_n" , 'click' , function(event)
{
    var wrapper = $(this).parent(".follow_response_buttons");
    wrapper.fadeOut(600);
    userFollowResponse(event,"N",wrapper);
    wrapper.siblings(".follow_response_text").children('.follow_response_append_n').fadeIn(600);
});

function userFollowResponse(event,response,div)
{
    event.preventDefault();
    var follow_id = div.data("follow_id");
    action({
            data: {
                'action':'userFollowResponse',
                'p_id': follow_id,
                'response': response
            },
            success: function(data)
            {

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
        }
    });
}

bind( ".group_response_y" , 'click' , null , function(event)
{
    var wrapper = $(this).parent(".group_request_buttons");
    wrapper.fadeOut(600);
    groupJoinResponse(event,"Y",wrapper);
    wrapper.siblings(".group_request_text").children('.group_request_append_y').fadeIn(600);
});

bind( ".group_response_n" , 'click' , null , function(event)
{
    var wrapper = $(this).parent(".group_request_buttons");
    wrapper.fadeOut(600);
    groupJoinResponse(event,"N",wrapper);
    wrapper.siblings(".group_request_text").children('.group_request_append_n').fadeIn(600);
});

function groupJoinResponse(event,response,div)
{
    event.preventDefault();
    var follow_id = div.data("follow_id");
    var g_id = div.data("g_id");
    action({
            data: {
                'action':'joinGroupResponse',
                'follow_id': follow_id,
                'g_id': g_id,
                'response': response
            },
            success: function(data)
            {

            }
        }
    );
}


/* follow group */
bind('.group_follow' , 'click' , null , function(event)
{
    var g_id = $(this).data("g_id");
    followGroup($(this),true,g_id);
});

bind('.group_unfollow' , 'click' , null , function(event)
{
    var g_id = $(this).data("g_id");
    followGroup($(this),false,g_id);
});


/* follow group */
function followGroup(div,follow,g_id)
{
    // If follow is true, start following
    // If follow is false, stop following
    action({
            data: {
                'action': 'followGroup',
                'follow': follow,
                'g_id': g_id
            },
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (div.length!=0) {
                    div.replaceWith(returned.html);
                }
                if (!follow) {
                    var navlink = getNavLink(returned.href);
                    if (navlink) {
                        navlink.remove();
                    }
                }
                else {
                    var navlink_html = returned.navlink_html;
                    $(".groups_wrapper").prepend(navlink_html);
                }
            }
        }
    );
}

/***********************************************************************************************************************
 *
 *     ~Group Invites
 *
 **********************************************************************************************************************/
bind( '#group_invite_submit' , 'click' , null , function(e)
{
    e.preventDefault();
    var g_id = $(this).data('g_id');
    var invitees = $('.invite_select').select2("val");
    if (invitees!='') {
        action({
            data: {'action': 'groupInvite', 'invitees': JSON.stringify(invitees), 'g_id':g_id},
            success: function(data)
            {
                $('#invite_submit_message').html('Invite Sent!');
                $('#invite_submit_message').fadeIn(200);
                window.setTimeout("$('div.overdiv').fadeOut(600); $('div.modal-general').fadeOut(600);",1000);
            }
        });
    }
});

bind(".invite_response_y" , 'click' , null , function(event) {
    var wrapper = $(this).parent(".invite_response_buttons");
    wrapper.fadeOut(600);
    groupInviteResponse(event,"Y",wrapper);
    wrapper.siblings(".invite_response_text").children('.invite_response_append_y').fadeIn(600);
});

bind(".invite_response_n" , 'click' , null , function(event) {
    var wrapper = $(this).parent(".invite_response_buttons");
    wrapper.fadeOut(600);
    groupInviteResponse(event,"N",wrapper);
    wrapper.siblings(".invite_response_text").children('.invite_response_append_n').fadeIn(600);
});

function groupInviteResponse(event,response,div)
{
    event.preventDefault();
    var g_id = div.data("g_id");
    action({
            data: {
                'action':'groupInviteResponse',
                'g_id': g_id,
                'response': response
            },
            success: function(data)
            {

            }
        }
    );
}

/***********************************************************************************************************************
 *
 *     ~Modal General
 *
 **********************************************************************************************************************/
function hideModal(event) {
    $('div.modal-general').hide();
    $('div.modal_overdiv').hide();
}

function showModal() {
    var modal_general = $('div.modal_general');
    var height = modal_general.height();
    modal_general.css("margin-top", (-1/2*height)-50);
    modal_general.fadeIn(500).css('display', 'inline-block');
    $('div.modal_overdiv').fadeIn(500);
}

// Bind clicks outside modal to closing the modal
bind( 'div.modal-wrapper', 'click', hideModal);
bind( 'div.modal_overdiv', 'click', hideModal);
bind( '.modal_close', 'click', hideModal);
// Don't propogate modal clicks to modal-wrapper (which would close modal)
bind( 'div.modal-general', 'click', function(e) {e.stopPropagation();});

function getModal(modal_name,data)
{
    if( typeof(data)=='undefined'){ data = { 'modal_name':modal_name }; }
    else{ data['modal_name'] = modal_name; }
    data['action'] = 'getModal';
    var modal_general = $('div.modal_general');

    // If create modal has recently been opened, use version in memory to avoid data loss
    if(modal_name=="create_modal" && modal_name==modal_general.data('last-loaded')) {
        showModal();
        return;
    }

    action({
        data: data,
        success: function(response_data)
        {
            var returned = eval('(' + response_data + ')');
            $('div.modal_content').html( returned.modal_html );
            modal_general.data('last-loaded',modal_name);

            showModal();
            bindOnNewElements();
        }
    });
}

/***********************************************************************************************************************
 *
 *      ~Random modals that get things you need
 *
 ***********************************************************************************************************************/
bind('.group_description_modal' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    getModal('group_description' , { 'g_id': g_id });
});


/***********************************************************************************************************************
 *
 *     ~Group Header
 *
 **********************************************************************************************************************/
bind( 'div.group_invite_members' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    getModal( 'group_invite_modal' , { 'g_id': g_id } );
});

bind( 'div.view_group_requests' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    getModal( 'group_requests_modal' , { 'g_id': g_id } );
});


/***********************************************************************************************************************
 *
 *     ~Notifications
 *
 **********************************************************************************************************************/

bind( 'div.notifications_dropdown_button' , 'click' , null , function(event)
{
    var dropdown = $('div.notifications_dropdown');
    dropdown.toggle();
    if( dropdown.is(":visible") )
    {
        dropdown.empty();
        var loading = $('div.notifications_dropdown_loading');
        dropdown.hide();
        loading.show();

        action({
            'data': {'action':'getNotifications',
                'dropdown':'true'},
            success: function(data)
            {
                var obj = eval('(' + data + ')');
                dropdown.html(obj.html);
                $(".notifications_dropdown_button").text(obj.num_still_new);
                loading.hide();
                dropdown.show();
            }
        });
    }
});

function bindNotificationsDropdownClickOutside()
{
    $('.notifications_dropdown').bindOnce( 'clickoutside.notifications_dropdown' , function(event)
    {
        if( !$(this).hasClass('notifications_dropdown_button') )
        {
            $('div.notifications_dropdown').hide();
        }
    });
}

bind( ".notification_user_follow" , 'click' , null , function(event)
{
    event.preventDefault();
    var follow_id = $(this).data('follow_id');
    var wrapper = $(this).parent(".notification_buttons");
    wrapper.fadeOut(600);
    action({
        data: {
            'action': 'userFollowRequest',
            'p_id': follow_id
        },
        success: function(data)
        {
            var returned = eval('(' + data + ')');
            var response = returned.response;

            if( response == "followed")
            {
                wrapper.siblings(".notification_text").children('.notification_append').text('You have followed them back');
            }
            else if( response == "requested")
            {
                wrapper.siblings(".notification_text").children('.notification_append').text('You have requested to follow them');
            }
            wrapper.siblings(".notification_text").children('.notification_append').fadeIn(600);
        }
    });
});



/***********************************************************************************************************************
 *
 *      ~GroupEdit
 *
 **********************************************************************************************************************/
function loadGroupEdit()
{
    selectPrivacyRadio();
    selectScaleRadio();

    $('select.admin_select').select2({
        placeholder: "Enter a member,"
    });

    $('select.member_select').select2({
        placeholder: "Enter a member,"
    });
}

function selectPrivacyRadio()
{
    var privacy = $('#group_privacy_container').data('group_privacy');
    var selected = $('input:radio[value="'+privacy+'"][name="group_privacy"]');
    selected.prop('checked',true);
    selected.parent().addClass('create-radio-selected');
}

function selectScaleRadio()
{
    var scale = $('#group_scale_container').data('group_scale');
    var selected = $('input:radio[value="'+scale+'"][name="scale"]');
    selected.prop('checked',true);
    selected.parent().addClass('create-radio-selected');
}

// Group Privacy Radio
bind( "div.group_privacy_radio" , 'click' , null , function(event)
{
    var prev = $("input:radio[name=group_privacy]:checked");
    prev.attr('checked',false);
    prev.parent('.group_privacy_radio').removeClass("create-radio-selected");

    $(this).children("input:radio[name=group_privacy]").attr('checked',true);
    $(this).addClass("create-radio-selected");
});

// Group Scale Radio
bind( "div.news_scale_radio" , 'click' , null , function(event)
{
    var prev = $("input:radio.news_scale:checked");
    prev.attr('checked',false);
    prev.parent('.news_scale_radio').removeClass("create-radio-selected");

    $(this).children("input:radio.news_scale").attr('checked',true);
    $(this).addClass("create-radio-selected");
});

// Mouseover Pencil for group edit
bind( '.group_edit_input' , 'mouseenter' , null , function(event)
{
    $(this).parent().next().children('.group_edit_icon').show();
});
bind( '.group_edit_input' , 'mouseout' , null , function(event)
{
    $(this).parent().next().children('.group_edit_icon').hide();
});

bind( '.append_pointer' , "click" , null , function(event)
{
    var pointer = $('.group_edit_pointer');
    $('.append_pointer').removeClass("account-button-selected");
    $(this).addClass("account-button-selected");
    $(this).prepend(pointer);
});

bind('.group_edit_button' , "click" , null , function(event)
{
    $(".group_edit_tab").hide();
    var div_class = $(this).data('div');
    $("." + div_class).show();
});

bind('#edit_admin_submit' , 'click' , null , function(e)
{
    e.preventDefault();
    var g_id = $("#edit_admin_submit").data('g_id');
    var new_admins = $('.admin_select').select2("val");

    if (new_admins!='') {
        action({
            data: {'action': 'addAdmins', 'admins': JSON.stringify(new_admins), 'g_id':g_id},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                $('#edit_admin_submit_message').html('Administrator Added');
                $('#edit_admin_submit_message').show();
                $('#edit_admin_submit_message').fadeOut(3000);
                $('#admin_remove_container').hide();
                $('#admin_remove_container').html(returned.html);
                $('#admin_remove_container').fadeIn(600);
                bindRemoveAdmin();
            }
        });
    }
});

bind('#members_remove_submit' , 'click' , null , function(e)
{
    e.preventDefault();
    var g_id = $(this).data('g_id');
    var members = $('.member_select').select2("val");

    if (members!='') {
        action({
            data: {'action': 'removeMembers', 'members': JSON.stringify(members), 'g_id':g_id},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                var return_message = $('#members_remove_submit_message');
                return_message.html('Members Removed');
                return_message.show();
                return_message.fadeOut(3000);
                var members_container = $(".group_members_container");
                members_container.hide();
                members_container.html(returned.html);
                members_container.fadeIn(600);
            }
        });
    }
});

bind('.remove_admin' , 'click', null , function(e)
{
    var admin_id = $(this).data('admin_id');
    var admin_name = $(this).data('admin_name');
    var g_id = $('#edit_admin_submit').data('g_id');
    $(this).parents('div.admin_container').fadeOut(600);
    removeAdmin( admin_id , g_id , function(data)
    {
        $('optgroup#add_members_input').append('<option value="' + admin_id + '">' + admin_name + '</option>');
    });
});

bind('.remove_admin_self' , 'click' , null , function(e)
{
    var admin_id = $(this).data('admin_id');
    var admin_name = $(this).data('admin_name');
    var g_id = $('#edit_admin_submit').data('g_id');
    var g_alias = $('#edit_admin_submit').data('g_alias');
    $(this).parents('div.admin_container').fadeOut(600);
    removeAdmin( admin_id , g_id , function(data)
    {
        window.location = '/' + g_alias + '/';
    });
});

function removeAdmin(admin_id,g_id,success)
{
    action({
        data:
        {
            'action': 'removeAdmin',
            'admin_id': admin_id,
            'g_id': g_id
        },
        success: success
    });
}


/***********************************************************************************************************************
 *
 *     ~Hover Comparison
 *
 **********************************************************************************************************************/
function loadHoverComparison()
{

    var hoverTimer;
    var hoverClearOK = true;

    function clearHover()
    {
        if( hoverClearOK )
        {
            $('#comparison-hover-div p').empty();
            $('#comparison-hover').empty();
            $('#comparison-hover-div').fadeOut(300);
        }
    }

    $('#comparison-hover-div').hover
        (
            function() { hoverClearOK = false; },
            function()
            {
                hoverClearOK = true;
                hoverTimer = setTimeout
                    (
                        function() { clearHover(); },
                        300
                    );
            }
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
                    var title_html = 'You &  <a href="' + href+ '">' + displayName + '</a>';
                    $('#comparison-hover-div p.hover-title').html(title_html);
                    var offset = findHoverPosition(self);
                    $('#comparison-hover-loading-img').show();
                    $('#comparison-hover-div').fadeIn(100);
                    $('#comparison-hover-div').offset(offset);
                    action({
                        'data': {'action':'hoverWebComparison','href':href},
                        'success': function(data)
                        {
                            var obj = eval('(' + data + ')');
                            $('#comparison-hover-loading-img').hide();
                            $('#comparison-hover').visualComparison(obj,true);
                        },
                        'error': null
                    });
                }
            },
            function(event)
            {
                hoverTimer = setTimeout
                    (
                        function(){ clearHover(); },
                        1000
                    );
            }
        );
}

/* deprecated
 function loadHoverBreakdown()
 {

 var hoverTimer;
 var hoverClearOK = true;

 function clearHover()
 {
 if( hoverClearOK )
 {
 $('#comparison-hover-div p').empty();
 $('#comparison-hover').empty();
 $('#comparison-hover-div').fadeOut(300);
 }
 }

 $('#comparison-hover-div').hover
 (
 function() { hoverClearOK = false; },
 function()
 {
 hoverClearOK = true;
 hoverTimer = setTimeout
 (
 function() { clearHover(); },
 300
 );
 }
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
 $('#comparison-hover-div p').text('You & ' + displayName);
 var offset = findHoverPosition(self);
 $('#comparison-hover-loading-img').show();
 $('#comparison-hover-div').fadeIn(100);
 $('#comparison-hover-div').offset(offset);
 action({
 'data': {'action':'hoverComparison','href':href},
 'success': function(data)
 {
 var obj = eval('(' + data + ')');
 $('#comparison-hover-loading-img').hide();
 $('#comparison-hover').html(obj.html);
 },
 'error': null
 });
 }
 },
 function(event)
 {
 hoverTimer = setTimeout
 (
 function(){ clearHover(); },
 1000
 );
 }
 );
 }
 */

/***********************************************************************************************************************
 *
 *     ~ q&a interface
 *
 **********************************************************************************************************************/
bind('.answer_button' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    expandChooseInterface(stub);
});

bind('.hide_button' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    hideStub(stub);
});

function hideStub(stub) {
    stub.find(".question_expanded").hide();
    stub.find(".hide_button").hide();
    stub.find(".answer_button").show();
}

function expandChooseInterface(stub) {
    stub.find(".question_expanded").hide();
    stub.find(".question_expanded_choose").show();
    stub.find(".answer_button").hide();
    stub.find(".hide_button").show();
}

function expandResponses(stub, animate) {
    var old_height = stub.height();
    stub.find(".question_expanded").hide();
    stub.find(".question_expanded_responses").show();
    var new_height = stub.height();
    if (animate) {
        stub.css('height', old_height);
        stub.animate({"height":new_height}, {"duration":500, "complete":function(){stub.css("height", "auto");}});
    }
}

/* sets question stubs to display appropriately */
function updateQuestionStubsDisplay() {
    $.each($(".question_stub"), function(i,e) {
        updateQuestionStubDisplay($(this), false);
    });
}

/* set initial display for all stubs */
function updateQuestionStubDisplay(stub, animate, display) {
    if (typeof(display) == 'undefined') {
        display = stub.data("default_display");
    }
    if (display == 'none') {
        hideStub(stub);
    }
    if (display == 'choose') {
        expandChooseInterface(stub);
    }
    if (display == 'responses') {
        var your_response = stub.data("your_response");
        if (your_response == 1) {
            expandResponses(stub, animate);
        }
        else {
            hideStub(stub);
        }
    }
}

bind('.answer_choice' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    if ($(this).hasClass("clicked")) {
        $(this).removeClass("clicked");
    }
    else {
        stub.find(".answer_choice").removeClass("clicked");
        $(this).addClass("clicked");
    }
    saveAnswer(stub);
});


bind('.change_answer_privacy' , 'click' , null , function(event)
{
    var wrapper = $(this).parents(".answer_privacy_wrapper");
    var stub = $(this).parents(".question_stub");
    var r_id = $(this).data("r_id");
    var q_id = $(this).data("q_id");
    action({
        data: {'action':'changeAnswerPrivacy', 'r_id':r_id, 'q_id':q_id},
        success: function(data) {
            var returned = eval('(' + data + ')');
            wrapper.replaceWith(returned.html);
            stub.data("privacy", returned.privacy);
        }
    });
});

// stage 1, save answer
function saveAnswer(stub) {
    var box = stub.find(".answer_choice.clicked");
    var a_id;
    if (box.length!=0) {
        a_id = box.data('a_id');
    }
    else {
        a_id = -1;
    }
    var q_id = stub.data('q_id');
    var default_display = stub.data("default_display");
    var your_response = stub.data("your_response");
    var privacy = stub.data("privacy");
    var importance = stub.find('.importance_bar').data('weight');

    var data = {'action':'saveAnswer', 'q_id':q_id,
        'a_id':a_id, 'default_display':default_display,
        'weight':importance, 'privacy':privacy};

    var container = stub.parents(".feed_main");
    if (container.length!=0) {
        var to_compare_id = container.data("to_compare_id");
        if (typeof(to_compare_id) != 'undefined') {
            data['to_compare_id'] = to_compare_id;
        }
        var scorecard_id = container.data("scorecard_id");
        if (scorecard_id) {
            data['scorecard_id'] = scorecard_id;
        }
        // check if should be scorecard edit answer
        var save_scorecard_answer = container.data("save_scorecard_answer");
        if (save_scorecard_answer == 1) {
            data['action'] = 'saveScorecardAnswer'
        }
        // if only unanswered animate hide question
        var only_unanswered = container.data('only_unanswered');
        if (only_unanswered) {
            stub.animate({"height":"0px"}, {"duration": 300, "complete":function(){stub.hide()}});
            expandChooseInterface(stub.next('.question_stub'));
        }
    }
    action({
        data: data,
        success: function(data) {
            var returned = eval('(' + data + ')');
            if (default_display=='responses') {
                var new_element = $(returned.html);
                var old_height = stub.height();
                stub.replaceWith(new_element);
                stub = new_element;
                new_element.find(".question_expanded_responses").show();
                var new_height = new_element.height();
                new_element.css('height', old_height);
                new_element.animate({"height":new_height}, {"duration":200, "complete":function(){new_element.css("height", "auto");}});
                bindOnNewElements();
            }
            var saved_message = stub.find(".saved_message");
            saved_message.show();
            saved_message.fadeOut(5000);
            updateMatches();
            updateStats();
        }
    });
}

// answer in feed
bind('.poll_answer' , 'click' , null , function(event)
{
    var item = $(this).parents(".sample_question");
    if ($(this).hasClass("clicked")) {
        $(this).removeClass("clicked");
    }
    else {
        item.find(".poll_answer").removeClass("clicked");
        $(this).addClass("clicked");
    }
    saveAnswerInFeed(item);
});


function saveAnswerInFeed(item) {
    var choice = item.find(".poll_answer.clicked");
    var a_id;
    if (choice.length!=0) {
        a_id = choice.data('a_id');
    }
    else {
        a_id = -1;
    }
    var q_id = item.data('q_id');
    var data = {'action':'saveAnswerInFeed', 'q_id':q_id,
        'a_id':a_id};
    action({
        data: data,
        success: function(data) {
            var saved_message = item.find(".saved_message");
            saved_message.show();
            //setTimeout(function(){saved_message.fadeOut()},1000);
        }
    });
}


bind('.see_their_response' , 'click' , null , function(event)
{
    expandResponses($(this).parents(".question_stub"));
});


/* importance sliders */
function bindImportanceSliders() {
    var importance_bars = $(".importance_bar");
    $.each(importance_bars, function(i, e) {
        bindImportanceSlider($(this));
    });
}

function bindImportanceSlider(div) {
    var stub = div.parents(".question_stub");
    var weight = div.data('weight');
    div.slider({'min':0,
        'max':100,
        'step':1,
        'value':weight,
        slide: function(event, ui) {
            div.data('weight', ui.value);
            var text = ui.value + "%";
            $(this).parents(".importance_wrapper").find(".importance_percent").text(text);
        },
        stop: function(event, ui) {
            saveAnswer(stub);
        }
    });
}




/***********************************************************************************************************************
 *
 *     ~ q&a feed
 *
 **********************************************************************************************************************/
bind('.only_unanswered' , 'click' , null , function(event)
{
    $(this).toggleClass("clicked");
    var container = $(this).parents(".feed_main");
    container.data("only_unanswered", $(this).hasClass("clicked"));
    refreshFeed(container);
});

/***********************************************************************************************************************
 *
 *     ~ homemade backbone.... dom elements which update themselves
 *
 **********************************************************************************************************************/
function updateMatches() {
    $.each($(".match_object"), function(i, e) {
        updateMatch($(this));
    });
}

function updateMatch(match) {
    var display = match.data('display');
    var to_compare_alias = match.data('to_compare_alias');
    action({
        data: {'action':'updateMatch', 'to_compare_alias':to_compare_alias, 'display':display},
        success: function(data) {
            var returned = eval('(' + data + ')');
            var new_element = $(returned.html);
            match.replaceWith(new_element);
            if (display=='comparison_web') {
                new_element.visualComparison();
            }
        }
    });
}

function updateStats() {
    $.each($(".stats_object"), function(i,e) {
        updateStatsObject($(this));
    });
}

function updateStatsObject(stats) {
    var object = stats.data('object');
    var data = {'action':'updateStats', 'object':object};
    if (object == 'you_agree_with') {
        data['q_id'] = stats.data('q_id');
    }
    if (object == 'poll_progress') {
        data['p_id'] = stats.data('p_id');
    }
    if (object == 'petition_bar') {
        data['p_id'] = stats.data('p_id');
    }
    if (object == 'profile_stats') {
        data['p_id'] = stats.data('p_id');
    }
    if (object == 'election_leaderboard') {
        data['e_id'] = stats.data('e_id');
    }
    action({
        data: data,
        success: function(data) {
            var returned = eval('(' + data + ')');
            var new_element = $(returned.html);
            stats.replaceWith(new_element);
        }
    });
}

/***********************************************************************************************************************
 *
 *     ~Histogram
 *
 **********************************************************************************************************************/

/* helpers for keeping state of histogram */
function saveHistogramMetadata(histogram_wrapper, histogram_metadata) {
    histogram_wrapper.data('metadata', histogram_metadata);
}
function loadHistogramMetadata(histogram_wrapper) {
    return histogram_wrapper.data('metadata');
}

/* bind click functions */
bind(".histogram-select-block", 'click', null, function(event) {
    var histogram_wrapper = $(this).parents(".histogram_wrapper");
    var block = $(this).siblings(".block-val").val();
    var was = $("#histogram-block").val();
    if (block == was) {
        $("#histogram-block").val(-1);
    }
    else {
        $("#histogram-block").val(block);
    }
    loadMoreHistogramUsers(event, true);
});

bind(".h-topic-img", 'click', null, function(event) {
    var histogram_wrapper = $(this).parents(".histogram_wrapper");
    var wrapper = $(this).parents(".topic-icon-wrapper");
    selectTopicSingle(wrapper);
    var topic = $(this).siblings(".t-alias").val();
    var was = histogram_wrapper.find(".histogram-topic").val();
    if (topic == was) {
        was.val('general');
    }
    else {
        was.val(topic);
    }
    refreshHistogram(histogram_wrapper);
});


/* get histograms going */
function loadHistograms() {
    $.each($(".histogram_wrapper"), function(i,e) {
        loadHistogram($(this));
    });
}

function loadHistogram(histogram_wrapper) {

    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    histogram_metadata.members_displayed = 0;
    histogram_metadata.identical_displayed = 0;
    saveHistogramMetadata(histogram_wrapper, histogram_metadata);
    updateHistogram(histogram_wrapper, true);

    histogram_wrapper.find('.update_histogram').bindOnce("click.histogram", function(event) {
        event.preventDefault();
        updateHistogram(histogram_wrapper, false);
    });

    histogram_wrapper.find(".histogram_topic_img").bindOnce("click.histogram", function(event) {
        var wrapper = $(this).parents(".topic_icon_wrapper");
        var alias;
        var topic_text;
        if (wrapper.hasClass("chosen")) {
            alias = 'all';
            topic_text = "All Topics"
        }
        else {
            alias = wrapper.data('t_alias');
            topic_text = wrapper.data('t_text');
        }
        histogram_wrapper.find(".histogram-topic").text(topic_text);
        histogram_metadata.topic_alias = alias;
        saveHistogramMetadata(histogram_wrapper, histogram_metadata);
        toggleTopicSingle(wrapper);
        refreshHistogram(histogram_wrapper);
    });

    histogram_wrapper.find(".bar_label").bindOnce("click.histogram", function(event) {
        var bar = $(this).parents(".bar");
        selectHistogramBar(histogram_wrapper, bar);
    });
    histogram_wrapper.find(".red_bar").bindOnce("click.histogram", function(event) {
        var bar = $(this).parents(".bar");
        selectHistogramBar(histogram_wrapper, bar);
    });

    histogram_wrapper.find(".get_more_members").bindOnce("click.histogram", function(event) {
        event.preventDefault();
        getHistogramMembers(histogram_wrapper);
    });
}

function selectHistogramBar(histogram_wrapper, bar) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    if (bar.hasClass("clicked")) {
        histogram_metadata.current_bucket = -1;
        saveHistogramMetadata(histogram_wrapper, histogram_metadata);
        bar.removeClass("clicked");
    }
    else {
        histogram_wrapper.find(".bar").removeClass("clicked");
        histogram_metadata.current_bucket = bar.data('bucket');
        saveHistogramMetadata(histogram_wrapper, histogram_metadata);
        bar.addClass("clicked");
    }
    refreshHistogramMembers(histogram_wrapper);
}

function refreshHistogramMembers(histogram_wrapper) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    histogram_metadata.members_displayed = 0;
    saveHistogramMetadata(histogram_wrapper, histogram_metadata);
    getHistogramMembers(histogram_wrapper);
}

function refreshHistogramData(histogram_wrapper, data) {

    var histogram_metadata = histogram_wrapper.data('metadata');

    histogram_metadata.total += data.total;
    histogram_metadata.identical += data.identical;
    histogram_metadata.identical_uids.push.apply(histogram_metadata.identical_uids, data.identical_uids);

    $.map(data.buckets, function(item, key) {

        var bar = histogram_wrapper.find(".bar[data-bucket=" + key + "]");

        bar.children('.red_bar').css("background-color",data.color);
        histogram_wrapper.find('.histogram-footer').css("background-color",data.color);
        histogram_wrapper.find(".histogram-wrapper").css("border-color",data.color);

        var num = bar.data('num') + item.num;
        bar.data('num', num);
        if (num == 1) {
            var mouseover = String(num) + " person.";
        }
        else {
            var mouseover = String(num) + " people.";
        }
        bar.find(".red_bar").attr("data-original-title", mouseover);

        if (histogram_metadata.total != 0) {
            var percent = (num / histogram_metadata.total)*100;
        }
        else {
            var percent = 0;
        }
        bar.data("percent", percent);

        var bucket_uids = histogram_metadata.bucket_uids[parseInt(key)];
        bucket_uids.push.apply(bucket_uids, item.u_ids);
    });
}

function normalizeHistogram(histogram_wrapper) {
    var histogram_max_percent=0;
    // calculate max
    histogram_wrapper.find(".bar").each(function(index, element) {
        var percent = $(this).data("percent");
        if (percent > histogram_max_percent) {
            histogram_max_percent = percent;
        }
    });
    // normalize percents
    if (histogram_max_percent > 0) {
        histogram_wrapper.find(".bar").each(function(index, element) {
            var percent = $(this).data("percent");
            var normalized = percent * (100/histogram_max_percent);
            $(this).data('percent', normalized);
        });
    }
}

function renderHistogram(histogram_wrapper) {
    normalizeHistogram(histogram_wrapper);
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    if (histogram_metadata.which == 'mini') {
        histogram_wrapper.find(".bar").each(function(index, element) {
            var percent = $(this).data("percent");
            var zero_height_percent = 3;
            var height_percent = Math.floor(zero_height_percent + ((100 - zero_height_percent)*(percent/100)));
            var empty_percent = 100 - height_percent;
            $(this).find(".white_bar").css("height", empty_percent + "%");
            $(this).find(".red_bar").css("height", height_percent + "%");
        });
    }

    else {
        histogram_wrapper.find(".bar").each(function(index, element) {
            // width and position
            var total_width = 850;
            var margin_left = 15;
            var margin_space = margin_left * histogram_metadata.resolution;
            var width = (total_width-margin_space) / histogram_metadata.resolution;
            $(this).css("width", width);
            $(this).css("margin-left", margin_left);
            $(this).find(".red_bar").css("width", width);

            // height
            var percent = $(this).data("percent");
            var total_height = 300;
            var zero_height = 5;
            var height = zero_height+((total_height-zero_height)*(percent/100));
            $(this).find(".white_bar").css("height", total_height-height);
            $(this).find(".red_bar").css("height", height);
        });
    }

    histogram_wrapper.find(".histogram_count").text(histogram_metadata.total);
    histogram_wrapper.find(".histogram_identical").text(histogram_metadata.identical);
    histogram_wrapper.show();

}

function refreshHistogram(histogram_wrapper) {

    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);

    histogram_metadata.total = 0;
    saveHistogramMetadata(histogram_wrapper, histogram_metadata);

    histogram_wrapper.find(".bar").data('num', 0);
    $.map(histogram_metadata.bucket_uids, function(item, key) {
        histogram_metadata.bucket_uids[key] = [];
    });
    histogram_metadata.members_displayed = 0;
    histogram_metadata.identical = 0;
    histogram_metadata.identical_uids = [];
    histogram_metadata.identical_displayed = 0;
    saveHistogramMetadata(histogram_wrapper, histogram_metadata);

    updateHistogram(histogram_wrapper, true);
}

function updateHistogram(histogram_wrapper, recursive) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    action({
            data: {
                'action':'updateHistogram',
                'start': histogram_metadata.total,
                'num': histogram_metadata.increment,
                'topic_alias':histogram_metadata.topic_alias,
                'g_id': histogram_metadata.g_id,
                'resolution': histogram_metadata.resolution,
                'log-ignore': true
            },
            success: function(data)
            {
                var returned =  eval('(' + data + ')');
                refreshHistogramData(histogram_wrapper, returned);
                renderHistogram(histogram_wrapper);
                getHistogramMembers(histogram_wrapper);
                getIdenticalMembers(histogram_wrapper);
                if (returned.total != 0 && recursive) {
                    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
                    if (histogram_metadata.maximum == -1 || histogram_metadata.total < histogram_metadata.maximum) {
                        updateHistogram(histogram_wrapper, true);
                    }
                }
            }
        }
    );
}

function getHistogramMembers(histogram_wrapper) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    if (!histogram_metadata.members_lockout) {
        getHistogramMembersHelper(histogram_wrapper, false);
    }
}

function getIdenticalMembers(histogram_wrapper) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    if (!histogram_metadata.identical_lockout) {
        getHistogramMembersHelper(histogram_wrapper, true);
    }
}

/* gets members for display in either identical or histogram place */
function getHistogramMembersHelper(histogram_wrapper, identical) {

    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    var start;
    var u_ids;
    var display;
    if (identical) {
        start = histogram_metadata.identical_displayed;
        display = 'avatar';
        u_ids = histogram_metadata.identical_uids;
    }
    else {
        start = histogram_metadata.members_displayed;
        display = 'strip';
        if (histogram_metadata.current_bucket != -1) {
            u_ids = histogram_metadata.bucket_uids[histogram_metadata.current_bucket];
        }
        else {
            u_ids = null;
        }
    }

    var num = 10;
    var replace = (start==0);
    var post_data;
    // if u_ids then get members by requesting ids
    if (u_ids) {
        if (u_ids.length!=0) {
            if (start <= (u_ids.length-1)) {
                if (identical) {
                    histogram_metadata.identical_lockout = true;
                }
                else {
                    histogram_metadata.members_lockout = true;
                }
                var end = Math.min(u_ids.length, start+num);
                u_ids = u_ids.slice(start, end);
                u_ids = JSON.stringify(u_ids);
                post_data = {'action':'getUsersByUID',
                    'u_ids': u_ids,
                    'display':display,
                    'log-ignore': true};
            }
        }
        else {
            if (replace) {
                if (identical) {
                    histogram_wrapper.find(".identical_wrapper").empty();
                }
                else {
                    histogram_wrapper.find(".members_wrapper").empty();
                }
            }
        }
    }
    // else get members by posting start, end and group_id
    else {
        post_data = {'action':'getGroupMembersForDisplay',
            'g_id':histogram_metadata.g_id,
            'start': start,
            'num': num,
            'display':display,
            'log-ignore': true};
    }
    if (post_data) {
        action({
                data: post_data,
                success: function(data)
                {
                    var returned =  eval('(' + data + ')');
                    appendHistogramMembersHTML(histogram_wrapper, returned.html, returned.num, identical, replace);
                }
            }
        );
    }
}

/* appends html to members wrapper or identical wrapper appropriately, depending on identical=True */
function appendHistogramMembersHTML(histogram_wrapper, html, num, identical, replace) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    if (identical) {
        var $wrapper = histogram_wrapper.find(".identical_wrapper");
        histogram_metadata.identical_displayed += num;
        histogram_metadata.identical_lockout = false;
    }
    else {
        var $wrapper = histogram_wrapper.find(".members_wrapper");
        histogram_metadata.members_displayed += num;
        histogram_metadata.members_lockout = false;
    }
    saveHistogramMetadata(histogram_wrapper, histogram_metadata);
    setHistogramExplanation(histogram_wrapper);
    if (replace) {
        $wrapper.html(html);
    }
    else {
        $wrapper.append(html);
    }
    loadHoverComparison();
}

/* sets histogram explanation text above members wrapper */
function setHistogramExplanation(histogram_wrapper) {
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    var lower = histogram_metadata.current_bucket;
    if (lower != -1) {

        var inc = 100 / histogram_metadata.resolution;
        var higher = lower + inc;
        var message = String(lower) + '-' + String(higher) + "% similar to you";
    }
    else {
        var message = "";
    }
    histogram_wrapper.find(".in_percentile").html(message);
}


function getHistogramGroupMembers(histogram_wrapper) {

    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    var start = histogram_metadata.members_displayed;
    var num = 10;

    var replace = (start== 0);
    histogram_metadata.members_lockout = true;
    saveHistogramMetadata(histogram_wrapper);

    action({
        data: {
            'action':'getHistogramGroupMembers',
            'start':start,
            'num':num,
            'g_id':histogram_metadata.g_id,
            'histogram_topic':histogram_metadata.topic_alias,
            'histogram_block':histogram_metadata.current_bucket,
            'log-ignore': true
        },
        success: function(data)
        {
            var returned =  eval('(' + data + ')');

            var $wrapper = $(".members-avatars");
            histogram_metadata.members_displayed += returned.num;
            histogram_metadata.members_lockout = false;
            saveHistogramMetadata(histogram_wrapper, histogram_metadata);

            if (replace) {
                $wrapper.html(returned.html);
            }
            else {
                $wrapper.append(returned.html);
            }
            loadHoverComparison();
        },
        error: function(error, textStatus, errorThrown)
        {
            $('body').html(error.responseText);
        }
    });
}

/***********************************************************************************************************************
 *
 *     ~Topics
 *
 **********************************************************************************************************************/
bind(".topic-img", 'mouseenter', null, function(event) {
    var wrapper = $(this).parents(".topic-icon-wrapper");
    wrapper.children(".normal").hide();
    wrapper.children(".selected").show();
});
bind(".topic-img", 'mouseout', null, function(event) {
    var wrapper = $(this).parents(".topic-icon-wrapper");
    if (!(wrapper.hasClass("chosen")))
    {
        wrapper.children(".selected").hide();
        wrapper.children(".normal").show();
    }
});

// selects a particular topic icon and deselects all others
function selectTopicSingle(wrapper)
{
    var icons_wrapper = wrapper.closest(".topic-icons-wrapper");
    clearTopicIcons(icons_wrapper);
    showTopicIcon(wrapper);
}

function toggleTopicSingle(wrapper) {
    var deselect = wrapper.hasClass("chosen");
    var icons_wrapper = wrapper.closest(".topic-icons-wrapper");
    clearTopicIcons(icons_wrapper);
    if (!deselect) {
        showTopicIcon(wrapper);
    }
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


/***********************************************************************************************************************
 *
 *      ~Friends and facebook share
 *
 ***********************************************************************************************************************/

bind( '.facebook_share_button' , 'click' , null , function(e)
{
    var data = {
        'fb_name' : $(this).data('fb_name'),
        'fb_share_id' : $(this).data('fb_share_id')
    };

    getModal('facebook_share_modal' , data);
});


bind( '.facebook_share_submit' , 'click' , null , function(e)
{
    e.preventDefault();

    var share_message = $(this).parents('.facebook_share_form').find('textarea[name="facebook_share_message"]').val();
    var fb_share_id = $(this).data('fb_share_id');
    var link = $(this).data('fb_link');

    var url = "/fb/action/?fb_action=share&fb_share_to=" + fb_share_id;
    url += "&message=" + share_message;

    if( link != null ) { url += "&fb_link=" + link; }

    url += "&action_to_page=" + window.location.pathname;

    window.location.href = url

});


/***********************************************************************************************************************
 *
 *      ~pin content
 *
 ***********************************************************************************************************************/

bind( '.pin_content' , 'click' , null , function(e)
{
    var data = { 'c_id' : $(this).data("c_id") };
    getModal('pin_content_modal',data);
});

bind( '.pin_to_group' , 'click' , null , function(e)
{
    var c_id = $(this).data("c_id");
    var g_id = $(this).data("g_id");


    action({
        data: {
            'action':'pinContent',
            'g_id': g_id,
            'c_id': c_id
        },
        success: function(data)
        {
            var returned =  eval('(' + data + ')');
        }
    });
});

bind('.pin_it' , 'click' , null , function(e)
{
    var c_id = $(this).data("c_id");
    var g_id = $(".pin_to_select").val();
    action({
        data: {
            'action':'pinContent',
            'g_id': g_id,
            'c_id': c_id,
            'pin':1
        },
        success: function(data)
        {
            var returned =  eval('(' + data + ')');
            $(".was_pinned").html(returned.html);
            $(".was_pinned").fadeIn(500);
        }
    });
});

bind('.unpin_content' , 'click' , null , function(e)
{
    var c_id = $(this).data("c_id");
    var g_id = $(this).data("g_id");
    var to_remove = $(this).parents(".pinned_wrapper");
    action({
        data: {
            'action':'pinContent',
            'g_id': g_id,
            'c_id': c_id,
            'pin':-1
        },
        success: function(data)
        {
            to_remove.remove();
        }
    });
});

/***********************************************************************************************************************
 *
 *      ~Petition sign
 *
 ***********************************************************************************************************************/
bind('.sign_button' , 'click' , null , function(e)
{
    var p_id = $(this).data('p_id');
    var signers_sidebar = $(this).parents(".signers_sidebar");
    action({
            data: {'action': 'signPetition', 'p_id':p_id},
            success: function(data) {
                var returned = eval('(' + data + ')');
                signers_sidebar.replaceWith(returned.html);
                updateStats();
            }}
    );
});

bind('.finalize_button' , 'click' , null , function(e)
{
    var p_id = $(this).data('p_id');
    var signers_sidebar = $(this).parents(".signers_sidebar");
    action({
            data: {'action': 'finalizePetition', 'p_id':p_id},
            success: function(data) {
                var returned = eval('(' + data + ')');
                signers_sidebar.replaceWith(returned.html);
            }}
    );
});


/***********************************************************************************************************************
 *
 *      ~dismissible header stuff, representatives
 *
 ***********************************************************************************************************************/
bind('.dismissible_x' , 'click' , null , function(e)
{
    $(this).parents(".dismissible_header").hide();
});


var reps_longitude;
var reps_latitude;
var reps_state;
var reps_district;
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
            center: new google.maps.LatLng(reps_latitude, reps_longitude),
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            panControl: false,
            zoomControl: true,
            mapTypeControl: false,
            scaleControl: true,
            streetViewControl: false
        };
        map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

        overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(false, .2, reps_state, reps_district));
        map.overlayMapTypes.insertAt(0, overlayWMS);

        overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(true, .7, reps_state, reps_district));
        map.overlayMapTypes.insertAt(0, overlayWMS);
    }

    if (rebind=="representatives" && reps_latitude && reps_longitude && reps_state && reps_district) {
        initialize();
    }
}


/* find address */
bind('.find_address_button' , 'click' , null , function(e)
{
    var form = $(this).parents(".address_form");
    var address = form.find(".street_input").val();
    var state = form.find(".state_input").val();
    var zip = form.find(".zip_input").val();
    var city = form.find(".city_input").val();
    var error_message = $(this).parents(".find_your_reps").find(".error_message");
    error_message.hide();
    action({
            data: {'action': 'submitTempAddress', 'address': address, 'city':city, 'state':state,
                'zip':zip},
            success: function(data) {
                var returned = eval('(' + data + ')');
                if (returned.success == -1) {
                    error_message.fadeIn();
                }
                else {
                    location.reload();
                }
            }}
    );
});

bind('.enter_new_address' , 'click' , null , function(e) {
    $(".dismissible_header").show();
});


/***********************************************************************************************************************
 *
 *      ~claim your profile
 *
 ***********************************************************************************************************************/
bind('.claim_profile_button' , 'click' , null , function(e)
{
    var p_id = $(this).data('p_id');
    var email = $(".claim_profile_email").val();
    action({
            data: {'action': 'claimProfile', 'p_id':p_id, 'email':email},
            success: function(data) {
                $(".claimed_message").fadeIn();
            }}
    );
});


bind('.ask_to_join' , 'click' , null , function(e)
{
    var p_id = $(this).data('p_id');
    action({
            data: {'action': 'askToJoin', 'p_id':p_id},
            success: function(data) {
                $(".asked_message").fadeIn();
            }}
    );
});


/***********************************************************************************************************************
 *
 *      ~like minded group
 *
 ***********************************************************************************************************************/
bind('.find_like_minded' , 'click' , null , function(e)
{
    $(".button_result").hide();
    findNewLikeMinded();
});

// recursive ajax function for finding new like minded members
function findNewLikeMinded() {
    $(".find_loading").show();
    action({
            data: {'action': 'findLikeMinded'},
            success: function(data) {
                var returned = eval('(' + data + ')');
                $(".find_loading").hide();
                var num_new = returned.num_new_members;
                // display num new members
                $('.num_new_found').html(num_new);
                $('.num_processed').html(returned.num_processed);
                $(".find_result").show();
                // change total members number
                var total_num = $(".total_members").data('num');
                total_num += num_new;
                $(".total_members").html(total_num);
                $(".total_members").data('num', total_num);
                // if there were members adjust shit appropriately
                if (num_new != 0) {
                    $(".no_members").hide();
                    $(".some_members").show();
                    $(".like_minded_members").prepend(returned.html);
                    bindOnNewElements();
                }
                if (returned.num_processed != 0) {
                    findNewLikeMinded();
                }
            }}
    );
}

bind('.clear_like_minded' , 'click' , null , function(e)
{
    $(".button_result").hide();
    if (confirm("are you sure you want to do this? After clearing you will have to recalculate the members of your like-minded group.")) {
        action({
                data: {'action': 'clearLikeMinded'},
                success: function(data) {
                    $(".like_minded_members").empty();
                    $(".clear_result").show();
                    $(".total_members").html(0);
                    $(".total_members").data('num',0);
                }}
        );
    }
});

bind('.like_minded_explanation' , 'click' , null , function(e)
{
    $(".button_explanations").show();
    $(".home_header_info").css("overflow", "visible");
});

bind('.like_minded_close' , 'click' , null , function(e)
{
    $(".home_header_info").css("overflow", "hidden");
    $(".button_explanations").hide();
});