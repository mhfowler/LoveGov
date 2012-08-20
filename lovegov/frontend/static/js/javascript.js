/***********************************************************************************************************************
 *
 *     ~init js, does stuff that delegated can't!
 *
 ***********************************************************************************************************************/
var rebind;
function bindOnReload() {
    bindOnNewElements();
    switch (rebind) {
        case "home":
            initFeed();
            break;
        case "profile":
            initFeed();
            break;
        case "groupedit":
            loadGroupEdit();
            break;
        case 'questions':
            initFeed();
            break;
        case 'question_detail':
            bindImportanceSliders();
            break;
        case 'poll_detail':
            bindImportanceSliders();
            break;
        case 'browse':
            initFeed();
            break;
    }

}

function undelegated() {
    var undelegated = $('.dummy_link');
    undelegated.bindOnce('click.undelegate', function(event) {
        event.preventDefault();
    });
}

function bindOnNewElements() {
    undelegated();
    loadHoverComparison();
    initHomePage();
    loadHistograms();
    $.each($(".expandable_wrapper"), function(i,e) {
        setInfoHeight($(this));
    });
    bindNotificationsDropdownClickOutside();
    pollAutoSwitch();
}

var poll_autoswitch;
function pollAutoSwitch() {
    clearInterval(poll_autoswitch);
    poll_autoswitch= setInterval(function()
    {
       cyclePollQuestions();
    }, 5000);
}

/***********************************************************************************************************************
 *
 *     ~Delegated binding function, similar to jquery's deprecated ".live()"
 *
 ***********************************************************************************************************************/
function bind(selector, events, data, handler) {
    $(document).on(events, selector, data, handler);
}

function action(dict) {
    var data = dict['data'];
    var success_fun = function(data) {
        var super_success = dict['success'];
        if (super_success) {
            super_success(data);
        }
        undelegated();
    };
    var error_fun = function(jqXHR, textStatus, errorThrown) {
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
    };
    data['url'] = window.location.href;
    $.ajax({
        url: '/action/',
        type: 'POST',
        data: data,
        success: success_fun,
        error: error_fun
    });
}

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

});

/* does some javascript manipulation of home page */
function initHomePage() {
    var navlink = getNavLink(path);
    selectNavLink(navlink);
}

/* does a get request for all feeds on page */
function initFeed() {
    selectRank(feed_rank);
    selectQuestionRank(question_rank);
    $.each(feed_types, function(i, e) {
        selectType(e);
    });
    $.each($(".feed_main"), function(i,e) {
        refreshFeed($(this));
    });
}

/***********************************************************************************************************************
 *
 *      ~Check browser compatibility using Modernizr
 *
 ***********************************************************************************************************************/

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

/***********************************************************************************************************************
 *
 *      ~Bind popovers
 *
 ***********************************************************************************************************************/

bind(".tooltip-top", "tooltip", {'placement': 'top', 'animation': 'true'});
bind(".tooltip-bottom", "tooltip", {'placement': 'bottom', 'animation': 'true'});
bind(".tooltip-right", "tooltip", {'placement': 'right', 'animation': 'true'});
bind(".tooltip-left", "tooltip", {'placement': 'left', 'animation': 'true'});

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
        navSectionToggle(navbar_section, true, true);
        homeReload($(this).attr("href"));
    } else {
        if (navbar_section.hasClass("section_shown")) {
            navSectionToggle(navbar_section, false, true);
        } else {
            navSectionToggle(navbar_section, true, true);
        }
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
    switch (event.which) {
        case 38: change=-1; break;
        case 40: change=1; break;
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
        moveAsterisk(navlink);
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
        navbarlinks.animate({"height":autoHeight}, animation_time);
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

    // If info is hidden, expand the info to it's previous expanded state
    if( info_hidden )
    {   // Set info hidden to false
        wrapper.data('info_hidden', false);
        wrapper.find(".hide_info").text('- minimize info');
        // If the info was un-expanded, show it at un-expanded form
        if( !info_expanded )
        {
            info_div.animate({"height":'100px'}, animation_time);
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
        info_div.animate({"height":'100px'}, animation_time);
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
        info_div.css("height","100px");
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

function homeReload(theurl) {
    $('#search-dropdown').hide();
    $.ajax
        ({
            url:theurl,
            type: 'POST',
            data: {'url':window.location.href},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                History.pushState( {k:1}, "LoveGov: Beta", returned.url);
                path = returned.url;
                $(".home_focus").html(returned.focus_html);
                bindOnNewElements();
                initFeed();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
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

/***********************************************************************************************************************
 *
 *      ~Ajax links
 *
 ***********************************************************************************************************************/
bind(".do_ajax_link", 'click', null, function(event) {
    ajaxReload($(this).attr("href"), true);
});

function ajaxReload(theurl, loadimg)
{
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
                var returned = eval('(' + data + ')');
                History.pushState( {k:1}, "LoveGov: Beta", returned.url);
                if (loadimg) { clearTimeout(timeout); $("#loading").hide(); }
                $('body').css("overflow","scroll");
                $('.main_content').css("top","0px");
                $(".main_content").html(returned.html);
                $('.main_content').show();
                rebind = returned.rebind;
                bindOnReload();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
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
var to_compare_id=null;
function getFeed(container) {
    var feed_start = container.data('feed_start');
    var replace = (feed_start==0);
    if (replace) {
        var old_height = $("body").height();
        $("body").css('min-height', old_height);
        container.find(".feed_content").empty();
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
        var only_unanswered = container.data('only_unanswered');
        if (typeof(only_unanswered) == 'undefined') {
            only_unanswered = false;
        }
        data = {'action': 'getQuestions', 'feed_rank':feed_rank, 'question_rank':question_rank,
            'feed_start':feed_start, 'feed_topic':feed_topic, 'to_compare_id':to_compare_id,
            'only_unanswered':only_unanswered };
    }
    else if (feed == 'getUserActivity')
    {
        var p_id = container.data('p_id');
        data = { 'action': 'getUserActivity', 'feed_start':feed_start, 'p_id':p_id };
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
                    container.find(".load_more").text('you loaded all that there is to load')
                }
                bindImportanceSliders();
                bindOnNewElements();
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
function editUserProfile(info,edit_div)
{
    var prof_data = info;
    prof_data.action = 'editProfile';

    action({
        'data': prof_data,
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            edit_div.text(obj.value);
            edit_div.show();
        }
    });
}


function editContent( c_id , info , edit_div )
{
    var content_data = info;
    content_data.action = 'editContent';
    content_data.c_id = c_id;

    action({
        'data': content_data,

        success: function(data)
        {
            var obj = eval('(' + data + ')');
            edit_div.html(obj.value);
            edit_div.show();
        }
    });
}



bind( ".edit_button" , 'click', null , function(event)
{
    event.preventDefault();
    $(this).siblings('.inline_hide').hide();
    $(this).hide();

    $(this).siblings('.inline_edit').show();
});

bind( ".submit_inline_edit" , 'click' , null , function(event)
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
});

/***********************************************************************************************************************
 *
 *      ~Login
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


/***********************************************************************************************************************
 *
 *      ~Profile
 *
 **********************************************************************************************************************/

bind(".user_unfollow", 'mouseenter', null, function(event) {
    $(this).text('stop');
});
bind(".user_unfollow", 'mouseout', null, function(event) {
    $(this).text('following');
});

bind(".user_unrequest", 'mouseenter', null, function(event) {
    $(this).text('un-request');
});
bind(".user_unrequest", 'mouseout', null, function(event) {
    $(this).text('requested');
});

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
 *      ~Following
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
            }
        }
    );
}

bind( 'div.group_join' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    groupFollow(event,$(this),true,g_id);
});

bind( 'div.group_leave' , 'click' , null , function(event)
{
    var g_id = $(this).data('g_id');
    groupFollow(event,$(this),false,g_id);
});

function groupFollow(event,div,follow,g_id)
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
                var response = returned.response;

                if( response == "joined")
                {
                    div.html("leave group");
                    div.removeClass("group_join");
                    div.addClass("group_leave");
                }
                else if( response == "requested")
                {
                    div.html("un-request group");
                    div.removeClass("group_join");
                    div.addClass("group_leave")
                }
                else if( response == "removed")
                {
                    div.html("join group");
                    div.removeClass("group_leave");
                    div.addClass("group_join")
                }
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
    groupFollowResponse(event,"Y",wrapper);
    wrapper.siblings(".group_request_text").children('.group_request_append_y').fadeIn(600);
});

bind( ".group_response_n" , 'click' , null , function(event)
{
    var wrapper = $(this).parent(".group_request_buttons");
    wrapper.fadeOut(600);
    groupFollowResponse(event,"N",wrapper);
    wrapper.siblings(".group_request_text").children('.group_request_append_n').fadeIn(600);
});

function groupFollowResponse(event,response,div)
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

bind( 'div.modal_overdiv' , 'click' , null , function(event)
{
    event.preventDefault();
    $(this).hide();
    $('div.modal_wrapper').hide();
});

bind( 'div.modal_close' , 'click' , null , function(event)
{
    event.preventDefault();
    $('div.modal_wrapper').hide();
    $('div.modal_overdiv').hide();
});

function getModal(modal_name,data)
{
    if( typeof(data)=='undefined'){ data = { 'modal_name':modal_name }; }
    else{ data['modal_name'] = modal_name; }
    data['action'] = 'getModal';

    action({
        data: data,
        success: function(response_data)
        {
            var returned = eval('(' + response_data + ')');
            $('div.modal_content').html( returned.modal_html );

            var modal_wrapper = $('div.modal_wrapper');

            //Get New Modal Position
            var body_middle = $('body').width()/2;
            var left_offset = modal_wrapper.outerWidth()/2;
            var left_position = body_middle - left_offset;
            modal_wrapper.css('left',left_position);

            modal_wrapper.fadeIn(500);
            $('div.modal_overdiv').fadeIn(500);
        }
    });
}


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

/***********************************************************************************************************************
 *
 *     ~QA
 *
 **********************************************************************************************************************/

bind('.answer_button' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    expandAnswerInterface(stub);
});

function expandAnswerInterface(stub) {
    stub.find(".question_comparison").hide();
    stub.find(".answer_expanded").show();
    stub.find(".answer_button").hide();
}

function expandResponse(stub) {
    stub.find(".answer_expanded").hide();
    stub.find(".question_comparison").show();
}


bind('.answer_checkbox' , 'click' , null , function(event)
{
    if ($(this).hasClass("clicked")) {
        $(this).removeClass("clicked");
    }
    else {
        var stub = $(this).parents(".question_stub");
        stub.find(".answer_checkbox").removeClass("clicked");
        $(this).addClass("clicked");
    }
});

bind('.save_button' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    saveQuestion(stub);
});


function saveQuestion(stub) {
    var box = stub.find(".answer_checkbox.clicked");
    var a_id;
    if (box.length!=0) {
        a_id = box.data('a_id');
    }
    else {
        a_id = -1;
    }
    var explanation = stub.find('.explanation').val();
    var privacy_bool = stub.find(".privacy_checkbox").hasClass("clicked");
    var privacy;
    if (privacy_bool) {
        privacy = 'PRI';
    } else {
        privacy = 'PUB';
    }
    var q_id = stub.data('q_id');
    var weight = stub.find(".importance_bar").slider("value");
    action({
        data: {'action':'stubAnswer', 'q_id':q_id, 'privacy':privacy,
            'explanation':explanation,'a_id':a_id, 'weight':weight,
            'to_compare_id':to_compare_id},
        success: function(data) {
            var returned = eval('(' + data + ')');

            var container = stub.parents(".feed_main");
            var only_unanswered = container.data('only_unanswered');
            if (only_unanswered) {
                stub.hide();
                expandAnswerInterface(stub.next('.question_stub'));
            }
            else {
                var new_element = $(returned.html);
                stub.replaceWith(new_element);
                var saved_message = new_element.find(".saved_message");
                saved_message.show();
                saved_message.fadeOut(5000);
                bindImportanceSlider(new_element.find(".importance_bar"));
            }
            if (rebind=="question_detail" || rebind=='poll_detail') {
                expandResponse(new_element);
            }
            updateMatches();
            updateStats();
        }
    });
}

bind('.privacy_checkbox' , 'click' , null , function(event)
{
    $(this).toggleClass("clicked");
});

bind('.cancel_button' , 'click' , null , function(event)
{
    var stub = $(this).parents(".question_stub");
    stub.find(".answer_expanded").hide();
    stub.find(".answer_button").show();
});

function bindImportanceSliders() {
    var importance_bars = $(".importance_bar");
    $.each(importance_bars, function(i, e) {
        bindImportanceSlider($(this));
    });
}

function bindImportanceSlider(div) {
    var weight = div.data('weight');
    div.slider({'min':0,
        'max':100,
        'step':1,
        'value':weight,
        slide: function(event, ui) {
            var text = ui.value + "%";
            $(this).parents(".importance_wrapper").find(".importance_percent").text(text);
        }
    });
}

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
    action({
        data: data,
        success: function(data) {
            var returned = eval('(' + data + ')');
            var new_element = $(returned.html);
            stats.replaceWith(new_element);
        }
    });
}

bind('.only_unanswered' , 'click' , null , function(event)
{
    $(this).toggleClass("clicked");
    var container = $(this).parents(".feed_main");
    container.data("only_unanswered", $(this).hasClass("clicked"));
    refreshFeed(container);
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
                    updateHistogram(histogram_wrapper, true);
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
 *      ~Friends
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



/***********************************************************************************************************************
 *
 *      ~Facebook Share Modal
 *
 ***********************************************************************************************************************/

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
 *      ~Check browser compatibility using Modernizr
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

