
/***********************************************************************************************************************
 *
 *     ~Delegated binding function, very similar to jquery's deprecated ".live()"
 *
 ***********************************************************************************************************************/

function bind(selector, events, data, handler) {
    $(document).on(events, selector, data, handler);
}

function action(dict) {
     var data = dict['data'];
     var success_fun = dict['success'];
     var error_fun = function(jqXHR, textStatus, errorThrown) {
         if(jqXHR.status==403) {
             //launch403Modal(jqXHR.responseText);
             return;
         }
         var superError = dict['error'];
         if (superError) {
             superError();
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

    // init home page
    initHomePage();

});

/* does some javascript manipulation of home page */
function initHomePage() {
    var navlink = getNavLink(path);
    selectNavLink(navlink);
    selectRank("H");
    getFeed();
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
                initFocus();
                feed_start=0;
                getFeed();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').html(jqXHR.responseText);
            }
        });
}

/* does js necessary to make focus appear correctly after reload */
function initFocus() {
    // if group info was expanded, expand this as well
    if (info_expanded) {
        expandInfoToggle(false);
    }
    // if parameters were selected, select them
    selectRank(feed_rank);
    $.each(feed_types, function(i, e) {
        selectType(e);
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

function selectRank(rank) {
    var which = $('.rank_button[data-rank="' + rank + '"]');
    $(".rank_button").removeClass("clicked");
    which.addClass("clicked");
    feed_rank = rank;
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
    feed_start=0;
    getFeed();
});

var feed_types = [];
var feed_rank = 'H';
var feed_start = 0;
function getFeed() {
    var replace = (feed_start==0);
    var feed_types_json = JSON.stringify(feed_types);
    var time = 10;
    var feed_timeout = setTimeout(function(){
        $(".feed_fetching").show();
    },time);
    action({
            data: {'action': 'getFeed', 'path': path, 'feed_rank':feed_rank, 'feed_start':feed_start, 'feed_types':feed_types_json},
            success: function(data) {
                var returned = eval('(' + data + ')');
                if (replace) {
                    $(".feed_content").html(returned.html);
                }
                else {
                    $(".feed_content").append(returned.html);
                }
                feed_start += returned.num_items;
                clearTimeout(feed_timeout);
                $(".feed_fetching").hide();
                if (returned.num_items == 0) {
                    $(".load_more").text('you loaded all that there is to load')
                }
            }}
    );
}

/* load more feed items */
bind(".load_more" , "click" , null , function(event) {
    getFeed();
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






















