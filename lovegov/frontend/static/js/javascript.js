/***********************************************************************************************************************
 *
 *     ~init js, does stuff that delegated cant!
 *
 ***********************************************************************************************************************/
var rebind="home";
function initJS() {
    undelegated();
    loadHoverComparison();
    switch (rebind) {
        case "home":
            initHomePage();
            initFeed();
            break;
        case "profile":
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
    initJS();

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
        $(this).data('feed_start', 0);
        getFeed($(this));
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
    event.preventDefault();
    if (!$(this).hasClass("clicked")) {
        selectNavLink($(this));
        homeReload($(this).attr("href"));
    }
});

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
    if (navlink) {
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
    var redtriangle = navbar_section.find(".red_triangle");
    var navbarlinks = redtriangle.siblings(".navbar_links_wrapper");
    redtriangle.removeClass("red-triangle-down");
    navbarlinks.animate({"height":'0px'}, animation_time);
    redtriangle.removeClass("clicked");
    // check if currently selected link is in section being hidden
    var current_link = getNavLink(path);
    if (current_link) {
        var current_wrapper = current_link.parents(".navbar_links_wrapper");
        if (current_wrapper.attr("class") == navbarlinks.attr("class")) {
            var to_where = current_link.parents(".navbar_section").find(".section_title");
            moveAsterisk(to_where);
        }
    }
    navbar_section.removeClass("shown");
}
function navSectionShow(navbar_section, animation_time) {
    if (!navbar_section.hasClass("shown")) {
        navbar_section.addClass("shown");
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
    expandInfoToggle(true);
});

var info_expanded = false;
function expandInfoToggle(animate) {
    if (animate) {
        var animation_time = 100;
    } else {
        animation_time = 0;
    }
    var expanded =  $(".home_header_expanded");
    if (expanded.hasClass("expanded")) {
        expanded.animate({"height":'10px'}, animation_time);
        expanded.removeClass("expanded");
        info_expanded = false;
        $(".expand_info").text('+ expand info');
    } else {
        expanded.css('height', 'auto');
        var autoHeight = expanded.height();
        expanded.css('height', '0px');
        expanded.animate({"height":autoHeight}, animation_time);
        expanded.addClass("expanded");
        info_expanded = true;
        $(".expand_info").text('- reduce info');
    }
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
                if (info_expanded) {
                    expandInfoToggle(false);
                }
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
    $('#main_content').hide();
    if (loadimg) { var timeout = setTimeout(function(){$("#loading").show();},1000); }
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
                $('#main_content').css("top","0px");
                $("#main_content").html(returned.html);
                $('#main_content').show();
                initJS();
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
    var outside = $(this).parents(".sign_in_dialogue").length == 0;
    if ((event.target.id != "sign_in_button") && outside) {
        $(".sign_in_dialogue").hide();
    }
});

bind(".sign_in_button", 'click', null, function(event) {
    event.preventDefault();
    $(".sign_in_dialogue").show();
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
    container.data('feed_start', 0);
    getFeed(container);
});

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
    if (feed == 'getFeed') {
        data = {'action': 'getFeed', 'path': path, 'feed_rank':feed_rank, 'feed_start':feed_start, 'feed_types':feed_types_json};
    }
    else {
        data = {'action': 'getQuestions', 'feed_rank':feed_rank, 'question_rank':question_rank,
            'feed_start':feed_start, 'feed_topic':feed_topic, 'to_compare_id':to_compare_id};
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
                feed_start += returned.num_items;
                container.data('feed_start', feed_start);
                clearTimeout(feed_timeout);
                container.find(".feed_fetching").hide();
                if (returned.num_items == 0) {
                    container.find(".load_more").text('you loaded all that there is to load')
                }
                bindImportanceSliders();
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

bind("img.gear", "click", function(e) { 
    $('div.user-menu').fadeToggle(50);
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

bind(".follow_button.following", 'mouseenter', null, function(event) {
    $(this).find('.is_following').hide();
    $(this).find(".stop_following").show();
});
bind(".follow_button.following", 'mouseout', null, function(event) {
    $(this).find(".stop_following").show();
    $(this).find('.is_following').hide();
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
                    div.html("unfollow");
                    div.removeClass('user_follow');
                    div.addClass('user_unfollow');
                }
                else if( response == "requested")
                {
                    div.html("un-request");
                    div.removeClass('user_follow');
                    div.addClass('user_unfollow');
                }
                else if( response == "removed")
                {
                    div.html("follow");
                    div.removeClass('user_unfollow');
                    div.addClass('user_follow');
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

function userFollowResponse(event,response,div)
{
    event.preventDefault();
    var follow_id = div.siblings(".user_follow_id").val();
    ajaxPost({
            data: {
                'action':'followResponseResponse',
                'p_id': follow_id,
                'response': response
            },
            success: function(data)
            {
                return true;
            },
            error: function(error, textStatus, errorThrown)
            {
                $('body').html(error.responseText);
            }
        }
    );
    return false;
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
                //alert(data);
            }

        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('body').html(jqXHR.responseText);
        }

    });
}

function groupInviteResponse(event,response,div)
{
    event.preventDefault();
    var g_id = div.data("g_id");
    ajaxPost({
            data: {
                'action':'groupInviteResponse',
                'g_id': g_id,
                'response': response
            },
            success: function(data)
            {
                //alert(data);
            },
            error: function(error, textStatus, errorThrown)
            {
                $('body').html(error.responseText);
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
 *     ~Group Invite Modal
 *
 **********************************************************************************************************************/

bind( 'div.group_invite_members' , 'click' , null , function(event)
{
    getModal('group_invite_modal');
});


/***********************************************************************************************************************
 *
 *     ~Notifications
 *
 **********************************************************************************************************************/

bind( 'div.notifications_dropdown_button' , 'click' , null , function(event)
{
    $('div.notifications_dropdown').toggle();
});

bind( null , 'click' , null , function(event)
{
    if( !$(event.target).hasClass('notifications_dropdown') &&
        !$(event.target).hasClass('notifications_dropdown_button'))
    {
        $('div.notifications_dropdown').hide();
    }
});


/***********************************************************************************************************************
 *
 *      ~GroupEdit
 *
 **********************************************************************************************************************/
function loadGroupEdit()
{
    bindGroupPrivacyRadio();
    bindScaleRadio();
    bindRemoveAdmin();
    selectPrivacyRadio();
    selectScaleRadio();

    var pencil = $('.group_edit_icon').detach();

    bind( '.group_edit_input' , 'mouseenter' , null , function(event)
    {
        $(this).parent().next().append(pencil);
    });

    bind( '.group_edit_input' , 'mouseout' , null , function(event)
    {
        pencil = pencil.detach();
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

    $('select.admin_select').select2({
        placeholder: "Enter a member,"
    });

    $('select.member_select').select2({
        placeholder: "Enter a member,"
    });
}

loadGroupEdit();

function bindRemoveAdmin()
{
    bind('.remove_admin' , 'click', null , function(e)
    {
        var admin_id = $(this).data('admin_id');
        var admin_name = $(this).data('admin_name');
        var g_id = $('#edit_admin_submit').data('g_id');
        $(this).parents('table.admin_container').fadeOut(600);
        removeAdmin( admin_id , g_id , function(data)
        {
            $('optgroup#add_members_input').append('<option value="' + admin_id + '">' + admin_name + '</option>');
        });
    });

    $('.remove_admin_self' , 'click' , null , function(e)
    {
        var admin_id = $(this).data('admin_id');
        var admin_name = $(this).data('admin_name');
        var g_id = $('#edit_admin_submit').data('g_id');
        $(this).parents('table.admin_container').fadeOut(600);
        removeAdmin( admin_id , g_id , function(data)
        {
            window.location = '/group/' + g_id + '/';
        });
    });
}

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

function bindGroupPrivacyRadio()
{
    bind( "div.group_privacy_radio" , 'click' , null , function(event)
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
    bind( "div.news_scale_radio" , 'click' , null , function(event)
    {
        var prev = $("input:radio.news_scale:checked");
        prev.attr('checked',false);
        prev.parent('.news_scale_radio').removeClass("create-radio-selected");

        $(this).children("input:radio.news_scale").attr('checked',true);
        $(this).addClass("create-radio-selected");
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
    stub.find(".question_comparison").hide();
    stub.find(".answer_expanded").show();
    $(this).hide();
});


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
    var box = stub.find(".answer_checkbox.clicked");
    var a_id;
    if (box.length!=0) {
        a_id = box.data('a_id');
    }
    else {
        a_id = -1;
    }
    var explanation = stub.find('.explanation').val();
    if (explanation=="explain your answer") {
        explanation == "";
    }
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
            'explanation':explanation,'a_id':a_id, 'weight':weight, 'to_compare_id':to_compare_id},
        success: function(data) {
            var returned = eval('(' + data + ')');
            var new_element = $(returned.html);
            stub.replaceWith(new_element);
            var saved_message = new_element.find(".saved_message");
            saved_message.show();
            saved_message.fadeOut(5000);
            bindImportanceSlider(new_element.find(".importance_bar"));
        }
    });
});

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
