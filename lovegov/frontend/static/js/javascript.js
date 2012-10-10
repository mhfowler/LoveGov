/***********************************************************************************************************************
 *
 *     ~init js, does stuff that delegated can't!
 *
 ***********************************************************************************************************************/
var rebind;
var FACEBOOK_APP_ID = 184966154940334;


function bindOnReload() {

    // things that get bound on items loaded by feeds and such (everything)
    bindOnNewElements();

    // ajax get fb friends for sidebar after page load
    getFBInviteFriends();

    // any feeds on the page, go get themselves
    initFeedParameters();
    refreshFeeds();

    // for all home pages
    navSectionOpenAll();
    initHomePage();
    selectHeaderLinks();

    // for reps paged
    loadGoogleMap();

    // about page
    teamSection();

    // misc
    bindNotificationsDropdownClickOutside();

    // like minded computing
    likeMindedComputing();

    // cached back button
    showBackButtonIfCachedPage();

    switch (rebind) {

        case "home":
            initHomePage();
            break;
        case "legislation":
            shortenLongText();
            showLegSelectors();
            showSelectors();
            loadBillSelect2();
            break;
        case "legislation_detail":
            shortenLongText();
            break;
        case "profile":
            break;
        case "groupedit":
            loadGroupEdit();
            break;
        case 'questions':
            break;
        case 'poll_detail':
            updateQuestionStubsDisplay();
            break;
        case 'browse':
            break;
        case 'settings':
            bindSettings();
            break;
        case 'about':
            bindAbout();
            break;
    }
}

/* gets called on all new elements appended to dom */
function bindOnNewElements() {

    // dummy_links are prevent defaulted
    undelegated();

    // show any visible helper bubles
    showBubbles();

    // question stubs
    updateQuestionStubsDisplay();

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

    // initialize self initializing elements
    initializeDomElements();

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

    HISTORY_ENABLED = prepareHistory();

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
    }, 10000);

    // start background tasks
    findNewLikeMinded();

});

function prepareHistory() {

    // Prepare
    var History = window.History; // Note: We are using a capital H instead of a lower h
    if ( !History.enabled )
    {        // History.js is disabled for this browser.
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

    return true;
}


/***********************************************************************************************************************
 *
 *     ~Delegated binding function, similar to jquery's deprecated ".live()"
 *
 ***********************************************************************************************************************/
function bind(selector, events, data, handler) {
    $(document).on(events, selector, data, handler);
}

function getValueFromKey(element, key) {
    var value = element.data(key);
    if (typeof(value) == 'undefined') {
        value = "";
    }
    return value;
}

function backgroundAction(dict, analyze) {
    action(dict, true, analyze);
}

function analyzeAction(dict) {
    action(dict, false, true);
}

var current_page_nonce=0;
function action(dict, in_background) {
    var data = dict['data'];
    var action = data['action'];

    var pre_page_nonce = current_page_nonce;
    var success_fun = function(data) {
        if (pre_page_nonce == current_page_nonce || in_background) {
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
                var result = $.parseJSON(jqXHR.responseText);
                if(result['silent']=='false') {
                    getModal("forbidden_modal");
                }
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
    var timeout = dict['timeout'];
    var complete_fun = dict['complete'];
    var url = window.location.href;
    var path = window.location.pathname;
    data['url'] = url;

    if(checkAnalyzeAction(action)) {
        success_fun = analyzeFunction(success_fun, path, action);
    }

    $.ajax({
        url: '/action/',
        type: 'POST',
        data: data,
        success: success_fun,
        error: error_fun,
        complete: complete_fun,
        timeout: timeout
    });

}

// Check whether the given action ought to have analytics turned on
function checkAnalyzeAction(action) {
    return CLIENT_SIDE_ANALYTICS && AJAX_ANALYTICS_ACTIONS.indexOf(action) >= 0;
}


// Attaches analytic functionality to the given function, fun
function analyzeFunction(fun, url, action) {
    var analyze_nonce_id = startPageAnalytic(url, action);
    return function(data) {
        finishPageAnalytic(analyze_nonce_id);
        return fun(data);
    }
}



function smoothTransition(element, fun, time) {
    var old_height = element.height();
    fun();
    var new_height = element.height();
    element.css("height", old_height);
    element.animate({"height":new_height}, {"duration":time, "complete":function(){element.css("height", "auto");}});
}

function updatePage() {

    // update page on schedule
    action({
        'data': {'action':'updatePage', 'log-ignore':true},
        success: function(data)
        {
            var obj = $.parseJSON(data);

            // update notifications num
            if (obj.notifications_num == 0) {
                $(".notifications_box").removeClass("new-notifications");
            }
            else {
                $(".notifications_box").addClass("new-notifications");
            }
            $(".notifications_dropdown_button").text(obj.notifications_num);
        }
    });

    // also send analytics data on schedule
    postPageAnalytics();
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

function pushURL(url) {
    History.pushState( {k:1}, "LoveGov: Beta", url);
    PATH = url;
}

function selectHeaderLinks() {
    $(".header_link").removeClass("clicked");
    var header_link = $('.header_link[href="' + PATH + '"]');
    header_link.addClass("clicked");
}

function ajaxReload(theurl)
{
    if (theurl == PATH) {
        return false;
    }

    storeCachedPage();
    current_page_nonce += 1;
    var pre_page_nonce = current_page_nonce;
    $('#search-dropdown').hide();
    $('.main_content').hide();
    $(document).scrollTop(0);

    var success_fun = function(data)
    {
        if (pre_page_nonce == current_page_nonce) {
            $('.ajax_reloading_heart').hide();
            var returned = $.parseJSON(data);
            pushURL(returned.url);
            $('body').css("overflow","scroll");
            $('.main_content').css("top","0px");
            $(".main_content").html(returned.html);
            $('.main_content').show();
            rebind = returned.rebind;
            bindOnReload();
        }
    };

    if(checkAnalyzeAction(action)) {
        success_fun = analyzeFunction(success_fun, theurl, action);
    }

    var data = {'url':window.location.href};
    if ($(".october_header").length != 0) {
        data['has_login_frame'] = true;
    }

    $('.ajax_reloading_heart').show();
    $.ajax({
        url: theurl,
        type: 'GET',
        data: data,
        success: success_fun,
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
    var navlink = getNavLink(PATH);
    selectNavLink(navlink);
}

/* sets feed parameters pased on js variables */
function initFeedParameters() {

    var hot_pages = ['/home/', '/questions/'];
    if (hot_pages.indexOf(PATH) != -1) {
        feed_rank = 'H';
    }
    else {
        feed_rank = 'N';
    }

    var feed_data = feed_memory[PATH];
    if (feed_data) {
        var saved_feed_rank = feed_data['feed_rank'];
        if (saved_feed_rank) {
            feed_rank = saved_feed_rank;
        }
        var saved_feed_types = feed_data['feed_types'];
        if (saved_feed_types) {
            feed_types = $.parseJSON(saved_feed_types);
        }
        var saved_question_rank = feed_data['question_rank'];
        if (saved_question_rank) {
            question_rank = saved_question_rank;
        }
    }

    selectRank(feed_rank);
    selectQuestionRank(question_rank);
    selectFeedTopic();
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
    $('select.select_2').each(function(i,e) {
        var placeholder = $(this).data("placeholder");
        if (typeof(placeholder)!='undefined') {
            $(this).select2({
                placeholder: placeholder
            });
        } else {
            $(this).select2();
        }
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

    $(".tooltip-top").tooltip({'placement': 'top', 'animation': false});
    $(".tooltip-bottom").tooltip({'placement': 'bottom', 'animation': false});
    $(".tooltip-right").tooltip({'placement': 'right', 'animation': false});
    $(".tooltip-left").tooltip({'placement': 'left', 'animation': false});
}

bind(".bind_link", "click", null, function(event) {
    var url = $(this).data('url');
    window.location.href = url;
    event.stopPropagation();
});


/***********************************************************************************************************************
 *
 *      ~Home
 *
 ***********************************************************************************************************************/
/* ajax load home sections */
function homeReload(theurl) {
    storeCachedPage();
    current_page_nonce += 1;
    var pre_page_nonce = current_page_nonce;
    $('#search-dropdown').hide();
    $(".home_reloading").show();


    // if coming from a home page
    if ($(".home_sidebar").length!=0) {

        var success_fun = function(data) {
            if (pre_page_nonce == current_page_nonce) {
                $(".home_reloading").hide();
                var returned = $.parseJSON(data);
                pushURL(returned.url);
                $(".home_focus").html(returned.focus_html);
                bindOnReload();
            }
        };

        if(checkAnalyzeAction(action)) {
            success_fun = analyzeFunction(success_fun, theurl, action);
        }

        $.ajax({
            url:theurl,
            type: 'GET',
            data: {'url':window.location.href, 'has_sidebar':1},
            success: success_fun,
            error: function(jqXHR, textStatus, errorThrown)
            {
                if (pre_page_nonce == current_page_nonce) {
                    $('body').html(jqXHR.responseText);
                }
            }
        });
    }
    else {
        ajaxReload(theurl, "crazy");
    }
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
            data: {'action':'getFBInviteFriends', 'log-ignore':true },
            success: function(data)
            {
                var returned = $.parseJSON(data);
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
    $(".left_link").removeClass("clicked");
    homeReload($(this).attr("href"));

    /*
     //var navbar_section = $(this).parents(".navbar_section");
     if (!$(this).hasClass("clicked")) {
     //selectNavLink($(this));
     //closeAllNavBarSections();
     homeReload($(this).attr("href"));
     } else {
     /*
     if (navbar_section.hasClass("section_shown")) {
     navSectionToggle(navbar_section, false, true);
     } else {
     navSectionToggle(navbar_section, true, true);
     } */
    //}
});

bind(".left_link", 'click', null, function(event) {
    if (!$(this).hasClass("clicked")) {
        selectNavLink($(this));
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
        // add/remove header link stuff
        $(".header_link").removeClass("clicked");
        //$(".home_header_link").addClass("clicked");
        // toggle section and remove new items num
        if (navlink.hasClass("navbar_link")) {
            var num_new_content = navlink.parents(".home_link_wrapper").find(".num_new_content");
            num_new_content.empty();
            var navbar_section = navlink.parents(".navbar_section");
            navSectionToggle(navbar_section, true, false);
        }

        //moveAsterisk(navlink);
    }
}

/* helper to get navlink element from url */
function getNavLink(url) {
    return $('.left_link[href="' + url + '"]');
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
        var current_link = getNavLink(PATH);
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
        wrapper.find(".hide_info").html('&#8211 minimize info');
        // If the info was un-expanded, show it at un-expanded form
        if( !info_expanded )
        {
            info_div.animate({"height":reduced_height}, animation_time);
            wrapper.find(".expand_info").html('+ expand info');
        } // If the info was expanded, show the full expanded form
        else
        {
            expandAnimation(info_div,animation_time);
            wrapper.find(".expand_info").html('&#8211 reduce info');
        }
    }
    // Otherwise, toggle the info expanded property
    else if( info_expanded )
    {   // Set expanded to false and un-expand the info
        wrapper.data('info_expanded', false);
        wrapper.find(".text_expanded").hide();
        wrapper.find(".text_unexpanded").show();
        info_div.animate({"height":reduced_height}, animation_time);
        wrapper.find(".expand_info").html('+ expand info');
    }
    else
    {   // Otherwise set expanded to true and expand the info
        wrapper.data('info_expanded', true);
        wrapper.find(".text_expanded").show();
        wrapper.find(".text_unexpanded").hide();
        expandAnimation(info_div,animation_time);
        wrapper.find(".expand_info").html('&#8211 reduce info');
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
        wrapper.find(".expand_info").html('+ show info');
        wrapper.find(".hide_info").html('+ show info');
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
    if ($(this).hasClass("clicked")) {
        $(this).removeClass("clicked");
        vote(wrapper, c_id, 0);
    }
    else {
        wrapper.find(".heart_button").removeClass("clicked");
        $(this).addClass("clicked");
        var heart_number = wrapper.find(".heart_number");
        var status = parseInt(heart_number.text());
        status += 1
        heart_number.text(status);
        vote( wrapper , c_id , 1 );
    }
});

bind( "div.heart_minus" , "click" , null , function(event)
{
    var wrapper = $(this).parent();
    var c_id = wrapper.data('c_id');
    if ($(this).hasClass("clicked")) {
        $(this).removeClass("clicked");
        vote(wrapper, c_id, 0);
    }
    else {
        wrapper.find(".heart_button").removeClass("clicked");
        $(this).addClass("clicked");
        var heart_number = wrapper.find(".heart_number");
        var status = parseInt(heart_number.text());
        status -= 1
        heart_number.text(status);
        vote( wrapper , c_id , -1 );
    }
});

// Vote for the feed AJAX request
function vote(wrapper, content_id, v)
{
    action({
        data: {'action':'vote','c_id':content_id, 'vote':v },
        success: function(data)
        {
            var returned = $.parseJSON(data);
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
            var returned = $.parseJSON(data);
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


function selectFeedTopic() {
    $(".topic_button").removeClass("clicked");
    var button = $('.topic_button[data-t_alias="' + feed_topic + '"]');
    if (button.length!=0) {
        button.addClass("clicked");
    }
}

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
        clearTypes();
        selectType($(this).data('type'));
    }
    else {
        removeType($(this).data('type'));
    }
});

bind(".like_minded_button", "click", null, function(event) {
    var container = $(this).parents(".feed_main");
    var like_minded_val;
    if ($(this).is(":checked")) {
        like_minded_val = 1;
    }
    else {
        like_minded_val = "";
    }
    container.data("like_minded", like_minded_val);
    refreshFeed(container);
});

bind(".like_minded_link", "click", null, function(event) {
    $(".like_minded_header_dialogue").fadeIn();
});

bind(null, "click", null, function(event) {
    var click_id = event.target.id;
    if (click_id.indexOf("like_minded_link_id")==-1) {
        $(".like_minded_header_dialogue").hide();
    }
});

bind(".like_minded_header_dialogue", 'click', null, function(event) {
    event.stopPropagation();
});

function clearTypes() {
    $(".type_button").removeClass("clicked");
    feed_types = [];
}

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
    var button = $(this);
    var container = button.parents(".feed_main");
    /*
     if (button.parent().hasClass(".feed_main")) {
     container = button.parents(".feed_main");
     }
     else {
     container = button.closest(".home_focus").find(".feed_main");
     }*/
    refreshFeed(container);
});


/* replaces feed, rather than appendin */
function refreshFeed(container) {
    container.data('feed_start', 0);
    getFeed(container);
}

var feed_memory = {};
var feed_types = [];
var feed_rank = 'H';
var feed_topic = null;
var question_rank = "R";
function getFeed(container) {

    container.find(".load_more").hide();

    var feed_nonce_pre_request = container.data('feed_nonce');
    feed_nonce_pre_request += 1;
    container.data('feed_nonce', feed_nonce_pre_request);

    var feed_start = container.data('feed_start');
    var replace = (feed_start==0);
    var single_item = container.data('single_item');
    if (replace) {
        var old_height = $("body").height();
        //container.css('min-height', old_height);
        container.find(".feed_content").empty();
        container.find(".everything_loaded_wrapper").hide();
        container.find(".load_previous").hide();
        // feed nonce increases when you replace content
    }

    var feed_types_json = JSON.stringify(feed_types);
    var feed = container.data('feed');
    var time = 5;
    var feed_timeout = setTimeout(function(){
        if (!single_item || replace) {
            container.find(".feed_fetching").show();
        }
        else {
            container.find('.feed_next').show();
        }
    },time);
    var like_minded = getValueFromKey(container, 'like_minded');
    var data;
    if (feed == 'getFeed')
    {
        data = {'action': 'getFeed', 'path': PATH, 'feed_rank':feed_rank, 'feed_start':feed_start, 'feed_types':feed_types_json, 'like_minded':like_minded};
    }
    else if (feed == 'getQuestions')
    {
        var default_display = container.data("default_display");
        data = {'action': 'getQuestions', 'feed_rank':feed_rank, 'question_rank':question_rank,
            'feed_start':feed_start, 'feed_topic':feed_topic, 'default_display':default_display };
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
        // check if trial question answering
        if (container.data("trial_questions")) {
            data['trial_questions'] = 1;
        }
        // check if only single item
        if (container.data("single_item")) {
            data['single_item'] = 1;
        }
    }
    else if (feed == 'getUserActivity')
    {
        var p_id = getValueFromKey(container, 'profile_id');
        data = { 'action': 'getUserActivity', 'feed_start':feed_start, 'p_id':p_id };
    }
    else if (feed == 'getElections')
    {
        data = {'action': 'getElections','feed_rank':feed_rank, 'feed_start':feed_start};
        var state = getValueFromKey(container, 'state');
        var city = getValueFromKey(container, 'city');
        data['state'] = state;
        data['city'] = city;
    }
    else if (feed == 'getGroups') {
        data = {'action': 'getGroups','feed_rank':feed_rank, 'feed_start':feed_start};
        var state = getValueFromKey(container, 'state');
        var city = getValueFromKey(container, 'city');
        data['state'] = state;
        data['city'] = city;
    }
    else if (feed == 'getLegislation') {
        var session = $('.session_select').val();
        var session_json;
        if ($("." + $('.session_select').data('selector')).hasClass('clicked')) {
            session_json = JSON.stringify(session);
        }
        else {
            session_json = JSON.stringify([]);
        }
        var type = $('.type_select').val();
        var type_json;
        if ($("." + $('.type_select').data('selector')).hasClass('clicked')) {
            type_json = JSON.stringify(type);
        }
        else {
            type_json = JSON.stringify([]);
        }
        var subject = $('.subject_select').val();
        var subject_json;
        if ($("." + $('.subject_select').data('selector')).hasClass('clicked')) {
            subject_json = JSON.stringify(subject);
        }
        else {
            subject_json = JSON.stringify([]);
        }
        var committee = $('.committee_select').val();
        var committee_json;
        if ($("." + $('.committee_select').data('selector')).hasClass('clicked')) {
            committee_json = JSON.stringify(committee);
        }
        else {
            committee_json = JSON.stringify([]);
        }
        var introduced = $('.introduced_select').val();
        var introduced_json;
        if ($("." + $('.introduced_select').data('selector')).hasClass('clicked')) {
            introduced_json = JSON.stringify(introduced);
        }
        else {
            introduced_json = JSON.stringify([]);
        }
        var sponsor_body = $('.sponsor_select_body').val();
        var sponsor_body_json;
        if ($("." + $('.sponsor_select_body').data('selector')).hasClass('clicked')) {
            sponsor_body_json = JSON.stringify(sponsor_body);
        }
        else {
            sponsor_body_json = JSON.stringify([]);
        }
        var sponsor_name = $('.sponsor_select_name').val();
        var sponsor_name_json;
        if ($("." + $('.sponsor_select_name').data('selector')).hasClass('clicked')) {
            sponsor_name_json = JSON.stringify(sponsor_name);
        }
        else {
            sponsor_name_json = JSON.stringify([]);
        }
        var sponsor_party = $('.sponsor_select_party').val();
        var sponsor_party_json;
        if ($("." + $('.sponsor_select_party').data('selector')).hasClass('clicked')) {
            sponsor_party_json = JSON.stringify(sponsor_party);
        }
        else {
            sponsor_party_json = JSON.stringify([]);
        }
        data = {'action': 'getLegislation', 'feed_start':feed_start, 'session_set':session_json,
            'type_set':type_json, 'subject_set':subject_json, 'committee_set':committee_json,
            'introduced_set':introduced_json, 'sponsor_body_set':sponsor_body_json,
            'sponsor_name_set':sponsor_name_json, 'sponsor_party':sponsor_party_json};
    }

    // save in memory
    feed_memory[PATH] = data;

    var action_dict = {
        data: data,
        success: function(data) {
            var returned = $.parseJSON(data);

            var feed_nonce_post_request = container.data('feed_nonce');
            if (feed_nonce_pre_request != feed_nonce_post_request) {
                return;
            }

            if (replace || single_item) {
                container.find(".feed_content").html(returned.html);
            }
            else {
                container.find(".feed_content").append(returned.html);
            }

            if (!replace) {
                container.find(".load_previous").show();
            }
            container.find(".load_next").show();

            container.data( 'feed_start' , feed_start + returned.num_items );
            clearTimeout(feed_timeout);
            container.find(".feed_fetching").hide();
            container.find(".feed_next").hide();
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
            else {
                container.find(".load_more").show();
            }
            bindOnNewElements();
            //container.css("min-height", container.height());
        }
    };

    analyzeAction(action_dict);
}

/* load (more) feed items */
bind(".load_more" , "click" , null , function(event) {
    var container = $(this).parents(".feed_main");
    getFeed(container);
});

bind(".load_next" , "click" , null , function(event) {
    var container = $(this).parents(".feed_main");
    getFeed(container);
});

bind(".load_previous" , "click" , null , function(event) {
    var container = $(this).parents(".feed_main");
    var feed_start = container.data('feed_start');
    feed_start = Math.max(feed_start - 2, 0);
    container.data('feed_start', feed_start);
    getFeed(container);
});

/***********************************************************************************************************************
 *
 *      ~About page
 *
 **********************************************************************************************************************/
function bindAbout() {
    var start_page = PATH;
    var section = $('.about_section[data-url="' + start_page + '"]');
    if (section.length != 0) {
        $(".about_section").hide();
        section.fadeIn(250);
    }
}

bind("div.about-div-button", "click",
    function(e) {
        $('div.about-div-button').removeClass("active");
        $("div.about_section").hide();
        var section_url = $(this).data('url');
        var to_show =  $('.about_section[data-url="' + section_url + '"]');
        to_show.fadeIn(250);
        $(this).toggleClass('active');
        //History.pushState( {k:1}, "LoveGov: Beta", section_url);
    });

function teamSection()
{

    var developerDivs = $('.who-are-we-circle-div');
    if (developerDivs.length != 0) {
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
}

/***********************************************************************************************************************
 *
 *      ~Left sidebar
 *
 **********************************************************************************************************************/
bind('.feedback_toggle', 'click', function()
{
    leftSideToggle($(".feedback_wrapper"));
});

bind('.invite_toggle', 'click', function()
{
    var wrapper = $(".invite_tab_wrapper");
    if (!wrapper.hasClass("open")) {
        $("#email-input").focus();
    }
    leftSideToggle(wrapper);
});

bind('#feedback-submit', 'click', function(event)
{
    event.preventDefault();
    var text = $('#feedback-text').val();
    var name = $('#feedback-name').val();
    action({
        data: {'action':'feedback','text':text,'path':PATH,'name':name},
        success: function(data)
        {
            $('#feedback-name').val("");
            $('#feedback-text').val("");
            $('#feedback-response').show();
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
    var msg = $("textarea#email-message").val();
    $("#invite-return-message").text("");
    $("#invite-return-loading-img").show();
    action({
        data: {'action':'invite','email':email, 'msg': msg},
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
    else { wrapper.animate({left:'-528px'},500); }
    setTimeout(function()
    {
        wrapper.css({'z-index':'100'});
        wrapper.children('.create' +
            'e-img').css({'z-index':'101'});
    },500);

    wrapper.removeClass('open');
}

function leftSideToggle(wrapper)
{
    if (wrapper.hasClass('open'))
    {
        closeLeftSideWrapper(wrapper);
    }
    else
    {
        wrapper.addClass('open');
        wrapper.css({'z-index':'101'});
        wrapper.children('.create-img').css({'z-index':'102'});
        wrapper.animate({left:'-1px'},500);

        wrapper.bindOnce('clickoutside',function(event)
        {
            if (event.target.className.indexOf("leftside_tab_toggle") == -1) {
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
            var obj = $.parseJSON(data);
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
            var obj = $.parseJSON(data);
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
            var obj = $.parseJSON(data);
            being_edited.html(obj.explanation_html);
            not_editing_display.show();
            var wrapper = not_editing_display.parents(".inline_editable");
            smoothTransition(wrapper, function(){ wrapper.css({'min-height':'0px'})}, 400);
        }
    });
}


function editPetitionFullText(p_id, full_text, being_edited, not_editing_display )
{
    action({
        'data': {'action':'editPetitionFullText', 'p_id':p_id, 'full_text':full_text},

        success: function(data)
        {
            var obj = $.parseJSON(data);
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
    doing_editing_display.find(".edit_links").show();
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
    var old_height = wrapper.height();
    wrapper.css({'min-height':old_height});
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
    form.find(".registering_gif").show();
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
            form.find(".registering_gif").hide();
            var returned = $.parseJSON(data);

            if (returned.success) {
                window.location.href = "/hello/";
            }
            else {
                form.replaceWith(returned.html);
            }
        }
    });
});

bind(".log_in_button", 'click', null, function(event) {
    $(".signing_in_gif").show();
});

/***********************************************************************************************************************
 *
 *      ~October login
 *
 **********************************************************************************************************************/
bind(".login_header_link", 'click', null, function(event) {
    var url = $(this).data('url');
    $(".login_central").hide();
    $('.login_central[data-url="' + url + '"]').fadeIn(1000);
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
    $(".no_phonenumber").hide();
    var wrapper = $(this).parents(".message_politician_wrapper");
    var p_id = wrapper.data("p_id");
    var message = wrapper.find(".message_textarea").val();
    var phone_number = wrapper.find(".phonenumber_input").val();
    if (phone_number == "") {
        $(".no_phonenumber").show();
    }
    else {
        action({
                data: {
                    'action': 'messagePolitician',
                    'p_id': p_id,
                    'phone_number':phone_number,
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
    }
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



bind(".see_all_bio" , 'click' , null , function(event)
{
    getModal('see_all_bio', {'p_id':$(this).data('p_id')});
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
                var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
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
                    if (returned.group_type != "E") {
                        $(".groups_wrapper").prepend(navlink_html);
                    }
                    else {
                        $(".elections_wrapper").prepend(navlink_html);
                    }
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
    $("div.modal-wrapper").hide();
    $('div.modal-general').hide();
    $('div.modal_overdiv').hide();
}

function showModal() {
    $("div.modal-wrapper").show();
    var modal_general = $('div.modal_general');
    var height = modal_general.height();
    var yoffset = window.pageYOffset;
    modal_general.css("top", yoffset-100);
    modal_general.fadeIn(100).css('display', 'inline-block');
    $('div.modal_overdiv').fadeIn(500);
}

// Bind clicks outside modal to closing the modal
bind( 'div.modal-wrapper', 'click', hideModal);
bind( 'div.modal_overdiv', 'click', hideModal);
bind( '.modal_close', 'click', hideModal);
// Don't propogate modal clicks to modal-wrapper (which would close modal)
bind( 'div.modal-general', 'click', function(e) {e.stopPropagation();});

function getModal(modal_name,data,callback)
{
    if( typeof(data)=='undefined'){ data = { 'modal_name':modal_name }; }
    else{ data['modal_name'] = modal_name; }

    data['action'] = 'getModal';
    var modal_general = $('div.modal_general');
    var modal_content = $('div.modal_content');

    // If create modal has recently been opened, use version in memory to avoid data loss
    if(modal_name==modal_general.data('last-loaded')) {
        if(modal_name=="create_modal" ) {
            // Don't cache different groups
            if(!data.hasOwnProperty('gid') || modal_general.data('last-group')==data['gid']) {
                showModal();
                if(callback) callback();
                return;
            }
        }
    }

    showModal();
    modal_content.html('<img src="/static/images/icons/ajax-loader.gif" style="margin: 50px;">');

    action({
        data: data,
        success: function(response_data)
        {
            var returned = eval('(' + response_data + ')');
            modal_content.html( returned.modal_html );
            modal_general.data('last-loaded',modal_name);
            modal_general.data('last-group',data['gid']);


            showModal();
            bindOnNewElements();
            if(callback) callback();
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
                var obj = $.parseJSON(data);
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
            var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
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
                            var obj = $.parseJSON(data);
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
 var obj = $.parseJSON(data);
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
        $(this).parents(".answer_wrapper").removeClass("clicked");
    }
    else {
        stub.data('answer_changed', true);
        stub.find(".answer_choice").removeClass("clicked");
        stub.find(".answer_wrapper").removeClass("clicked");
        $(this).addClass("clicked");
        $(this).parents(".answer_wrapper").addClass("clicked");
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
            var returned = $.parseJSON(data);
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
    var answer_changed = stub.data('answer_changed');
    var privacy = stub.data("privacy");
    if (privacy == 'False') {
        privacy = 'PUB';
    }
    if (privacy == 'True') {
        privacy = 'PRI';
    }
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
        if (only_unanswered && a_id!=-1) {
            stub.animate({"height":"0px"}, {
                "duration": 300,
                "complete":function(){
                    stub.hide();
                    var stubs = container.find(".question_stub:visible");
                    if (stubs.length==0) {
                        refreshFeed(container);
                    }
                }
            });
            var next_stub = stub.next('.question_stub');
            $(".qa_tutorial_question").removeClass("qa_tutorial_question");
            next_stub.addClass("qa_tutorial_question");
            $(".qa_bubble").hide();
            expandChooseInterface(next_stub);
            showBubbles();
        }
    }

    if (answer_changed && your_response == 0 ) {
        var q_bottom = stub.find(".question_item_bottom_wrapper");
        /*
         smoothTransition(q_bottom, function(){
         q_bottom.css({"height":'auto'});
         }, 200);*/
        q_bottom.css({"height":'auto',"overflow":"visible"});
        //q_bottom.fadeIn();
    }

    action({
        data: data,
        success: function(data) {
            var returned = $.parseJSON(data);
            if (default_display=='responses') {
                var new_element = $(returned.html);
                var old_height = stub.height();
                stub.replaceWith(new_element);
                stub = new_element;
                new_element.find(".question_expanded_responses").show();
                var new_height = new_element.height();
                new_element.css('height', old_height);
                new_element.animate({"height":new_height}, {"duration":200, "complete":function(){new_element.css("height", "auto");}});
            }
            stub.find(".num_responses span.num").html(returned.num_responses);
            var saved_message = stub.find(".saved_message");
            saved_message.show();
            saved_message.fadeOut(5000);

            if (answer_changed) {
                stub.data("answer_changed", false);
                var percent_agreed_bubbles = returned.lg_percent_agreed_bubbles;
                //$(".percent_agreed_wrapper").fadeOut(1000);
                $.each(percent_agreed_bubbles, function(i,e) {
                    var this_a_id = e.a_id;
                    var this_html = e.html;
                    var this_wrapper = stub.find('.answer_wrapper[data-a_id="' + this_a_id + '"]').find('.percent_agreed_wrapper');
                    this_wrapper.html(this_html);
                    this_wrapper.fadeIn(200);
                });
                setTimeout(function() {
                    //stub.find(".percent_agreed_wrapper").fadeOut(1000);
                }, 3000);

                var agreement_bargraph = stub.find(".agreement_bargraph_seed");
                if (agreement_bargraph.length!=0) {
                    initializeDomElement(agreement_bargraph);
                }
            }

            bindOnNewElements();
            updateMatches();
            updateStats();
            updateElementsAfterAnswer();

            // if should compute like minded then start it up
            if (returned.start_like_minded) {
                computing_like_minded = true;
                findNewLikeMinded();
            }
        }
    });
}

// hide percent agreed bubbles
bind('.percent_agreed_wrapper' , 'click' , null , function(event)
{
    $(".percent_agreed_wrapper").hide();
});

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
    var saved_message = item.find(".saved_message");
    saved_message.hide();
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
            saved_message.show();
            //saved_message.fadeOut(2000);
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
    var slider_dict = {'min':0,
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
    };
    if (div.hasClass("feed-importance-bar")) {
        slider_dict['orientation'] = 'vertical';
    }
    div.slider(slider_dict);
}


/***********************************************************************************************************************
 *
 *     ~ q&a feed
 *
 **********************************************************************************************************************/
bind('.only_unanswered' , 'click' , null , function(event)
{
    var container = $(this).parents(".feed_main");
    container.data("only_unanswered", $(this).is(":checked"));
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
        data: {'action':'updateMatch', 'to_compare_alias':to_compare_alias, 'display':display, 'log-ignore':true},
        success: function(data) {
            var returned = $.parseJSON(data);
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
    var data = {'action':'updateStats', 'object':object, 'log-ignore':true};
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
    if (object == 'poll_stats') {
        data['p_id'] = stats.data('p_id');
    }
    if (object == 'not_enough_questions_warning') {
        data['of_what'] = stats.data('of_what');
    }
    if (object == 'poll_completed_num') {
        data['p_id'] = stats.data('p_id');
    }
    action({
        data: data,
        success: function(data) {
            var returned = $.parseJSON(data);
            var new_element = $(returned.html);
            stats.replaceWith(new_element);
        }
    });
}

bind('div.stats-box.following_user_modal_link', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('following_user_modal', {'user': p_id});
});

bind('div.stats-box.user_following_modal_link', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('user_following_modal', {'user': p_id});
});

bind('div.stats-box.posts_link', 'click', function(e) {
    var posts_tab = $('a.profile_tab.posts_tab')
    posts_tab.click();
    $('body').animate({
        scrollTop: posts_tab.offset().top
    }, 1000);
});

bind('div.stats-box.answers_link', 'click', function(e) {
    window.location.href = 'worldview';
});

bind('div.stats-box.signatures_link', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('user_signatures_modal', {'user': p_id});
});

bind('div.stats-box.groups_link, span.profile-groups.breakdown-box a.link-all', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('user_groups_modal', {'user': p_id});
});

bind('div.stats-box.groups_link, span.profile-groups.breakdown-box a.link-all', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('user_groups_modal', {'user': p_id});
});

bind('span.profile-politicians.breakdown-box a.link-all', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('user_supporting_modal', {'user': p_id});
});

bind('div.stats-box.supporter-box', 'click', function(e) {
    var p_id = $('div.stats_object').data('p_id');
    getModal('supporting_user_modal', {'user': p_id});
});

function updateElementsAfterAnswer() {
    $(".update_after_answer").each(function(i,e) {
        updateDomElement($(this));
    });
}

function updateDomElement(element) {
    var data = element.data();
    action({
        data: data,
        success: function(data) {
            var returned = $.parseJSON(data);
            element.html(returned.html);
            postInitialize(element);
        }
    });
}

function initializeDomElements() {
    $(".initialize_self").each(function(i,e) {
        $(this).find(".initialize_loading").show();
        initializeDomElement($(this));
    });
}

function initializeDomElement(element) {
    var data = element.data();
    element.removeClass("initialize_self");
    action({
        data: data,
        success: function(data) {
            var returned = $.parseJSON(data);
            element.html(returned.html);
            postInitialize(element);
        }
    });
}

function postInitialize(element) {

    if (element.hasClass("agreement_bargraph_seed")) {
        element.find(".agreement_bargraph").fadeIn();
    }

    if (element.hasClass("agreement_people_list_seed")) {
        element.find(".agreement_people_list_wrapper").fadeIn();
    }

    if (element.hasClass("presidential_matching_counter")) {
        var questions_answered = element.find(".questions_answered");
        var num = questions_answered.data('num');
        if (num >= 10) {
            $(".trial_question_answering").fadeOut();
            $(".trial_answering_questions_header").fadeOut();
            $(".sign_up_wrapper").fadeIn();
            setTimeout(function() {
                $(".big_loading").hide();
                $(".presidential_matching_finished").show();
                $(".sign_up_wrapper").fadeIn();
            }, 0);
        }
    }

    bindOnNewElements();

}


bind('.see_who_agrees', 'click', function(e) {
    var wrapper = $(this).parents(".agreement_wrapper");
    var people_list = wrapper.find(".agreement_people_list_seed");
    if (!$(this).hasClass("clicked")) {
        $(this).addClass("clicked");
        people_list.show();
    }
    else {
        $(this).removeClass("clicked");
        people_list.hide();
    }
});

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
        histogram_metadata.topic_text = topic_text;
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
    histogram_wrapper.find(".histogram_loading_members").show();
    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
    histogram_metadata.loading_members_nonce += 1;
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
        setHistogramExplanation(histogram_wrapper);
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
                var returned =  $.parseJSON(data);
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
    var old_loading_members_nonce = histogram_metadata.loading_members_nonce;
    if (post_data) {
        action({
                data: post_data,
                success: function(data)
                {
                    var returned =  $.parseJSON(data);
                    var histogram_metadata = loadHistogramMetadata(histogram_wrapper);
                    if (histogram_metadata.loading_members_nonce == old_loading_members_nonce) {
                        appendHistogramMembersHTML(histogram_wrapper, returned.html, returned.num, identical, replace);
                    }
                }
            }
        );
    }
}

/* appends html to members wrapper or identical wrapper appropriately, depending on identical=True */
function appendHistogramMembersHTML(histogram_wrapper, html, num, identical, replace) {
    histogram_wrapper.find(".histogram_loading_members").hide();
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
        var topic_text = histogram_metadata.topic_text;
        if (topic_text != "All Topics") {
            message += " over " + topic_text + " questions";
        }
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
            var returned =  $.parseJSON(data);

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

    var fb_name = $(this).data('fb_name');
    var fb_share_id = $(this).data('fb_share_id');

    // open share modal in new window
    window.open('http://www.facebook.com/dialog/feed?app_id='+FACEBOOK_APP_ID+'&to='+fb_share_id+'&display=popup&name=LoveGov&link=http://lovegov.com&redirect_uri=http://lovegov.com/popup_redirect&description='+
        'LoveGov is a political social network that personalizes politics. We are making it easy to stay informed and get involved.',
        '_blank','width=450,height=300');
});



/***********************************************************************************************************************
 *
 *      ~Facebook Share Content
 *
 ***********************************************************************************************************************/
bind( '.facebook_share_content_button' , 'click' , null , function(e)
{

    var c_id = $(this).data('c_id');
    var url = $(this).data('url');
    var img = $(this).data('img');
    var title= $(this).data('title');
    var description = $(this).data('description');

    window.open('http://www.facebook.com/dialog/feed?app_id='+FACEBOOK_APP_ID+'&link=http://lovegov.com/'+url+
        '&picture=http://lovegov.com/'+img+'&name=' + title +
        '&description= '+description+
        '&redirect_uri=http://lovegov.com/popup_redirect&display=popup',
        '_blank','width=450,height=300');
});


//bind( '.facebook_share_content_submit' , 'click' , null , function(e)
//{
//    e.preventDefault();
//
//    var share_message = $(this).parents('.facebook_share_form').find('textarea[name="facebook_share_message"]').val();
//    var link = $(this).data('fb_link');
//
//    var url = "/fb/action/?fb_action=share";
//    url += "&message=" + share_message;
//
//    if( link != null ) { url += "&fb_link=" + link; }
//
//    url += "&action_to_page=" + window.location.pathname;
//
//    window.location.href = url
//
//});


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
            var returned =  $.parseJSON(data);
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
            var returned =  $.parseJSON(data);
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
    var sign_areas = $('.sign_area[data-p_id="' + p_id + '"]');
    action({
            data: {'action': 'signPetition', 'p_id':p_id},
            success: function(data) {
                var returned = $.parseJSON(data);
                sign_areas.replaceWith(returned.sign_area);
                signers_sidebar.replaceWith(returned.signers_sidebar);
                updateStats();
            }}
    );
});

bind('.finalize_button' , 'click' , null , function(e)
{
    var p_id = $(this).data('p_id');
    var signers_sidebar = $(this).parents(".signers_sidebar");
    var sign_areas = $(".sign_area");
    action({
            data: {'action': 'finalizePetition', 'p_id':p_id},
            success: function(data) {
                var returned = $.parseJSON(data);
                sign_areas.replaceWith(returned.sign_area);
                signers_sidebar.replaceWith(returned.signers_sidebar);
            }}
    );
});


bind('.see_all_signers' , 'click' , null , function(e)
{
    var data = { 'p_id' : $(this).data("p_id") };
    getModal('see_all_signers_modal',data);
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

bind('.anon_x' , 'click' , null , function(e)
{
    $(this).parents(".anon_welcome").hide();
    $.cookie('closed_anon', 1);
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
                var returned = $.parseJSON(data);
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
                var returned = $.parseJSON(data);
                $(".asked_message").replaceWith(returned.html);
            }}
    );
});


/***********************************************************************************************************************
 *
 *      ~like minded group
 *
 ***********************************************************************************************************************/
// recursive ajax function for finding new like minded members. doesn't do anyting if computing_like_minded is false
var computing_like_minded = false;
var like_minded_request_sending = false;
var like_minded_safety_max = 50;
var like_minded_safety_count = 0;
function findNewLikeMinded() {
    if (computing_like_minded) {
        $(".clear_result").fadeOut();
        $(".find_loading").show();

        if (like_minded_request_sending) {       // loop until exceed safety max or return received
            setTimeout(function(){
                like_minded_safety_count += 1;
                if (like_minded_safety_count < like_minded_safety_max) {
                    findNewLikeMinded();
                }
            }, 500);
        }
        like_minded_request_sending = true;

        backgroundAction({
                data: {'action': 'findLikeMinded'},
                success: function(data) {
                    like_minded_request_sending = false;
                    var returned = $.parseJSON(data);

                    var like_minded_header = $(".like_minded_header");
                    // if on like minded page, update stuff visually
                    if (like_minded_header.length != 0) {
                        $(".computing_result").hide();
                        $(".find_loading").hide();
                        var num_new = returned.num_new_members;
                        // change total found
                        var total_num = $(".total_found").data('num');
                        total_num += num_new;
                        $(".total_found").data('num', total_num);
                        $(".total_found").html(total_num);
                        // change total processed
                        var total_processed = parseInt($(".total_processed").text());
                        $(".total_processed").html(total_processed + returned.num_processed);
                        // display num found
                        $('.num_new_found').html(total_num);
                        $('.num_processed').html(total_processed + returned.num_processed);
                        $('.find_result').toggleClass("toggle");
                        $(".find_result").show();
                        // if there were members adjust shit appropriately
                        if (num_new != 0) {
                            $(".no_members").hide();
                            $(".some_members").show();
                            $(".like_minded_members").prepend(returned.html);
                            bindOnNewElements();
                        }
                    }

                    // if not finished, use recursion
                    if (returned.num_processed != 0) {
                        findNewLikeMinded();
                    }
                    else {
                        computing_like_minded = false;
                        var message = String(total_num) + " like-minded people were found on LoveGov";
                        $(".find_result").html(message);
                    }
                }}
        ); // add , true is for analyzing like minded
    }
}

function likeMindedComputing() {
    if (computing_like_minded) {
        $(".find_loading").show();
        $(".computing_result").show();
    }
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
                    $(".total_found").data('num', 0);
                    $(".total_found").html(0);
                    $(".total_processed").html(0);
                    $(".computing_result").show();
                    computing_like_minded = true;
                    findNewLikeMinded();
                }}
        );
    }
});

bind('.find_like_minded' , 'click' , null , function(e)
{
    computing_like_minded = true;
    $(".computing_result").show();
    $(".button_result").hide();
    findNewLikeMinded();
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


bind(".like_minded_x", "click", null, function(e) {
    $(".like_minded_header_dialogue").hide();
});

/***********************************************************************************************************************
 *
 *      ~log news link clicks
 *
 ***********************************************************************************************************************/
bind('.news_link' , 'click' , null , function(e)
{
    var link_redirect = $(this).data("link_redirect");
    window.open(link_redirect);
});


/***********************************************************************************************************************
 *
 *      ~running for elections
 *
 ***********************************************************************************************************************/
bind('.run_for' , 'click' , null , function(e)
{
    var button = $(this);
    var e_id = $(this).data('e_id');
    action({
        data: {'action': 'runForElection', 'e_id':e_id, 'run':1},
        success: function(data) {
            var returned = $.parseJSON(data);
            button.replaceWith(returned.html);
        }
    });
});

bind('.stop_running_for' , 'click' , null , function(e)
{
    var button = $(this);
    var e_id = $(this).data('e_id');
    action({
        data: {'action': 'runForElection', 'e_id':e_id, 'run':0},
        success: function(data) {
            var returned = $.parseJSON(data);
            button.replaceWith(returned.html);
        }
    });
});

bind('.invite_to_run_for' , 'click' , null , function(e)
{
    var e_id = $(this).data('e_id');
    getModal('invite_to_run_for_modal' , { 'e_id': e_id });
});


bind('.invite_to_run_for_button' , 'click' , null , function(e)
{
    $(".success_message").hide();
    var e_id = $(this).data('e_id');
    var invite_email = $(".invite_to_election_email").val();
    action({
        data: {'action': 'inviteToRunForElection', 'e_id':e_id, 'invite_email':invite_email},
        success: function(data) {
            $(".success_message").show();
        }
    });
});


/***********************************************************************************************************************
 *
 *      ~filter feed by location
 *
 ***********************************************************************************************************************/
bind('.filter_by_state_select', 'change', null, function(e) {
    var value = $(this).val();
    if (value != "") {
        $(".filter_by_city").show();
        $("#filter_by_city").focus();
    }
    else {
        $(".filter_by_city").hide();
    }
    var feed = $(this).parents(".feed_main");
    feed.data('state', value);
    refreshFeed(feed);
});

bind(".filter_by_city_input", "keypress", function(e) {
    if(e.keyCode==13) {
        e.preventDefault();
        var value = $(this).val();
        var feed = $(this).parents(".feed_main");
        feed.data('city', value);
        refreshFeed(feed);
    }
});


/***********************************************************************************************************************
 *
 *      ~ add to / invite to scorecard
 *
 ***********************************************************************************************************************/
bind(".add_to_scorecard", "click", function(e) {
    var s_id = $(this).data('s_id');
    getModal('add_to_scorecard_modal' , { 's_id': s_id }, function() {
        $(".add_to_select").select2({
        });
    });
});


bind(".add_to_button", "click", function(e) {
    $(".success_message").hide();
    var s_id = $(this).data('s_id');
    var add_ids = $(".add_to_select").val();
    action({
        'data': {'action':'addToScorecard', 's_id':s_id, 'add_ids':JSON.stringify(add_ids)},
        success: function(data)
        {
            $(".add_success_message").show();
        }
    });
});

bind(".remove_from_scorecard", "click", function(e) {
    var s_id = $(this).data('s_id');
    var p_id = $(this).data('p_id');
    var wrapper = $(this).parents(".scorecard_avatar_strip_wrapper");
    action({
        'data': {'action':'removeFromScorecard', 's_id':s_id, 'p_id':p_id},
        success: function(data)
        {
            wrapper.remove();
        }
    });
});

bind(".invite_to_scorecard_button", "click", function(e) {
    $(".success_message").hide();
    var s_id = $(this).data('s_id');
    var invite_email = $(".invite_to_email").val();
    action({
        'data': {'action':'inviteToScorecard', 's_id':s_id, 'invite_email':invite_email},
        success: function(data)
        {
            $(".add_success_message").show();
        }
    });
});

/* remove scorecard from group */
bind(".group_remove_scorecard", "click", function(e) {
    var g_id = $(this).data('g_id');
    if (confirm("Are you sure you want to remove this group's scorecard?")) {
        action({
            'data': {'action':'removeScorecard', 'g_id':g_id},
            success: function(data)
            {
                alert("scorecard removed.");
                $(this).remove();
            }
        });
    }
});

/***********************************************************************************************************************
 *
 *      ~ Dismissible header stuff
 *
 ***********************************************************************************************************************/
bind(".congress_header_link", "click", function(e) {
    var url = $(this).data('url');
    var warning = $(this).data('warning');
    if (warning == 1) {
        getModal("answer_questions_warning_modal", {"which":"congress_header"});
    }
    else {
        window.location.href = url;
    }
});


bind(".find_reps_header_button", "click", function(e) {
    var zip = $(".reps_zip_input").val();
    action({
            data: {'action': 'submitTempAddress', 'address': "", 'city':"", 'state':"",
                'zip':zip},
            success: function(data) {
                window.location.href = "/representatives/";
            }}
    );
});

/***********************************************************************************************************************
 *
 *      ~ change privacy mode
 *
 ***********************************************************************************************************************/
bind(".change_privacy_mode", "click", function(e) {
    var mode = $(this).data('mode');
    action({
        'data': {'action':'changePrivacyMode', 'mode':mode},
        success: function(data)
        {
            if (mode=="PRI") {
                $(".private_mode_button").hide();
                $(".public_mode_button").show();
            }
            else {
                $(".public_mode_button").hide();
                $(".private_mode_button").show();
            }
        }
    });
});

bind(".privacy_option", "click", function(e) {
    var sibling = $(this).siblings();
    $(this).hide();
    sibling.show();
    var wrapper = $(this).parents(".answer_privacy_wrapper");
    var r_id = wrapper.data("r_id");
    var q_id = wrapper.data("q_id");
    action({
        data: {'action':'changeAnswerPrivacy', 'r_id':r_id, 'q_id':q_id},
        success: function(data) {
        }
    });
});

/***********************************************************************************************************************
 *
 *      ~ first login
 *
 ***********************************************************************************************************************/
bind('.explore_your_feed','click', function() {
    showAllBubbles();
    $(".explore_your_feed").removeClass("incomplete");
    action({
        data: {
            'action': 'completeTask',
            'task': 'E'
        },
        success: function(data) {
        }
    });
});

bind('.click_to_complete_task','click', function() {
    var task = $(this).data("task");
    action({
        data: {
            'action': 'completeTask',
            'task': task
        },
        success: function(data) {
        }
    });
});

bind('.hide_intros','click', function() {
    if (confirm("Are you sure?")) {
        action({
            data: {
                'action': 'completeTask',
                'task': "H"
            },
            success: function(data) {
            }
        });
        $(this).parents(".dismissible_header").hide();
    }
});

function showAllBubbles() {
    $(".helper_bubble").fadeIn(200);
}

function showBubbles() {
    var time = 200;
    setTimeout(function() {
        var bubbles = $(".helper_bubble.bubble_show");
        bubbles.each(function() {
            showBubble($(this), true);
        });
    }, time);
}

bind('.x_helper_bubble','click', function() {
    var helper_bubble = $(this).parents(".helper_bubble");
    hideBubble(helper_bubble, false);
    var task = helper_bubble.data("task");
    if (task!="") {
        action({
            data: {
                'action': 'completeTask',
                'task': task
            },
            success: function(data) {
            }
        });
    }
});

bind('.take_a_tutorial','click', function() {
    var tutorial = $(this).data('tutorial');
    if (tutorial == 'qa') {
        showBubble($(".qa_start_tutorial"), true);
    }
    if (tutorial == 'feed') {
        showBubble($(".feedtut_start_tutorial"), true);
    }
});

bind('.continue_tutorial','click', function() {
    // hide original bubble
    var helper_bubble = $(this).parents(".helper_bubble");
    hideBubble(helper_bubble, true);
    // this is the bubble we're going to show
    var next_classname = $(this).data("next");
    var next_bubble = $("." + next_classname);
    // show bubble
    showBubble(next_bubble, true);
});

function hideBubble(bubble, animate) {
    bubble.removeClass("bubble_show");
    if (animate) {
        bubble.fadeOut();
    }
    else {
        bubble.hide();
    }
}
function showBubble(bubble, animate) {

    // my parent selector
    var my_parent_selector = getValueFromKey(bubble, 'my_parent_selector');
    // if directions, we must append next_bubble to next_parent before we show it
    if (my_parent_selector != "") {
        var my_parent = $(my_parent_selector);
        my_parent.append(bubble);
    }

    // then show bubble
    bubble.addClass("bubble_show");
    if (animate) {
        bubble.fadeIn();
    }
    else {
        bubble.show();
    }
}


bind('.normal_feed_button','click', function() {
    $(".temp_questions_feed").hide();
    $(".normal_feed").show();
    $(".what_would_be_wrapper").hide();
});

bind('.what_would_be_x','click', function() {
    $(".what_would_be_wrapper").hide();
});

bind('.see_congratulations','click', function() {
    action({
        data: {
            'action': 'completeTask',
            'task': "W"
        },
        success: function(data) {
            window.location.href = "/home/";
        }
    });
});

bind('.first_answer_questions','click', function() {
    $('body').animate({
        scrollTop: 470
    }, 1000);
});

/***********************************************************************************************************************
 *
 *      ~ content detail
 *
 ***********************************************************************************************************************/
bind('div.content-admin-actions span.content-admin-action-delete', 'click', function(e) {
    if(confirm("\n\n\n\n\nAre you sure you want to delete this?\n\nAll associated discussions and data will also be deleted.\n\n\n\n\n")) {
        var c_id = $(this).data('c_id');
        action({
            data: {
                'action': 'delete',
                'c_id': c_id,
            },
            success: function(data) {
                var obj = $.parseJSON(data);
                homeReload(obj.url);
            },
        });
    }
});

/***********************************************************************************************************************
 *
 *      ~ groups
 *
 ***********************************************************************************************************************/
bind('.select_party','click', function() {
    var deselect = $(this).hasClass("selected");
    var g_id = $(this).data('g_id');
    $(this).toggleClass("selected");
    if (!deselect) {
        action({
            data: {
                'action': 'joinGroupRequest',
                'g_id':g_id
            },
            success: null
        });
    }
    else {
        action({
            data: {
                'action': 'leaveGroup',
                'g_id':g_id
            },
            success: null
        });
    }
});

bind('div.profile-page div.profile-image', 'click', function(e) {
    var uid=$(this).data('uid');
    getModal('get_full_image_modal', {'uid': uid});
});

/***********************************************************************************************************************
 *
 *     ~ client side analytics
 *
 ***********************************************************************************************************************/

var CLIENT_SIDE_ANALYTICS = true;

var ANALYTICS_DICT = {};
var ANALYTICS_NONCE_ID = 0;

var AJAX_ANALYTICS_ACTIONS = [
    'getFeed',
    'getGroups',
]

function startPageAnalytic(path, action) {
    var nonce_id = -1;
    if (CLIENT_SIDE_ANALYTICS) {
        var now = new Date().getTime();
        var analytics_object = {'path':path, 'action':action, 'start_time':now};
        ANALYTICS_NONCE_ID += 1;
        nonce_id = ANALYTICS_NONCE_ID;
        ANALYTICS_DICT[nonce_id] = analytics_object;
    }
    return nonce_id;
}

function finishPageAnalytic(nonce_id) {
    if (CLIENT_SIDE_ANALYTICS) {
        var now = new Date().getTime();
        var analytics_object = ANALYTICS_DICT[nonce_id];
        if (typeof(analytics_object) != 'undefined') {
            analytics_object.end_time = now;
        }
    }
}

// post client side analytics data to server
function postPageAnalytics() {
    if (CLIENT_SIDE_ANALYTICS) {
        var client_side_data = JSON.stringify(ANALYTICS_DICT);
        ANALYTICS_DICT = {};
        if (client_side_data != "{}") {
            action({
                'data': {'action':'clientSideAnalytics', 'client_side_data':client_side_data, 'log-ignore':true},
                success: function(data)
                {

                }
            });
        }
    }
}


/***********************************************************************************************************************
 *
 *     ~ caching and restoring a page (for back to feed)
 *
 ***********************************************************************************************************************/
function CachedPage(html, page_height, url) {
    this.html = html;
    this.page_height = page_height;
    this.url = url;

    this.restorePage = function () {
        $(".main_content").html(this.html);
        pushURL(this.url);
        bindOnNewElements();
        $(document).scrollTop(this.page_height);
    }
}

var cached_pages = [];
function restoreLastCachedPage() {
    if (cached_pages.length != 0) {
        var last_cached_page = cached_pages.pop();
        last_cached_page.restorePage();
    }
}

function storeCachedPage() {
    var page_html = $(".main_content").html();
    var page_height = $(document).scrollTop();
    var cached_page = new CachedPage(page_html, page_height, PATH);
    cached_pages.push(cached_page);
    if (cached_pages.length > 2) {
        cached_pages.splice(0, 1);
    }
}

function showBackButtonIfCachedPage() {
    if (cached_pages.length != 0) {
        $(".restore_cache").show();
    }
    else {
        $(".restore_cache").hide();
    }
}

bind('.restore_cache', 'click', function(e) {
    restoreLastCachedPage();
});


/***********************************************************************************************************************
 *
 *     ~ login stuff
 *
 ***********************************************************************************************************************/
bind('.request_password_recovery_button', 'click', function(e) {
    var email = $(".request_password_recovery_email").val();
    $(".requested_message").hide();
    $(".requesting_password").show();
    action({
        data: {
            'action': 'requestPasswordRecovery',
            'email': email

        },
        success: function(data) {
            setTimeout(function() {
                $(".requesting_password").hide();
                $(".requested_message").show();
            }, 200);
        }
    });
});


bind('.email_login_button', 'click', function(e) {
    var email = $(".sign_in_email_input").val();
    var password = $(".sign_in_password_input").val();
    var from_page = PATH;
    $(".login_error").hide();
    action({
        data: {
            'action': 'emailLogin',
            'email': email,
            'password':password,
            'from_page':from_page
        },
        success: function(data) {
            $(".signing_in_gif").hide();
            var returned = $.parseJSON(data);
            if (returned.success) {
                window.location.href = returned.go_to_page;
            }
            else {
                $(".login_error").text(returned.error);
                $(".login_error").show();
            }
        }
    });
});

bind('.twitter_register_button', 'click', function(e) {
    var name = $(".twitter_name").val();
    var email = $(".twitter_email").val();
    $(".twitter_registering").show();
    $(".twitter_error").hide();
    action({
        data: {
            'action': 'twitterRegisterPost',
            'email': email,
            'name': name
        },
        success: function(data) {
            $(".twitter_registering").hide();
            var returned = $.parseJSON(data);
            if (returned.success) {
                window.location.href = returned.url;
            }
            else {
                $(".twitter_name_error").text(returned.twitter_name_error);
                $(".twitter_email_error").text(returned.twitter_email_error);
                $(".twitter_general_error").text(returned.twitter_error);
                $(".twitter_error").show();
            }
        }
    });
});

bind('.goto_sign_up', 'click', function(e) {
    var sign_up = $(".sign_up_wrapper");
    var element = sign_up;
    var old_height = element.height();
    element.css("height", "auto");
    var new_height = element.height();
    element.css("height", old_height);
    element.animate({"height":new_height}, {"duration":1000,
        "complete":function(){
            element.css("height", "auto");
            element.css("overflow", "visible");
        }});
});