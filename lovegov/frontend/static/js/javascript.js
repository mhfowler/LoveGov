
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


// /***********************************************************************************************************************
//  *
//  *      ~Header links
//  *
//  ***********************************************************************************************************************/
// function selectHeaderLink(div) {
//     $(".header_link").removeClass("clicked");
//     div.addClass("clicked");
// }

// bind('reactivate-first-login', 'click', function() {
//         setFirstLoginStage(0, function() {
//             window.location = '/match';
//         });
//     });

// function bindTutorialLink() {
//     $('.reactivate-first-login').bindOnce('click', function() {
//         setFirstLoginStage(0, function() {
//             window.location = '/match';
//         });
//     });
// }

// /***********************************************************************************************************************
//  *
//  *      ~Menu and Icon Display
//  *
//  ***********************************************************************************************************************/
// function loadMenuToggles() {

//     function menuClickoff(menu) {
//         menu.bindOnce("clickoutside.menuoff", function(event) {
//             if (menu.hasClass("hack_workaround")) {
//                 menu.removeClass("hack_workaround");
//             }
//             else {
//                 menu.hide();
//                 menu.parents(".menu_toggle").removeClass("clicked");
//             }
//         });
//     }


//     $(".menu").hide();
//     $(".menu_toggle").click(function(event) {
//         if (!$(this).hasClass("clicked")) {
//             var other_menu_toggles = $(".menu_toggle").not($(this));
//             other_menu_toggles.removeClass("clicked");
//             other_menu_toggles.children(".menu").hide();
//             var menu=$(this).children(".menu");
//             menu.addClass("hack_workaround");
//             menuClickoff(menu);
//         }
//         $(this).children(".menu").toggle();
//     });

//     $(".menu_toggle").hover(
//         function(event) {
//             $(this).children(".triangle-selector").addClass("highlighted");
//         },
//         function(event) {
//             if (!$(this).hasClass("clicked")) {
//                 $(this).children(".triangle-selector").removeClass("highlighted");
//             }
//         }
//     );
//     defaultHoverClick($(".menu_toggle"));
// }

// function defaultHoverClick(div) {
//     div.click(function(event) {
//         defaultClick($(this));
//     });
//     defaultHover(div);
// }

// function defaultHoverClickSingle(div) {
//     div.click(function(event) {
//         defaultClickSingle($(this), div);
//     });
//     defaultHover(div);
// }

// function defaultClickSingle(this_div, all_div) {
//     var already = $(this).hasClass("clicked");
//     all_div.removeClass("clicked");
//     if (!already) {
//         this_div.addClass("clicked");
//     }
// }

// function defaultClick(this_div) {
//     this_div.toggleClass("clicked");
// }

// function defaultHover(all_div) {
//     all_div.hover(
//         function(event) {
//             $(this).addClass("hovered");
//         },
//         function(event) {
//             $(this).removeClass("hovered");
//         }
//     );
// }


// /***********************************************************************************************************************
//  *
//  *      ~Following
//  *
//  ***********************************************************************************************************************/
// /* user follower */
// function userFollow(event,div,follow)
// {
//     event.preventDefault();
//     div.unbind();
//     var action = 'userFollowRequest';
//     if( !follow )
//     {
//         action = 'userFollowStop';
//     }
//     ajaxPost({
//             data: {
//                 'action': action,
//                 'p_id': p_id
//             },
//             success: function(data)
//             {
//                 if( data == "follow success")
//                 {
//                     div.html("unfollow");
//                     div.click(
//                         function(event)
//                         {
//                             userFollow(event,div,false);
//                         }
//                     );
//                 }
//                 else if( data == "follow request")
//                 {
//                     div.html("un-request");
//                     div.click(
//                         function(event)
//                         {
//                             userFollow(event,div,false);
//                         }
//                     );
//                 }
//                 else if( data == "follow removed")
//                 {
//                     div.html("follow");
//                     div.click(
//                         function(event)
//                         {
//                             userFollow(event,div,true);
//                         }
//                     );
//                 }
//                 else
//                 {
//                     //alert(data);
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         }
//     );
// }

// function groupFollow(event,div,follow)
// {
//     event.preventDefault();
//     div.unbind();
//     var action = 'joinGroupRequest';
//     if( !follow )
//     {
//         action = 'leaveGroup';
//     }
//     ajaxPost({
//             data: {
//                 'action': action,
//                 'g_id': g_id
//             },
//             success: function(data)
//             {
//                 if( data == "follow success")
//                 {
//                     div.html("leave");
//                     div.click(
//                         function(event)
//                         {
//                             groupFollow(event,div,false);
//                         }
//                     );
//                 }
//                 else if( data == "follow request")
//                 {
//                     div.html("un-request");
//                     div.click(
//                         function(event)
//                         {
//                             groupFollow(event,div,false);
//                         }
//                     );
//                 }
//                 else if( data == "follow removed")
//                 {
//                     div.html("join");
//                     div.click(
//                         function(event)
//                         {
//                             groupFollow(event,div,true);
//                         }
//                     );
//                 }
//                 else
//                 {
//                     //alert(data);
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         }
//     );
// }

// function userFollowResponse(event,response,div)
// {
//     event.preventDefault();
//     var follow_id = div.siblings(".user_follow_id").val();
//     ajaxPost({
//             data: {
//                 'action':'followResponseResponse',
//                 'p_id': follow_id,
//                 'response': response
//             },
//             success: function(data)
//             {
//                 return true;
//             },
//             error: function(error, textStatus, errorThrown)
//             {
//                 $('body').html(error.responseText);
//             }
//         }
//     );
//     return false;
// }

// function setFollowPrivacy(event,private_follow,div)
// {
//     event.preventDefault();
//     div.unbind();
//     ajaxPost({
//         data: {
//             'action':'followprivacy',
//             'p_id': p_id,
//             'private_follow': private_follow
//         },
//         success: function(data)
//         {
//             if( data == "follow privacy set")
//             {
//                 if( private_follow )
//                 {
//                     div.html("private");
//                     div.click(
//                         function(event)
//                         {
//                             setFollowPrivacy(event,0,$(this));
//                         }
//                     );
//                 }
//                 else
//                 {
//                     div.html("public");
//                     div.click(
//                         function(event)
//                         {
//                             setFollowPrivacy(event,1,$(this));
//                         }
//                     );
//                 }
//             }
//             else
//             {
//                 //alert(data);
//             }

//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $('body').html(jqXHR.responseText);
//         }

//     });
// }

// function groupInviteResponse(event,response,div)
// {
//     event.preventDefault();
//     var g_id = div.data("g_id");
//     ajaxPost({
//             data: {
//                 'action':'groupInviteResponse',
//                 'g_id': g_id,
//                 'response': response
//             },
//             success: function(data)
//             {
//                 //alert(data);
//             },
//             error: function(error, textStatus, errorThrown)
//             {
//                 $('body').html(error.responseText);
//             }
//         }
//     );
// }


// /***********************************************************************************************************************
//  *
//  *      ~InlineEdits
//  *
//  ***********************************************************************************************************************/
// function editUserProfile(info,edit_div)
// {
//     var prof_data = info;
//     prof_data.action = 'editProfile';

//     ajaxPost({
//         'data': prof_data,
//         success: function(data)
//         {
//             var obj = eval('(' + data + ')');
//             if( obj.success )
//             {
//                 edit_div.text(obj.value);
//                 edit_div.show();
//             }
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $('body').html(jqXHR.responseText);
//         }
//     });
// }


// function editContent(c_id,info,edit_div)
// {
//     var content_data = info;
//     content_data.action = 'editContent';
//     content_data.c_id = c_id;

//     ajaxPost({
//         'data': content_data,

//         success: function(data)
//         {
//             var obj = eval('(' + data + ')');
//             if( obj.success )
//             {
//                 edit_div.html(obj.value);
//                 edit_div.show();
//             }
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $('body').html(jqXHR.responseText);
//         }
//     });
// }

// function unbindInlineEdits()
// {
//     $(".edit_button").unbind();
//     $(".submit_inline_edit").unbind();
//     $(".cancel_inline_edit").unbind();
// }

// function bindInlineEdits()
// {
//     $(".edit_button").bindOnce('click.edit',
//         function(event)
//         {
//             event.preventDefault();
//             $(this).siblings('.inline_hide').hide();
//             $(this).hide();

//             $(this).siblings('.inline_edit').show();
//         }
//     );

//     $(".submit_inline_edit").bindOnce('click.edit',
//         function(event)
//         {
//             event.preventDefault();
//             var input = $(this).siblings('.edit_input');
//             var wrapper = $(this).parent();
//             var name = input.attr('name');
//             var value = input.val();
//             var model = wrapper.data('model');
//             var info = {
//                 'key':name,
//                 'val':value
//             };
//             var edit_div = $(this).parent().siblings('.inline_hide');

//             if( model == "Content" )
//             {
//                 var c_id = wrapper.data('id');
//                 editContent(c_id,info,edit_div);
//             }
//             else if( model == "UserProfile")
//             {
//                 editUserProfile(info,edit_div);
//             }

//             $(this).parent().siblings('.edit_button').show();
//             $(this).parent().hide();
//         }
//     );

//     $(".cancel_inline_edit").bindOnce("click.edit",
//         function(event)
//         {
//             event.preventDefault();
//             var wrapper = $(this).parent();
//             wrapper.hide();
//             wrapper.siblings('.inline_hide').show();
//             wrapper.siblings('.edit_button').show();
//         }
//     );
// }


// /***********************************************************************************************************************
//  *
//  *      ~General
//  *
//  ***********************************************************************************************************************/
// function loadHoverComparison()
// {

//     var hoverTimer;
//     var hoverClearOK = true;

//     function clearHover()
//     {
//         if( hoverClearOK )
//         {
//             $('#comparison-hover-div p').empty();
//             $('#comparison-hover').empty();
//             $('#comparison-hover-div').fadeOut(300);
//         }
//     }

//     $('#comparison-hover-div').hover
//         (
//             function() { hoverClearOK = false; },
//             function()
//             {
//                 hoverClearOK = true;
//                 hoverTimer = setTimeout
//                     (
//                         function() { clearHover(); },
//                         300
//                     );
//             }
//         );

//     function findHoverPosition(selector)
//     {
//         var top = selector.offset().top - $('#comparison-hover-div').height() - 30;
//         if (top <= $(document).scrollTop())
//         {
//             // show below
//             top = selector.offset().top + selector.height() + 30;
//             $('#comparison-hover-pointer-up').show(); $('#comparison-hover-pointer-down').hide();
//         }
//         else
//         {
//             // show above
//             $('#comparison-hover-pointer-up').hide(); $('#comparison-hover-pointer-down').show();
//         }
//         var left = selector.offset().left - ($('#comparison-hover-div').width()/2) + (selector.width()/2);
//         return {top:top,left:left};
//     }

//     var to_hover = $('.has_hover_comparison').not('.already_hover');
//     to_hover.addClass('already_hover');
//     to_hover.hoverIntent
//         (
//             function(event)
//             {
//                 var self = $(this);
//                 var href = $(this).data('href');
//                 var displayName = $(this).data("display_name");
//                 if (href != "")
//                 {
//                     clearTimeout(hoverTimer);
//                     $('#comparison-hover').empty();
//                     $('#comparison-hover-div p').text('You & ' + displayName);
//                     var offset = findHoverPosition(self);
//                     $('#comparison-hover-loading-img').show();
//                     $('#comparison-hover-div').fadeIn(100);
//                     $('#comparison-hover-div').offset(offset);
//                     ajaxPost({
//                         'data': {'action':'hoverComparison','href':href},
//                         'success': function(data)
//                         {
//                             var obj = eval('(' + data + ')');
//                             $('#comparison-hover-loading-img').hide();
//                             $('#comparison-hover').visualComparison(obj,true);
//                         },
//                         'error': function(jqXHR, textStatus, errorThrown)
//                         {
//                             $('#comparison-hover-div p').text('Sorry there was an error');
//                         }
//                     });
//                 }
//             },
//             function(event)
//             {
//                 hoverTimer = setTimeout
//                     (
//                         function(){ clearHover(); },
//                         1000
//                     );
//             }
//         );
// }



// // loads topic bar select functionality
// function loadTopicSelect()
// {
//     // hide all selected
//     $(".selected").hide();

//     // hover
//     $(".topic-img").hover
//         (
//             function(event)
//             {
//                 var wrapper = $(this).parents(".topic-icon-wrapper");
//                 wrapper.children(".normal").hide();
//                 wrapper.children(".selected").show();
//             },
//             function(event)
//             {
//                 var wrapper = $(this).parents(".topic-icon-wrapper");
//                 if (!(wrapper.hasClass("chosen")))
//                 {
//                     wrapper.children(".selected").hide();
//                     wrapper.children(".normal").show();
//                 }
//             }
//         );
// }

// // selects a particular topic icon and deselects all others
// function selectTopicSingle(wrapper)
// {
//     var icons_wrapper = wrapper.closest(".topic-icons-wrapper");
//     clearTopicIcons(icons_wrapper);
//     showTopicIcon(wrapper);
// }

// function toggleTopicSingle(wrapper) {
//     var deselect = wrapper.hasClass("chosen");
//     var icons_wrapper = wrapper.closest(".topic-icons-wrapper");
//     clearTopicIcons(icons_wrapper);
//     if (!deselect) {
//         showTopicIcon(wrapper);
//     }
// }

// // clears all topic icons within an overall topic-icons-wrapper
// function clearTopicIcons(icons_wrapper) {
//     var icons = icons_wrapper.find(".topic-icon-wrapper");
//     icons.each(function(index) {
//         hideTopicIcon($(this));
//     });
// }

// // toggles topic icon between being selected and unselected
// function toggleTopicIcon(wrapper)
// {
//     if (wrapper.hasClass("chosen")) {
//         hideTopicIcon(wrapper);
//     }
//     else {
//         showTopicIcon(wrapper);
//     }
// }

// function hideTopicIcon(wrapper) {
//     wrapper.removeClass("chosen");
//     wrapper.children(".selected").hide();
//     wrapper.children(".normal").show();
// }

// function showTopicIcon(wrapper) {
//     wrapper.addClass("chosen");
//     wrapper.children(".selected").show();
//     wrapper.children(".normal").hide();
// }


// function loadAjaxifyAnchors()
// {
//     var ajaxClicked = function(event) {
//         var elem = event.target;
//         var href = $(elem).attr('href');
//         if (
//             href != undefined &&
//                 href != "" &&
//                 href.indexOf("http://") == -1 &&
//                 href != "#")
//         {
//             event.preventDefault();
//             $('#comparison-hover').empty();
//             $('#comparison-hover-div').hide();
//             ajaxLink($(elem), true);
//             return false;
//         }
//     };
//     $('.do-ajax-link').bindOnce('click.ajax',  ajaxClicked);
// }
// /***********************************************************************************************************************
//  *
//  *      ~DocumentReady
//  *
//  ***********************************************************************************************************************/
// $(document).ready(function()
// {
//     // csrf protect
//     $.ajaxSetup({ data: {csrfmiddlewaretoken: csrf} });

//     // check browser compatability
//     checkCompatability();

//     // Prepare
//     var History = window.History; // Note: We are using a capital H instead of a lower h
//     if ( !History.enabled )
//     {
//         // History.js is disabled for this browser.
//         // This is because we can optionally choose to support HTML4 browsers or not.
//         return false;
//     }
//     // Bind to StateChange Event
//     History.Adapter.bind(window,'statechange',function()
//     {
//         // Note: We are using statechange instead of popstate
//         var State = History.getState(); // Note: We are using History.getState() instead of event.state
//         History.log(State.data, State.title, State.url);
//     });

//     // back button reload
//     window.onpopstate = function(event)
//     {
//         if (event.state != null) { window.location.reload(); }
//     };

//     if (pageTitle != "")
//     {
//         document.title = pageTitle;
//     }

//     // page specific bindings
//     rebindFunction()
// });


// var page_auto_update;
// function rebindUniversalFrame()
// {
//     loadHeader();
//     loadLeftSidebar();

//     // check notifications on interval
//     clearInterval(page_auto_update);
//     page_auto_update = setInterval(updatePage, 10000);
// }



// // wrapper for ajax post
// function ajaxPost(dict) {
//     var data = dict['data'];
//     var success_fun = dict['success'];
//     var error_fun = function(jqXHR, textStatus, errorThrown) {
//         if(jqXHR.status==403) {
//             launch403Modal(jqXHR.responseText);
//             return;
//         }
//         var superError = dict['error'];
//         if (superError) {
//             superError()
//         } else {
//             $("body").html(jqXHR.responseText);
//         }
//     };
//     data['url'] = window.location.href;
//     $.ajax({
//         url:'/action/',
//         type: 'POST',
//         data: data,
//         success: success_fun,
//         error: function(jqXHR, textStatus, errorThrown) {
//             error_fun(jqXHR, textStatus, errorThrown);
//         }
//     });
// }

// function launch403Modal(msg) {
//     launchModal('<h2> You\'re not allowed to do that </h2>' +
//         '<p style="font-size:16px;color:black;"> until you ' +
//         '<a href="/login">sign in or register! </a> </p> ');
// }


// function launchModal(content) {
//     $('div.overdiv').show();
//     var modal = $('div.modal');
//     modal.children("#general_modal_content").html(content);
//     var width = modal.outerWidth();
//     var height = modal.outerHeight();
//     modal
//         .css("margin-top", -height/2)
//         .css("margin-left", -width/2)
//         .css("display", "inline-block");
//     bindCloseClick(modal);
//     return modal;
// }

// function launchAModal(modal) {
//     $('div.overdiv').show();
//     var width = modal.outerWidth();
//     var height = modal.outerHeight();
//     modal
//         .css("margin-top", -height/2)
//         .css("margin-left", -width/2)
//         .css("display", "inline-block");
//     bindCloseClick(modal);
//     return modal;
// }

// function launchFirstLoginModal(content) {
//     var modal = $('.first-login-modal');
//     modal.children('div.first-login-content').html(content);
//     var width = modal.outerWidth();
//     var height = modal.outerHeight();
//     modal
//         .css("margin-top", -height/2)
//         .css("margin-left", -width/2);
//     setTimeout(function() {modal.fadeIn(1500)}, 1500);
// }



// // Binds an overdiv click to hide a particular element
// // Unbinds when the click occurs
// function bindCloseClick(element) {
//     var overdiv = $('div.overdiv');
//     overdiv.bindOnce('click', function(e) {
//         element.hide();
//         overdiv.hide();
//         overdiv.off('click');
//     });

//     element.find('.general_modal_close').bindOnce('click.general_close' , function(e) {
//         element.hide();
//         overdiv.hide();
//         overdiv.off('click');
//     });
// }


// // ajax load home page
// function ajaxReload(theurl, loadimg)
// {
//     $('#search-dropdown').hide();
//     $('#main-content').hide();
//     if (loadimg) { var timeout = setTimeout(function(){$("#loading").show();},1000); }
//     $.ajax
//         ({
//             url:theurl,
//             type: 'GET',
//             data: {'url':window.location.href},
//             success: function(data)
//             {
//                 var returned = eval('(' + data + ')');
//                 History.pushState( {k:1}, "LoveGov: Beta", returned.url);
//                 if (loadimg) { clearTimeout(timeout); $("#loading").hide(); }
//                 replaceCenter(returned.html);
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
// }

// // for ajax loading of pages - this function only changes content in center of page
// function replaceCenter(stuff)
// {
//     $('body').css("overflow","scroll");
//     $('#main-content').css("top","0px");
//     $("#main-content").html(stuff);
//     $('#main-content').show();
//     rebindFunction();
// }




// /***********************************************************************************************************************
//  *
//  *     ~Header
//  *
//  **********************************************************************************************************************/
// function loadHeader()
// {

//     var timeout;
//     var delay = 750;
//     var isLoading = false;
//     var currentSearch;
//     $('#searchbar').bind('keyup',function()
//     {
//         var text = $(this).val();
//         if (timeout) { clearTimeout(timeout); }
//         if (!isLoading && text != currentSearch)
//         {
//             timeout = setTimeout(function()
//             {
//                 isLoading = true;
//                 $("#autocomplete-loading-gif").show();
//                 ajaxPost({
//                     data: {'action':'searchAutoComplete','string':text},
//                     success: function(data)
//                     {
//                         var obj = eval('(' + data + ')');
//                         $("#autocomplete-loading-gif").hide();
//                         $('#search-dropdown').html(obj.html);
//                         $('#search-dropdown').fadeIn('fast');
//                     },
//                     error: function(jqXHR, textStatus, errorThrown)
//                     {
//                         $("#autocomplete-loading-gif").hide();
//                         $('#search-dropdown').empty();
//                         $('#search-dropdown').hide();
//                     }
//                 });
//                 // Simulate a real ajax call
//                 setTimeout(function() { isLoading = false; }, delay);
//             }, delay);
//         }
//     });

//     $('#search-dropdown').bind('clickoutside',function(event)
//     {
//         if (event.target.id != 'searchbar')
//         {
//             $(this).empty();
//             $(this).hide();
//         }
//     });


//     var tempDropDownDiv = $('.notifications-dropdown-static-div');
//     $('#notifications-dropdown-button').click(
//         function(event)
//         {
//             var dropdown = $('#notifications-dropdown');
//             dropdown.empty().append(tempDropDownDiv);
//             $('.notifications-ajax-load').show();
//             event.preventDefault();
//             var pos = $(this).offset();
//             dropdown.toggle();

//             if( $('#notifications-dropdown').is(':visible') )
//             {
//                 pos.left = (pos.left-dropdown.width()/2)+($(this).width()/2);
//                 pos.top = dropdown.offset().top;
//                 $('#notifications-dropdown').offset(pos);
//                 ajaxPost({
//                     'data': {'action':'getNotifications',
//                         'dropdown':'true'},
//                     success: function(data)
//                     {
//                         var obj = eval('(' + data + ')');
//                         $('.notifications-ajax-load').hide();
//                         $('#notifications-dropdown').empty().append(tempDropDownDiv).append(obj.html);
//                         unbindNotification();
//                         loadNotification();
//                         loadAjaxifyAnchors();
//                         $("#notifications-number-text").text(obj.num_still_new);
//                     },
//                     error: function(jqXHR, textStatus, errorThrown)
//                     {
//                         $('body').html(jqXHR.responseText);
//                     }
//                 });
//             }
//             event.stopPropagation();
//             hideOtherDropDowns(dropdown);
//         }
//     );

//     function hideOtherDropDowns(exclude)
//     {
//         $('.drop_down').each(function()
//         {
//             if (!$(this).is(exclude))
//             {
//                 $(this).hide();
//             }
//         });
//     }

//     $('#notifications-dropdown').bind('clickoutside',function(event)
//     {
//         if ($('#notifications-dropdown').css("display") != "none")
//         {
//             $('#notifications-dropdown').empty().append(tempDropDownDiv);
//             $(this).hide();
//         }
//     });

//     $('#logo-link').hover
//         (
//             function(){ $(this).attr('src', STATIC_URL + '/images/top-logo-hover.png'); },
//             function(){ $(this).attr('src', STATIC_URL + '/images/top-logo-default.png'); }
//         );

//     function toggleUserMenu()
//     {
//         $('.user-menu').toggleClass("user-menu-unselected");
//         $('.user-menu').toggleClass("user-menu-selected");
//         $("#user-menu-dropdown").toggle('slide',{direction:'up'},10);
//         hideOtherDropDowns($('#user-menu-dropdown'));
//         var left = $('#user-menu-dropdown').width()-$('.user-menu').width()+$('.user-img').width()+$('#user-name').width()/2-$('.user-menu-pointer').width()/2;
//         $('.user-menu-pointer').css('left',left);
//     }

//     $('#user-menu-dropdown').bind("clickoutside",function(event)
//     {
//         if ($('#user-menu-dropdown').css('display') != 'none')
//         {
//             $('#user-menu').removeClass("user-menu-selected");
//             $('#user-menu').addClass("user-menu-unselected");
//             $('#user-menu-dropdown').hide();
//         }
//     });

//     $('.user_menu_dropdown').click(function(event)
//     {
//         toggleUserMenu();
//         event.stopPropagation();
//     });

//     var pubMessage = "You are in PUBLIC mode. Comments and content you create while in this mode will be attributed to you. Click to change to Anonymous mode.";
//     var priMessage = "You are in ANONYMOUS mode. Comments and content you create while in this mode will be attributed to \"Anonymous\". Click to change to Public mode.";


//     if ($.cookie('privacy'))
//     {
//         switch($.cookie('privacy'))
//         {
//             case "PUB":
//                 $.cookie('privacy','PUB', {path:'/'});
//                 $(".security_setting").each(function()
//                 {
//                     if ($(this).is('img')) { $(this).attr("src",STATIC_URL + "/images/public.png") }
//                     $(this).attr('data-original-title',pubMessage);
//                 });
//                 break;
//             case "PRI":
//                 $.cookie('privacy','PRI', {path:'/'});
//                 $(".security_setting").each(function()
//                 {
//                     if ($(this).is('img'))
//                     {
//                         $(this).attr("src",STATIC_URL + "/images/user-menu/lockgray.png") ;
//                         $(this).attr('data-original-title',priMessage);
//                     }
//                 });
//                 break;
//         }
//     }
//     else
//     {
//         $.cookie('privacy','PUB', {path:'/'});
//         $(".security_setting").each(function()
//         {
//             if ($(this).is('img'))
//             {
//                 $(this).attr("src",STATIC_URL + "/images/public.png");
//                 $(this).attr('data-original-title',pubMessage);
//             }

//         });
//     }


//     $(".security_setting").each(function(event)
//     {
//         if (!$(this).hasClass("has_security_setting"))
//         {
//             $(this).bind("click", function()
//             {
//                 switch($.cookie('privacy'))
//                 {
//                     case "PUB":
//                         $.cookie('privacy','PRI', {path:'/'});
//                         $(".security_setting").each(function()
//                         {
//                             if ($(this).is('img'))
//                             {
//                                 $(this).attr("src",STATIC_URL + "/images/user-menu/lockgray.png");
//                                 $(this).attr('data-original-title',priMessage);
//                             }
//                         });
//                         break;
//                     case "PRI":
//                         $.cookie('privacy','PUB', {path:'/'});
//                         $(".security_setting").each(function()
//                         {
//                             if ($(this).is('img')) { $(this).attr("src",STATIC_URL + "/images/public.png");
//                                 $(this).attr('data-original-title',pubMessage);}
//                         });
//                         break;
//                 }
//             });

//             $(this).addClass("has_security_setting");
//         }
//     });

//     // header links
//     $(".header_link").bindOnce('click.header', function(event) {
//         selectHeaderLink($(this));
//     });

// }

// /***********************************************************************************************************************
//  *
//  *     ~LeftSidebar
//  *
//  **********************************************************************************************************************/
// var regUrl = /^(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;

// function convert(str)
// {
//     str = str.replace(/&amp;/g, "&");
//     str = str.replace(/&gt;/g,">");
//     str = str.replace(/&lt;/g,"<");
//     str = str.replace(/&quot;/g,'"');
//     str = str.replace(/&#039;/g,"'");
//     return str;
// }

// function closeLeftSideWrapper(wrapper)
// {

//     if (wrapper.hasClass('create-wrapper-large')) { wrapper.animate({left:'-603px'},500); }
//     else { wrapper.animate({left:'-493px'},500); }
//     setTimeout(function()
//     {
//         wrapper.css({'z-index':'100'});
//         wrapper.children('.create' +
//             'e-img').css({'z-index':'101'});
//     },500);

//     wrapper.removeClass('clicked');
// }

// function leftSideToggle(wrapper)
// {
//     if (wrapper.hasClass('clicked'))
//     {
//         closeLeftSideWrapper(wrapper);
//     }
//     else
//     {
//         wrapper.addClass('clicked');
//         wrapper.css({'z-index':'101'});
//         wrapper.children('.create-img').css({'z-index':'102'});
//         wrapper.animate({left:'-1px'},500);

//         wrapper.bindOnce('clickoutside',function(event)
//         {
//             if (event.target.className != "footer_button") {
//                 closeLeftSideWrapper(wrapper);
//             }
//         });
//     }

// }


// function loadLeftSidebar()
// {

//     $('.left-side-img').click(function()
//     {
//         var parent = $(this).parent();
//         leftSideToggle(parent);
//     });



//     $('#feedback-submit').click(function(event)
//     {
//         event.preventDefault();
//         var text = $('#feedback-text').val();
//         var name = $('#feedback-name').val();
//         ajaxPost({


//             data: {'action':'feedback','text':text,'path':path,'name':name},
//             success: function(data)
//             {
//                 $('#feedback-name').val("");
//                 $('#feedback-text').val("");
//                 $('#feedback-response').css('display','block');
//                 $('#feedback-response').fadeOut(3000);
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 //alert("failure");
//             }
//         });
//     });

//     function sendInvitation(event)
//     {
//         event.preventDefault();
//         var email = $("#email-input").val();
//         $("#invite-return-message").text("");
//         $("#invite-return-loading-img").show();
//         ajaxPost({
//             data: {'action':'invite','email':email},
//             success: function(data)
//             {
//                 $("#invite-return-loading-img").hide();
//                 $("#invite-return-message").text("Invitation Sent!");
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $("#invite-return-loading-img").hide();
//                 $("#invite-return-message").text("Server Error, Did Not Send.");
//             }
//         });
//     }


//     $('#email-input').keydown(function(event)
//     {
//         if (event.keyCode == 13)
//         {
//             sendInvitation(event);
//         }
//     });

//     $("#invite-button").click(function(event)
//     {
//         sendInvitation(event);
//     });
// }

// /***********************************************************************************************************************
//  *
//  *     ~Share Button
//  *
//  **********************************************************************************************************************/
// function loadShareButton() {
//     $('div.overdiv').appendTo('body');
//     $('div.shareModal').appendTo('body');

//     $('.share_button').bindOnce('click.share', function(event) {
//         event.preventDefault();
//         var share_id = $(this).data('share_id');
//         $("#share_id").data('share_id', share_id);
//         $('div.overdiv').fadeToggle("fast");
//         $('div.shareModal').fadeToggle("fast");
//     });

//     $('div.overdiv').bindOnce('click.hide_overdiv', function() {
//         $('div.overdiv').hide();
//         $('div.shareModal').hide();
//     });

//     $('div.share_modal_close').bindOnce('click.hide_overdiv', function() {
//         $('div.overdiv').hide();
//         $('div.shareModal').hide();
//     });
// }

// /***********************************************************************************************************************
//  *
//  *     ~Invite Button
//  *
//  **********************************************************************************************************************/
// function loadInviteButton() {
//     $('#group_invite_button').bindOnce('click.group_invite', function(event) {
//         event.preventDefault();
//         $('div.overdiv').fadeToggle("fast");
//         $('div.invite_modal').fadeToggle("fast");
//     });

//     $('div.overdiv').bindOnce('click.hide_overdiv', function() {
//         $('div.overdiv').hide();
//         $('div.invite_modal').hide();
//     });

//     $('div.invite_modal_close').bindOnce('click.hide_overdiv', function() {
//         $('div.overdiv').hide();
//         $('div.invite_modal').hide();
//     });

//     $('#invite_submit_content').bindOnce('click.invite_submit', (function(e) {
//         e.preventDefault();
//         var g_id = $("#group_invite_button").data('g_id');
//         var invitees = $('.invite_select').select2("val");
//         if (invitees!='') {
//             ajaxPost({
//                 data: {'action': 'groupInvite', 'invitees': JSON.stringify(invitees), 'g_id':g_id},
//                 success: function(data)
//                 {
//                     $('#invite_submit_message').html('Invite Sent!');
//                     $('#invite_submit_message').fadeIn(200);
//                     window.setTimeout("$('div.overdiv').fadeOut(600); $('div.invite_modal').fadeOut(600);",1000);
//                 }
//             });
//         }
//     }) );
// }
// /***********************************************************************************************************************
//  *
//  *     ~RightSidebar
//  *
//  **********************************************************************************************************************/
// var right_sidebar_topic = 'all';

// function loadRightSideBar()
// {
//     // select topic click function
//     $(".q-topic-img").click(function(event) {
//         var wrapper = $(this).parents(".topic-icon-wrapper");
//         toggleTopicSingle(wrapper);
//         toggleQuestionTopic($(this));
//     });

//     // sidebar stuff, for question-topic select
//     $(".topic-div").hide();

//     // if page has a topic then show questions of that topic
//     if (right_sidebar_topic!='all')
//     {
//         var alias_div = $('input[value="' + right_sidebar_topic + '"]');
//         selectQuestionTopic(alias_div.siblings(".normal"));
//     }
//     // else show questions of all topics
//     else
//     {
//         $("#topic-all").show();
//     }

//     // hides all other topic divs, and shows random topic div
//     $("#all-topics-button").click(function(event) {
//         var wrapper =  $(".q-topics-wrapper");
//         wrapper.find(".selected").hide();
//         wrapper.find(".normal").show();
//         $(".topic-div").hide();
//         $("#topic-all").show();
//         topics=[];

//     });
// }

// // shows questions from the selected topic and calls select topic to adjust icons appropriately
// function selectQuestionTopic(div)
// {
//     var t = div.siblings(".t-alias").val();
//     $(".topic-div").hide();
//     var topic_div = $("#topic-"+t);
//     topic_div.fadeIn();
//     topic_div.addClass("chosen");
// }

// // shows questions from the selected topic and calls select topic to adjust icons appropriately
// function toggleQuestionTopic(div)
// {
//     var t = div.siblings(".t-alias").val();
//     $(".topic-div").hide();
//     var topic_div = $("#topic-"+t);
//     if (topic_div.hasClass("chosen")) {
//         topic_div.removeClass("chosen");
//         $("#topic-all").fadeIn();
//     }
//     else {
//         topic_div.addClass("chosen");
//         topic_div.fadeIn();
//     }
// }



// /***********************************************************************************************************************
//  *
//  *      ~Question
//  *
//  ***********************************************************************************************************************/
// function loadQuestion()
// {
//     // submit answer
//     $("#submitquestion").bindOnce("click.submitanswer", function(event)
//     {
//         event.preventDefault();
//         var checked = false;
//         $('.answer-container').find('input').each(function()
//         {
//             if ($(this).prop("checked"))
//             {
//                 checked = true;
//             }
//         });

//         $("#questionform").submit();

//     });

//     // answer select
//     $('.answer-container').find('input').each(function()
//     {
//         if ($(this).prop("checked"))
//         {
//             $(this).parent().parent().addClass("answer-container-selected");
//         }
//     });

//     $('.answer-container').hover
//         (
//             function()
//             {
//                 $(this).addClass("answer-container-hover");
//             },
//             function()
//             {
//                 $(this).removeClass("answer-container-hover");
//             }
//         );

//     // answer click
//     $('input').bindOnce("click.answer", function(event)
//     {
//         event.preventDefault();
//     });

//     $('.answer-container').bindOnce("click.answercontainer", function()
//     {
//         $('.answer-container').removeClass("answer-container-selected");

//         if ($(this).find('input').prop('checked'))
//         {
//             $(this).find('input').prop("checked", false);
//             $(this).removeClass("answer-container-selected");
//             $(this).removeClass("answer-container-hover");
//         }
//         else
//         {
//             $(this).find('input').prop("checked", true);
//             $(this).addClass("answer-container-selected");
//         }

//         submitAnswer();
//     });
// }

// function submitAnswer()
// {
//     var choice = $('input:radio[name=choice]:checked').val();
//     var q_id = c_id;
//     var explanation = "";
//     var weight = 5;
//     // var exp = $("#explanation").val();
//     ajaxPost({
//         data: {'action':'answer','q_id': q_id,'choice':choice,'weight':weight,'explanation':explanation},
//         success: function(data) {
//         },
//         error: function(jqXHR, textStatus, errorThrown){
//             $('.errors_div').html(jqXHR.responseText);
//         }
//     });
// }

// /***********************************************************************************************************************
//  *
//  *      ~Thread
//  *
//  ***********************************************************************************************************************/
// // binding for thread
// function loadThread()
// {
//     bindInlineEdits();
//     heartButtons();
//     bindTooltips();

//     $(".submit-comment").bindOnce("click.submitcomment",function(event)
//     {
//         event.preventDefault();
//         $(this).parent().submit();
//     });

//     // increment number of comments
//     function incNumComments() {
//         var ncspan = $('span.num_comments');
//         var num_comments = parseInt(ncspan.text());
//         ncspan.text(num_comments + 1);
//     }

//     $("#commentform").bindOnce("submit.comment",function(event)
//     {
//         event.preventDefault();
//         var comment_text = $(this).children(".comment-textarea").val();
//         var comment_text_length = comment_text.length;
//         if (comment_text_length <= 10000)
//         {
//             $(this).children(".comment-textarea").val("");
//             var content_id = $("#content_id").val();
//             ajaxPost({
//                 'data': {'action':'comment','c_id': content_id,'comment':comment_text},
//                 'success': function(data) {
//                     ajaxThread();
//                     incNumComments();
//                 },
//                 'error': null
//             });
//         }
//         else
//         {
//             alert("Please limit your response to 10,000 characters.  You have currently typed " + comment_text_length + " characters.");
//         }
//     });

//     // toggle reply form for comment
//     $(".reply").bindOnce("click.reply",function()
//     {
//         $(this).parent().siblings('.replyform').toggle();
//     });

//     // hide for "cancel" button
//     $("input.tab-button.alt").click(function()
//     {
//         $(this).parent().hide();
//     });

//     // delete comment


//     // like comment
//     $(".commentlike").bindOnce("click.like",function(event)
//     {
//         event.preventDefault();
//         var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//         $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
//             function(data)
//             {
//                 ajaxThread();
//             });
//     });

//     // dislike comment
//     $(".commentdislike").bindOnce("click.dislike",function(event)
//     {
//         event.preventDefault();
//         var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//         $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
//             function(data)
//             {
//                 ajaxThread();
//             });
//     });

//     // delete comment
//     $(".commentdelete").bindOnce("click.delete",function()
//     {
//         var content_id = $(this).children(".delete_id").val();
//         $.post('/action/', {'action':'delete','c_id':content_id},
//             function(data)
//             {
//                 ajaxThread();
//             });
//     });


//     // reply to comment
//     $(".replyform").bindOnce("submit.reply", function(event)
//     {
//         event.preventDefault();
//         var comment_text = $(this).children(".comment-textarea").val();
//         var comment_text_length = comment_text.length;
//         if (comment_text_length <= 10000)
//         {
//             var content_id = $(this).children(".hidden_id").val();
//             ajaxPost({
//                 data: {'action':'comment','c_id': content_id,'comment':comment_text},
//                 success: function(data)
//                 {
//                     ajaxThread();
//                     incNumComments();
//                 },
//                 error: null
//             });
//         }
//         else
//         {
//             alert("Please limit your response to 10000 characters.  You have currently typed " + comment_text_length + " characters.");
//         }
//     });


//     // Collapse a thread (a comment and all its children)
//     $('span.collapse').bindOnce("click.collapse",function(e) {
//         var close = '[-]';
//         var open = '[+]';
//         if($(this).text()==close) {
//             $(this).text(open);
//             $(this).next('div.threaddiv').children().hide();
//         } else if($(this).text()==open) {
//             $(this).text(close);
//             $(this).next('div.threaddiv').children().show();
//         }
//     });

//     // Flag a comment
//     $('span.flag').bindOnce("click.flag", function(e) {
//         var commentid = $(this).data('commentid');
//         var comment = $(this).parent().children('div.comment-text').text();
//         var conf = confirm("Are you sure you want to flag this comment?\n\n"+comment);
//         if(conf) {
//             ajaxPost({
//                 data: {'action': 'flag', 'c_id': commentid},
//                 success: function(data) {
//                     alert(data);
//                     $(this).css("color", "red");
//                 },
//                 error: function(data) {
//                     alert("Flagging comment failed.");
//                 }
//             });
//         }
//     });

//     loadHoverComparison();
//     bindChangeContentPrivacy();

// }

// // ajax gets thread and replaces old thread
// function ajaxThread()
// {
//     ajaxPost({
//         data: {'action':'ajaxThread','type':'thread', 'c_id':c_id},
//         success: function(data)
//         {
//             var returned = eval('(' + data + ')');
//             $("#thread").html(returned.html);
//             loadThread();
//             return false;
//         },
//         error: null
//     });
// }

// /***********************************************************************************************************************
//  *
//  *      ~UsersList
//  *
//  ***********************************************************************************************************************/
// function loadUserList()
// {
//     $('.user-list-item').hover
//         (
//             function()
//             {
//                 $(this).children('.user-list-item-name-big').addClass("user-list-item-hover");
//             },
//             function()
//             {
//                 $(this).children('.user-list-item-name-big').removeClass("user-list-item-hover");
//             }
//         );
// }

// /***********************************************************************************************************************
//  *
//  *      ~About
//  *
//  ***********************************************************************************************************************/


// /***********************************************************************************************************************
//  *
//  *      ~Notifications
//  *
//  ***********************************************************************************************************************/
// function unbindNotification()
// {
//     $('.notification-user-follow').unbind();
//     $('.notification-follow-response-y').unbind();
//     $(".notificatton-follow-response-n").unbind();
//     $('.notification-invite-response-y').unbind();
//     $(".notificatton-invite-response-n").unbind();
//     $('.notification-group-response-y').unbind();
//     $(".notificatton-group-response-n").unbind();
// }

// function loadNotification()
// {
//     $(".notification_user_follow").click( function(event)
//     {
//         event.preventDefault();
//         var follow_id = $(this).siblings(".user_follow_id").val();
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         ajaxPost({
//                 data: {
//                     'action':'userFollowRequest',
//                     'p_id': follow_id
//                 },
//                 success: function(data)
//                 {
//                     wrapper.siblings(".notification_text").children('.notification_append').fadeIn(600);
//                 },
//                 error: function(jqXHR, textStatus, errorThrown)
//                 {
//                     $('body').html(jqXHR.responseText);
//                 }
//             }
//         );
//     });

//     $(".notification_follow_response_y").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         userFollowResponse(event,"Y",$(this));
//         wrapper.siblings(".notification_text").children('.notification_append_y').fadeIn(600);
//     });

//     $(".notification_follow_response_n").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         userFollowResponse(event,"N",$(this));
//         wrapper.siblings(".notification_text").children('.notification_append_n').fadeIn(600);
//     });

//     $(".notification_group_response_y").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         groupFollowResponse(event,"Y",wrapper);
//         wrapper.siblings(".notification_text").children('.notification_append_y').fadeIn(600);
//     });

//     $(".notification_group_response_n").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         groupFollowResponse(event,"N",wrapper);
//         wrapper.siblings(".notification_text").children('.notification_append_n').fadeIn(600);
//     });

//     $(".notification_invite_response_y").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         groupInviteResponse(event,"Y",wrapper);
//         wrapper.siblings(".notification_text").children('.notification_append_y').fadeIn(600);
//     });

//     $(".notification_invite_response_n").click( function(event) {
//         var wrapper = $(this).parent(".notification_buttons");
//         wrapper.fadeOut(600);
//         groupInviteResponse(event,"N",wrapper);
//         wrapper.siblings(".notification_text").children('.notification_append_n').fadeIn(600);
//     });

//     $("a.agg_popup").bindOnce("click.agg_notification_modal",
//         function(event)
//         {
//             event.preventDefault();
//             var n_id = $(this).data('n_id');
//             ajaxPost({
//                 'data': {'action':'getAggregateNotificationUsers',
//                     'n_id': n_id },
//                 success: function(data)
//                 {
//                     var obj = eval('(' + data + ')');
//                     $('div#agg_notification_modal').html(obj.html);
//                     $('div.overdiv').fadeIn(300);
//                     $('div#agg_notification_modal').fadeIn(300);

//                     $('div.agg_notification_modal_close').click(function(event) {
//                         $('div.overdiv').hide();
//                         $('div#agg_notification_modal').hide();
//                     });

//                     loadHoverComparison();
//                 },
//                 error: function(jqXHR, textStatus, errorThrown)
//                 {
//                     $('body').html(jqXHR.responseText);
//                 }
//             })
//         }
//     );

//     $('div.overdiv').click(function(event) {
//         $('div.overdiv').hide();
//         $('div#agg_notification_modal').hide();
//     });
// }


// function updateNotificationsNum() {

//     ajaxPost({
//         'data': {'action':'getNumNotifications', 'log-ignore':true},
//         success: function(data)
//         {
//             var obj = eval('(' + data + ')');
//             $("#notifications-number-text").text(obj.num);
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $('body').html(jqXHR.responseText);
//         }
//     });
// }


// function updatePage() {

//     ajaxPost({
//         'data': {'action':'updatePage', 'log-ignore':true},
//         success: function(data)
//         {
//             var obj = eval('(' + data + ')');

//             // update notifications num
//             $("#notifications-number-text").text(obj.notifications_num);
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $('body').html(jqXHR.responseText);
//         }
//     });

// }


// /***********************************************************************************************************************
//  *
//  *      ~Profile
//  *
//  ***********************************************************************************************************************/
// var prof_more_notifications = true;
// var prof_more_actions = true;
// var prof_more_groups = true;

// function getMoreNotifications()
// {
//     if( prof_more_notifications )
//     {
//         prof_more_notifications = false;
//         var num_notifications = $("#num_notifications").val();
//         ajaxPost({
//             'data': {'action':'getNotifications',
//                 'num_notifications':num_notifications },
//             success: function(data)
//             {
//                 var obj = eval('(' + data + ')');
//                 $('#profile_notifications').append(obj.html);
//                 $('#num_notifications').val(obj.num_notifications);
//                 if( obj.hasOwnProperty('error') && obj.error == 'No more notifications' )
//                 {
//                     $('#see_more_notifications').html('No more notifications');
//                     $('#see_more_notifications').unbind();
//                     $('#see_more_notifications').click( function(event)
//                     {
//                         event.preventDefault();
//                     });
//                 }
//                 else if( obj.hasOwnProperty('error') )
//                 {
//                     $('body').html(obj.error);
//                 }
//                 else
//                 {
//                     prof_more_notifications = true;
//                 }
//                 unbindNotification();
//                 loadNotification();
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// function getMoreUserActions()
// {
//     if( prof_more_actions )
//     {
//         prof_more_actions = false;
//         var num_actions = $("#num_actions").val();
//         ajaxPost({
//             'data': {'action':'getUserActions',
//                 'num_actions':num_actions,
//                 'p_id':p_id },
//             success: function(data)
//             {
//                 var obj = eval('(' + data + ')');
//                 $('#profile_activity_feed').append(obj.html);
//                 $('#num_actions').val(obj.num_actions);
//                 if( obj.hasOwnProperty('error') && obj.error == 'No more actions' )
//                 {
//                     $('#profile_more_actions').html('No more actions')
//                     $('#profile_more_actions').unbind();
//                     $('#profile_more_actions').click( function(event)
//                     {
//                         event.preventDefault();
//                     });
//                 }
//                 else if( obj.hasOwnProperty('error') )
//                 {
//                     $('body').html(obj.error);
//                 }
//                 else
//                 {
//                     prof_more_actions = true;
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// function getMoreGroups()
// {
//     if( prof_more_groups )
//     {
//         prof_more_groups = false;
//         var num_groups = $("#num_groups").val();
//         ajaxPost({
//             'data': {'action':'getUserGroups',
//                 'num_groups':num_groups,
//                 'p_id':p_id },
//             success: function(data)
//             {
//                 var obj = eval('(' + data + ')');
//                 $('#profile_group_feed').append(obj.html);
//                 $('#num_groups').val(obj.num_groups);
//                 if( obj.hasOwnProperty('error') && obj.error == 'No more groups' )
//                 {

//                     $('#profile_more_groups').html('No more groups');
//                     $('#profile_more_groups').unbind();
//                     $('#profile_more_groups').click( function(event)
//                     {
//                         event.preventDefault();
//                     });
//                 }
//                 else if( obj.hasOwnProperty('error') )
//                 {
//                     $('body').html(obj.error);
//                 }
//                 else
//                 {
//                     prof_more_groups = true;
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// function bindProfileFollowersButton()
// {
//     $('#profile_followers').click( function(event) {
//         event.preventDefault();
//         $('div.overdiv').fadeToggle("fast");
//         $('div#profile_followers_modal').fadeToggle("fast");
//         loadHoverComparison();
//     });

//     $('div.overdiv').click(function() {
//         $('div.overdiv').hide();
//         $('div#profile_followers_modal').hide();
//     });

//     $('div.followers_modal_close').click(function() {
//         $('div.overdiv').hide();
//         $('div#profile_followers_modal').hide();
//     });
// }

// function loadProfile()
// {
//     unbindNotification();
//     loadNotification();

//     bindProfileFollowersButton();

//     $("#user_follow_button").click( function(event)
//     {
//         userFollow(event,$(this),true);
//     });

//     $(".user-unfollow-button").click( function(event)
//     {
//         userFollow(event,$(this),false);
//     });

//     $(".group-invite-response-y").click( function(event) {
//         groupInviteResponse(event,"Y",$(this));
//     });

//     $(".group-invite-response-n").click( function(event) {
//         groupInviteResponse(event,"N",$(this));
//     });

//     $(window).scroll(
//         function()
//         {
//             if  (($(window).scrollTop() + $(window).height() + 5 >= $(document).height())) {

//                 if( p_id == view_id )
//                 {
//                     getMoreNotifications();
//                 }
//                 getMoreUserActions();
//                 getMoreGroups();
//             }
//         }
//     );

//     $('#see_more_notifications').click(
//         function(event)
//         {
//             event.preventDefault();
//             getMoreNotifications();
//         }
//     );

//     $('#profile_more_actions').click(
//         function(event)
//         {
//             event.preventDefault();
//             getMoreUserActions();
//         }
//     );

//     $('#profile_more_groups').click(
//         function(event)
//         {
//             event.preventDefault();
//             getMoreGroups();
//         }
//     );

//     $(".public-follow").click( function(event)
//     {
//         setFollowPrivacy(event,0,$(this));
//     });

//     $(".private-follow").click( function(event)
//     {
//         setFollowPrivacy(event,1,$(this));
//     });

//     $(".support_button").bindOnce('click.profile', function(event) {
//         event.preventDefault();
//         support($(this));
//     });

//     $(".message_button").click(function(event) {
//         event.preventDefault();
//         $(".message-dialogue").toggle();
//     });

//     $(".message_send").click(function(event) {
//         event.preventDefault();
//         var $wrapper = $(this).parents(".message-wrapper");
//         messageRep($wrapper);
//     });

//     $(".message_x").bindOnce("click.message", function(event) {
//         event.preventDefault();
//         $(this).parents(".message-wrapper").hide();
//     });

//     $('div.profile-img').bindOnce("click.image", function(event) {
//         event.preventDefault();
//         $('div.overdiv').show();
//         if ($('img.profile-img-actual-size').length==0) {
//             var img_to_show = $('div.profile-img img').data('original_image');
//             var img = $("<img />").attr('src', img_to_show).attr('class', 'profile-img-actual-size')
//                 .load(function() {
//                     if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
//                         alert('broken image!');
//                     } else {
//                         $("div.profile-img-modal").append(img);
//                     }
//                 });

//         }
//         $('div.profile-img-modal').css('background-image', img_to_show).show();

//     });

//     $('div.overdiv').click(function(event) {
//         $('div.profile-img-modal').hide();
//     });
// }


// /* sends a message to a representative */
// function messageRep($wrapper) {

//     var p_id = $wrapper.data('p_id');
//     var message = $wrapper.find(".message-textarea").val();

//     ajaxPost({
//         data: {'action':'messageRep', 'p_id':p_id, 'message':message
//         },
//         success: function(data) {
//             $wrapper.hide();
//             $(".message-sent").show();
//             $(".message-sent").fadeOut(1500);

//             var returned = eval('(' + data + ')');
//             var num = returned.num;
//             $(".messages-number").text(num);
//         },
//         error: null
//     });
// }

// /* supports a politician */
// function support(div) {

//     var p_id = div.data('p_id');
//     var confirmed = div.data('confirmed');

//     ajaxPost({
//         data: {'action':'support','p_id':p_id, 'confirmed':confirmed},
//         success: function(data)
//         {
//             var returned = eval('(' + data + ')');
//             var num = returned.num;
//             $(".supporters-number").text(num);

//             if (confirmed == 0) {
//                 $(".unsupport").hide();
//                 $(".support").show();
//             }
//             else {
//                 $(".support").hide();
//                 $(".unsupport").show();
//             }
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $("body").html(jqXHR.responseText);
//         }
//     });
// }


// /***********************************************************************************************************************
//  *
//  *      ~Petition
//  *
//  ***********************************************************************************************************************/
// function loadPetition()
// {
//     var barWrapper = $('div.petition_bar div.bar-wrapper');
//     petitionBar(barWrapper);

//     $("#sign-button").click(function(event)
//     {
//         event.preventDefault();
//         ajaxPost({
//             data: {'action':'sign','c_id':c_id},
//             success: function(data)
//             {
//                 var returned = eval('(' + data + ')');
//                 if (returned.success==true) {
//                     $("div.petition-signers-list").append(returned.signer);
//                     $('div.signers-bar-wrapper').html(returned.bar);
//                     if ($('#be-first-signer-message').length > 0)
//                     {
//                         $('#be-first-signer-message').fadeOut('slow');
//                     }
//                     $('.sign').text("Thank you for signing!");
//                     var num_signers = parseInt($('#num-signers').text().replace('signed',"").replace(/\s/g, ""));
//                     num_signers = num_signers + 1;
//                     $('#num-signers').text(num_signers + " " + "signed");
//                     var barWrapper = $('div.petition_bar div.bar-wrapper');
//                     petitionBar(barWrapper);
//                     loadHoverComparison();
//                 }
//                 else {
//                     $('.sign').text(returned.error);
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $("body").html(jqXHR.responseText);
//             }
//         });
//     });

//     $("#finalize-button").click(function(event)
//     {
//         event.preventDefault();
//         ajaxPost({
//             data: {'action':'finalize','c_id':c_id},
//             success: function(data)
//             {
//                 location.reload();
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $("body").html(jqXHR.responseText);
//             }
//         });
//     });

//     $('div.see-all-signers').bindOnce('click', function(e) {
//         e.preventDefault();
//         $('div.overdiv').fadeToggle();
//         $('div.petition-signers-modal').fadeToggle();
//         var petition_id = $('div.petition-signers-modal').data('petition_id');
//         alert('clicky '+petition_id);
//         ajaxPost({
//             data: {'action': 'getSigners', 'petition2_id': petition_id},
//             success: function(data) {
//                 alert(data);
//                 var returned = eval('(' + data + ')');
//                 alert(returned['html']);
//             },
//             error: function(data) {
//                 var returned = eval('(' + data + ')');
//                 alert("error: "+returned['error']);
//             }
//         });
//     });


//     $('div.overdiv').bindOnce('click.hideSigners', function(e) {
//         e.preventDefault();
//         $('div.overdiv').hide();
//         $('div.petition-signers-modal').hide();
//     })

// }

// /***********************************************************************************************************************
//  *
//  *      ~Petition
//  *
//  **********************************************************************************************************************/

// function loadAccount()
// {
//     $('#choose-image input').attr("accept","image/jpg, image/gif, image/png, image/JPG, image/GIF, image/PNG, image/jpeg");

//     $("#submitpassword").click(function(event)
//     {
//         event.preventDefault();
//         $("#passwordform").submit();
//     });

//     $("#submitpic").click(function(event)
//     {
//         event.preventDefault();
//         $("#picform").submit();
//     });

//     $('#new2').bind('keyup', function(event)
//     {
//         if (event.keyCode != 13)
//         {
//             var new1 = $('#new1').val();
//             var new2 = $('#new2').val();
//             if (new1 == "" && new2 == "")
//             {
//                 $('.new').css({"background-color":"#FFFFFF"});
//             }
//             else if (new1==new2)
//             {
//                 $('.new').css({"background-color":"#DBFFD6"});
//             }
//             else
//             {
//                 $('.new').css({"background-color":"#FFD6D6"});
//             }
//         }
//     });

//     $('#new1').bind('keyup', function(event)
//     {
//         if (event.keyCode != 13 && $('#new2').val() != "")
//         {
//             var new1 = $('#new1').val();
//             var new2 = $('#new2').val();
//             if (new1 == "" && new2 == "")
//             {
//                 $('.new').css({"background-color":"#FFFFFF"});
//             }
//             else if (new1==new2)
//             {
//                 $('.new').css({"background-color":"#DBFFD6"});
//             }
//             else
//             {
//                 $('.new').css({"background-color":"#FFD6D6"});
//             }
//         }
//     });
// }



// /***********************************************************************************************************************
//  *
//  *      ~Group
//  *
//  **********************************************************************************************************************/
// function bindGroupRequestsButton()
// {
//     $('#group_requests').click( function(event) {
//         event.preventDefault();
//         $('div.overdiv').fadeToggle("fast");
//         $('div#group_requests_modal').fadeToggle("fast");
//     });

//     $('div.overdiv').click(function() {
//         $('div.overdiv').hide();
//         $('div#group_requests_modal').hide();
//     });

//     $('div.request_modal_close').click(function() {
//         $('div.overdiv').hide();
//         $('div#group_requests_modal').hide();
//     });
// }

// function groupFollowResponse(event,response,div)
// {
//     event.preventDefault();
//     var follow_id = div.data("follow_id");
//     var g_id = div.data("g_id");
//     ajaxPost({
//             data: {
//                 'action':'joinGroupResponse',
//                 'follow_id': follow_id,
//                 'g_id': g_id,
//                 'response': response
//             },
//             success: function(data)
//             {
//                 //alert(data);
//             },
//             error: function(error, textStatus, errorThrown)
//             {
//                 $('body').html(error.responseText);
//             }
//         }
//     );
// }

// var group_more_actions = true;
// var group_more_members = true;

// function getMoreGroupActions()
// {
//     if( group_more_actions )
//     {
//         group_more_actions = false;
//         var num_actions = $("#num_actions").val();
//         ajaxPost({
//             'data': {'action':'getGroupActions',
//                 'num_actions':num_actions,
//                 'g_id':g_id },
//             success: function(data)
//             {
//                 var obj = eval('(' + data + ')');
//                 $('#group_activity_feed').append(obj.html);
//                 $('#num_actions').val(obj.num_actions);
//                 if( 'error' in obj && obj.error == 'No more actions' )
//                 {
//                     $('#group_more_actions').html('No more actions');
//                     $('#group_more_actions').unbind();
//                     $('#group_more_actions').click( function(event)
//                     {
//                         event.preventDefault();
//                     });
//                 }
//                 else if( 'error' in obj )
//                 {
//                     $('body').html(obj.error);
//                 }
//                 else
//                 {
//                     group_more_actions = true;
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// function getMoreGroupMembers()
// {
//     if( group_more_members )
//     {
//         group_more_members = false;
//         var num_members = $("#num_members").val();
//         ajaxPost({
//             'data': {'action':'getGroupMembers',
//                 'num_members':num_members,
//                 'g_id':g_id },
//             success: function(data)
//             {
//                 var obj = eval('(' + data + ')');
//                 $('.group_members_container').append(obj.html);
//                 $('#num_members').val(obj.num_members);
//                 if( 'error' in obj && obj.error == 'No more members' )
//                 {
//                     $('#group_more_members').html('No more members');
//                     $('#group_more_members').unbind();
//                     $('#group_more_members').click( function(event)
//                     {
//                         event.preventDefault();
//                     });
//                 }
//                 else if( 'error' in obj )
//                 {
//                     $('body').html(obj.error);
//                 }
//                 else
//                 {
//                     group_more_members = true;
//                 }
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// // bind news div
// function bindNewDivs()
// {
//     $('.group-member-div').hover
//         (
//             function(){ $(this).css("background-color","#EBEBEB") },
//             function(){ $(this).css("background-color","#FFFFFF") }
//         );
// }

// var loadUsersLockout=false;
// function loadMoreUsers(event, replace)
// {
//     if (replace == true) {
//         $("#histogram-displayed-num").val(0);
//     }
//     event.preventDefault();
//     var histogram_displayed_num = $('#histogram-displayed-num').val();
//     var histogram_topic = $('#histogram-topic').val();
//     var histogram_block = $('#histogram-block').val();
//     var group_id = $('#group-id').val();
//     if (!loadUsersLockout)
//     {
//         loadUsersLockout = true;
//         ajaxPost({
//             data: {'action':'loadGroupUsers','histogram_displayed_num':histogram_displayed_num,'group_id':group_id,
//                 'histogram_topic':histogram_topic,'histogram_block':histogram_block },
//             success: function(data)
//             {
//                 var returned = eval('(' + data + ')');
//                 if (replace==true) {
//                     $('#members-list').html(returned.html);
//                 }
//                 else {
//                     $('#members-list').append(returned.html);
//                 }
//                 $('#histogram-displayed-num').val(returned.num);
//                 loadHoverComparison();
//                 loadAjaxifyAnchors();
//                 bindNewDivs();
//                 loadUsersLockout = false;
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $('body').html(jqXHR.responseText);
//             }
//         });
//     }
// }

// /* binds js for create motion modal */
// function loadCreateMotion() {

//     $(".motion_action_select").bindOnce("change.motion", function(event) {
//         var action = $(this).val();
//         $(".motion_action_modifier").hide();
//         var class_name = action + "_modifier";
//         $("." + class_name).show();
//     });

//     $('select.add_moderator_select').select2({
//         placeholder: "Enter a member,"
//     });

//     $('select.remove_moderator_select').select2({
//         placeholder: "Enter a moderator,"
//     });

//     $('select.motion_action_select').select2({
//         placeholder: "Choose an action."
//     });

//     $(".create_motion_button").bindOnce("click.motion", function(event) {
//         event.preventDefault();
//         var action =  $(".motion_action_select").val();
//         var because = $(".because_textarea").val();
//         var g_id = $(this).data('g_id');
//         var to_post = {'action': 'createMotion', 'g_id':g_id,
//             'motion_type':action, 'because':because};
//         if (action == 'add_moderator') {
//             to_post['moderator_id'] = $(".add_moderator_select").val();
//         }
//         if (action == 'remove_moderator') {
//             to_post['moderator_id'] = $(".remove_moderator_select").val();
//         }
//         if (action == 'coup_detat') {
//             to_post['government_type'] = "traditional";
//         }
//         ajaxPost({
//             data: to_post,
//             success: function(data)
//             {
//                 var returned = eval('(' + data + ')');
//                 if (returned.success) {
//                     location.reload();
//                 }
//                 else {
//                     alert(data);
//                 }
//             }
//         });
//     });
// }


// function loadGroup()
// {
//     loadInviteButton();
//     bindGroupRequestsButton();

//     $(".group_response_y").click( function(event) {
//         var wrapper = $(this).parent(".group_request_buttons");
//         wrapper.fadeOut(600);
//         groupFollowResponse(event,"Y",wrapper);
//         wrapper.siblings(".group_request_text").children('.group_request_append_y').fadeIn(600);
//     });

//     $(".group-response-n").click( function(event) {
//         var wrapper = $(this).parent(".group_request_buttons");
//         wrapper.fadeOut(600);
//         groupFollowResponse(event,"N",wrapper);
//         wrapper.siblings(".group_request_text").children('.group_request_append_n').fadeIn(600);
//     });

//     $("#group_follow").click( function(event) {
//         groupFollow(event,$(this),true);
//     });
//     $("#group_unfollow").click( function(event) {
//         groupFollow(event,$(this),false);
//     });

//     // select histogram block
//     $(".histogram-select-block").click(function(event) {
//         event.preventDefault();
//         var block = $(this).siblings(".block-val").val();
//         var was = $("#histogram-block").val();
//         if (block == was) {
//             $("#histogram-block").val(-1);
//         }
//         else {
//             $("#histogram-block").val(block);
//         }
//         loadMoreUsers(event, true);
//     });

//     // change histogram topic
//     $(".h-topic-img").click(function(event) {
//         var wrapper = $(this).parents(".topic-icon-wrapper");
//         selectTopicSingle(wrapper);
//         var topic = $(this).siblings(".t-alias").val();
//         var was = $("#histogram-topic").val();
//         if (topic == was) {
//             $("#histogram-topic").val('general');
//         }
//         else {
//             $("#histogram-topic").val(topic);
//         }
//         loadMoreUsers(event, true);
//         getHistogram();
//     });

//     $('#group_more_actions').click(
//         function(event)
//         {
//             event.preventDefault();
//             getMoreGroupActions();
//         }
//     );

//     $('#group_more_members').click(
//         function(event)
//         {
//             event.preventDefault();
//             getMoreGroupMembers();
//         }
//     );

//     $(window).scroll(
//         function()
//         {
//             if(($(window).scrollTop() + $(window).height() >= $(document).height() ))
//             {
//                 getMoreGroupActions();
//                 getMoreGroupMembers();
//             }
//         }
//     );

//     $('#group-see-more-users').bindOnce('click.group', function(event)
//     {
//         loadMoreUsers(event, false);
//     });

//     loadHistogram();

//     $(".histogram_box").bindOnce("click.group", function(event) {
//         window.location.href = "/histogram/" + histogram.g_id + "/"
//     });

//     bindNewDivs();

//     $("#group_motion_button").bindOnce("click.group", function(event) {
//         event.preventDefault();
//         var modal = $(".motion_modal");
//         launchAModal($(modal));
//     });

//     loadCreateMotion();

// }

// /***********************************************************************************************************************
//  *
//  *      ~GroupEdit
//  *
//  **********************************************************************************************************************/


// function loadGroupEdit()
// {
//     bindGroupPrivacyRadio();
//     bindScaleRadio();
//     bindRemoveAdmin();
//     selectPrivacyRadio();
//     selectScaleRadio();

//     var pointer = $('.group_edit_pointer');
//     var pencil = $('.group_edit_icon').detach();

//     $('.group_edit_input').hover(
//         function() { $(this).parent().next().append(pencil); },
//         function() { pencil = pencil.detach(); }
//     );

//     $('.append_pointer').bindOnce("click.append_pointer" , function(event)
//     {
//         $('.append_pointer').removeClass("account-button-selected");
//         $(this).addClass("account-button-selected");
//         $(this).prepend(pointer);
//     });

//     $('.group_edit_button').bindOnce("click.group_info_edit" , function(event)
//     {
//         $(".group_edit_tab").hide();
//         var div_class = $(this).data('div');
//         $("." + div_class).show();
//     });

//     $('#edit_admin_submit').bindOnce('click.edit_admin_submit', (function(e) {
//         e.preventDefault();
//         var g_id = $("#edit_admin_submit").data('g_id');
//         var new_admins = $('.admin_select').select2("val");

//         if (new_admins!='') {
//             ajaxPost({
//                 data: {'action': 'addAdmins', 'admins': JSON.stringify(new_admins), 'g_id':g_id},
//                 success: function(data)
//                 {
//                     var returned = eval('(' + data + ')');
//                     $('#edit_admin_submit_message').html('Administrator Added');
//                     $('#edit_admin_submit_message').show();
//                     $('#edit_admin_submit_message').fadeOut(3000);
//                     $('#admin_remove_container').hide();
//                     $('#admin_remove_container').html(returned.html);
//                     $('#admin_remove_container').fadeIn(600);
//                     bindRemoveAdmin();
//                 }
//             });
//         }
//     }));

//     $('#members_remove_submit').bindOnce('click.remove_members_submit', (function(e) {
//         e.preventDefault();
//         var g_id = $(this).data('g_id');
//         var members = $('.member_select').select2("val");

//         if (members!='') {
//             ajaxPost({
//                 data: {'action': 'removeMembers', 'members': JSON.stringify(members), 'g_id':g_id},
//                 success: function(data)
//                 {
//                     var returned = eval('(' + data + ')');
//                     var return_message = $('#members_remove_submit_message');
//                     return_message.html('Members Removed');
//                     return_message.show();
//                     return_message.fadeOut(3000);
//                     var members_container = $(".group_members_container");
//                     members_container.hide();
//                     members_container.html(returned.html);
//                     members_container.fadeIn(600);
//                 }
//             });
//         }
//     }));


//     $('select.admin_select').select2({
//         placeholder: "Enter a member,"
//     });

//     $('select.member_select').select2({
//         placeholder: "Enter a member,"
//     });
// }

// function bindRemoveAdmin()
// {
//     $('.remove_admin').bindOnce('click.remove_admin', (function(e) {
//         var admin_id = $(this).data('admin_id');
//         var admin_name = $(this).data('admin_name');
//         var g_id = $('#edit_admin_submit').data('g_id');
//         $(this).parents('table.admin_container').fadeOut(600);
//         removeAdmin( admin_id , g_id ,function(data)
//         {
//             $('optgroup#add_members_input').append('<option value="' + admin_id + '">' + admin_name + '</option>');
//         });
//     }));

//     $('.remove_admin_self').bindOnce('click.remove_admin', (function(e) {
//         var admin_id = $(this).data('admin_id');
//         var admin_name = $(this).data('admin_name');
//         var g_id = $('#edit_admin_submit').data('g_id');
//         $(this).parents('table.admin_container').fadeOut(600);
//         removeAdmin( admin_id , g_id ,function(data)
//         {
//             window.location = '/group/' + g_id + '/';
//         });
//     }));
// }

// function removeAdmin(admin_id,g_id,success)
// {
//     ajaxPost({
//         data:
//         {
//             'action': 'removeAdmin',
//             'admin_id': admin_id,
//             'g_id': g_id
//         },
//         success: success,
//         error: function(data)
//         {
//             //alert(data);
//         }
//     })
// }

// function selectPrivacyRadio()
// {
//     var privacy = $('#group_privacy_container').data('group_privacy');
//     var selected = $('input:radio[value="'+privacy+'"][name="group_privacy"]');
//     selected.prop('checked',true);
//     selected.parent().addClass('create-radio-selected');
// }

// function selectScaleRadio()
// {
//     var scale = $('#group_scale_container').data('group_scale');
//     var selected = $('input:radio[value="'+scale+'"][name="scale"]');
//     selected.prop('checked',true);
//     selected.parent().addClass('create-radio-selected');
// }



// /***********************************************************************************************************************
//  *
//  *      ~NewFeed
//  *
//  **********************************************************************************************************************/

// /*
//  Sets the red bar to proper width.
//  */
// function petitionBar() {
//     var petition_bars = $(".petition-bar-wrapper");
//     petition_bars.each(function(index, element) {
//         var percent = $(this).data('percent');
//         $(this).find('.red_bar').css("width", percent + "%");
//     });
// }

// /*
//  Takes in a a value and the classname of an input which the value should
//  either be added to or removed from that list (toggled).
//  */
// function listToggleHelper(list_values, value) {
//     var index = $.inArray(value, list_values);
//     if (index == -1) {
//         list_values.push(value);
//     }
//     else {
//         list_values.splice(index, 1);
//     }
//     return list_values
// }

// /*
//  Replaces feed with all new items based on current parameters.
//  */
// function refreshFeed(num) {

//     feed_metadata.feed_start = 0;
//     current_pinterest_column = 0;
//     getFeed(num);
// }

// /*
//  if the start value is 0, then replace feed with all new items based on current parameters
//  else get new feed items starting at start value and append them to the current feed.
//  */
// function getFeed(num)
// {

//     if (num==-1) {
//         num = 18;
//     }

//     var feed_ranking = feed_metadata.ranking;
//     var feed_display =  feed_metadata.display;
//     var feed_submissions_only =  feed_metadata.submissions_only;
//     var feed_topics = feed_metadata.topics;
//     var feed_types =  feed_metadata.types;
//     var feed_levels =  feed_metadata.levels;
//     var feed_groups =  feed_metadata.groups;
//     var feed_start = feed_metadata.feed_start;
//     feed_topics = JSON.stringify(feed_topics);
//     feed_types = JSON.stringify(feed_types);
//     feed_levels = JSON.stringify(feed_levels);
//     feed_groups = JSON.stringify(feed_groups);

//     var feed_end =  feed_start + num;

//     var feed_replace;
//     if (feed_start==0) {
//         feed_replace = true;
//     }
//     else {
//         feed_replace = false;
//     }

//     setTimeout(function() {
//         $(".feed_loading").show();
//     }, 100);

//     ajaxPost({
//         data: {'action':'ajaxGetFeed','feed_ranking': feed_ranking,'feed_topics':feed_topics,
//             'feed_types':feed_types, 'feed_levels': feed_levels, 'feed_groups':feed_groups,
//             'feed_submissions_only':feed_submissions_only,'feed_display':feed_display,
//             'feed_start':feed_start, 'feed_end':feed_end
//         },
//         success: function(data) {

//             $(".feed_loading").hide();
//             scrollLoadLockout=false;

//             var returned = eval('(' + data + ')');

//             feed_metadata.feed_start = feed_start + returned.num;

//             if (feed_display == "P") {
//                 if (feed_replace == true) {
//                     $(".pinterest_column").html("");
//                 }
//                 var cards = $.parseJSON(returned.cards);
//                 newPinterestRender(cards);
//                 $(".linear-wrapper").hide();
//                 $(".pinterest-wrapper").show();
//             }
//             else {
//                 if (feed_replace == true) {
//                     $(".linear-items-wrapper").html(returned.html);
//                 }
//                 else {
//                     $(".linear-items-wrapper").append(returned.html);
//                 }
//                 $(".pinterest-wrapper").hide();
//                 $(".linear-wrapper").show();
//             }

//             heartButtons();
//             loadShareButton();
//             petitionBar();
//             loadHoverComparison();
//             bindTooltips();
//             bindLinks();

//         },
//         error: null
//     });
// }

// /*
//  makes a post to the server to save the current filter setting as the inputted name.
//  */
// function saveFilter(name) {

//     var feed_name = name;
//     var feed_ranking = feed_metadata.ranking;
//     var feed_display =  feed_metadata.display;
//     var feed_submissions_only =  feed_metadata.submissions_only;
//     var feed_topics = feed_metadata.topics;
//     var feed_types =  feed_metadata.types;
//     var feed_levels =  feed_metadata.levels;
//     var feed_groups =  feed_metadata.groups;
//     feed_topics = JSON.stringify(feed_topics);
//     feed_types = JSON.stringify(feed_types);
//     feed_levels = JSON.stringify(feed_levels);
//     feed_groups = JSON.stringify(feed_groups);

//     ajaxPost({
//         data: {'action':'saveFilter','feed_ranking': feed_ranking,'feed_topics':feed_topics,
//             'feed_types':feed_types, 'feed_levels': feed_levels, 'feed_groups':feed_groups,
//             'feed_submissions_only':feed_submissions_only,'feed_display':feed_display,
//             'feed_name': feed_name
//         },
//         success: function(data) {
//             $(".save_filter_input").val(feed_name);
//             $(".saved-message").show();
//             $(".saved-message").fadeOut();
//         },
//         error: null
//     });
// }

// /* deletes a filter from my_filters list */
// function deleteFilter(name) {
//     ajaxPost({
//         data: {'action':'deleteFilter','f_name':name},
//         success: function(data) {
//             location.reload();
//         },
//         error: null
//     });
// }

// /*
//  retrives the filter setting with the inputted id from the server and refreshes feed.
//  */
// function getFilter(f_id) {
//     ajaxPost({
//         data: {'action':'getFilter', filter_id:f_id},
//         success: function(data) {

//             var returned = eval('('+data+')');

//             feed_metadata.ranking = returned.ranking;
//             feed_metadata.display = returned.display;
//             feed_metadata.submissions_only = returned.submissions_only;
//             feed_metadata.topics = $.parseJSON(returned.topics);
//             feed_metadata.levels = $.parseJSON(returned.levels);
//             feed_metadata.groups = $.parseJSON(returned.groups);
//             feed_metadata.types = $.parseJSON(returned.types);

//             updateFeedVisual();

//             refreshFeed(-1);

//         },
//         error: null
//     })
// }

// /* retrieves and sets defaults filter for user */
// function getFilterByName(name) {
//     $(".saved-filter-selector").removeClass("clicked");
//     var this_filter = $(".saved-filter-selector[data-f_name=" + name + "]");
//     this_filter.addClass("clicked");
//     $(".save_filter_input").val(name);
//     getFilter(this_filter.data('f_id'));
// }

// /* heart stuff */
// function heartButtons()
// {
//     function upvote(wrapper) {
//         vote(wrapper, wrapper.data('c_id'), 1);
//     }

//     function downvote(wrapper) {
//         vote(wrapper, wrapper.data('c_id'), -1);
//     }

//     $(".heart_minus").bindOnce('click.vote', function(event) {
//         var wrapper = $(this).parents(".hearts-wrapper");
//         event.preventDefault();
//         if($(this).hasClass('clicked')) {
//             upvote(wrapper);
//         } else {
//             downvote(wrapper);
//         }

//     });

//     $(".heart_plus").bindOnce('click.vote', function(event) {
//         var wrapper = $(this).parents(".hearts-wrapper");
//         event.preventDefault();
//         if($(this).hasClass('clicked')) {
//             downvote(wrapper);
//         } else {
//             upvote(wrapper);
//         }
//     });
// }



// /*
//  visually and in data representation sets all feed parameters to defaults
//  */
// function clearFilterParameters() {

//     feed_metadata.topics =  [];
//     feed_metadata.types =  [];
//     feed_metadata.levels =  [];
//     feed_metadata.groups =  [];
//     feed_metadata.ranking = 'N';
//     updateFeedVisual();

//     refreshFeed(-1);

// }

// /* updates the visual display of feed parameters based on javascript object representation */
// function updateFeedVisual() {

//     var feed_types = $(".feed-type-selector");
//     feed_types.each(function(index) {
//         var this_type = $(this).data('type');
//         var i = $.inArray(this_type, feed_metadata.types);
//         if (i != -1) {
//             $(this).addClass("clicked");
//         }
//         else {
//             $(this).removeClass("clicked");
//         }
//     });

//     var feed_levels = $(".feed-level-selector");
//     feed_levels.each(function(index) {
//         var this_level = $(this).data('level');
//         var i = $.inArray(this_level, feed_metadata.levels);
//         if (i != -1) {
//             $(this).addClass("clicked");
//         }
//         else {
//             $(this).removeClass("clicked");
//         }
//     });

//     var feed_groups = $(".feed_group_selector");
//     feed_groups.each(function(index) {
//         var this_group = $(this).data('g_id');
//         var i = $.inArray(this_group, feed_metadata.groups);
//         if (i != -1) {
//             $(this).addClass("clicked");
//         }
//         else {
//             $(this).removeClass("clicked");
//         }
//     });

//     var feed_topics = $(".feed-topic-icon-wrapper");
//     feed_topics.each(function(index) {
//         var this_topic = $(this).data('t_id');
//         var i = $.inArray(this_topic, feed_metadata.topics);
//         if (i != -1) {
//             showTopicIcon($(this));
//         }
//         else {
//             hideTopicIcon($(this));
//         }
//     });

//     setDisplay(feed_metadata.display);

//     setRanking(feed_metadata.ranking);
// }

// function setDisplay(value) {
//     feed_metadata.display = value;
//     var visual_wrapper = $("div[data-display=" + value + "]");
//     visualSelectDisplayWrapper(visual_wrapper);
// }

// function setRanking(value) {
//     $(".feed-ranking-selector").removeClass("clicked");
//     var ranking_wrapper = $(".feed-ranking-selector[data-ranking=" + value + "]");
//     ranking_wrapper.addClass("clicked");
//     $(".ranking_menu_title").text(ranking_wrapper.data('verbose'));
//     feed_metadata.ranking = value;
// }

// var current_pinterest_column = 0;
// function newPinterestRender(cards) {

//     var num_columns = $(".pinterest_column").size();

//     $.each(cards, function(index, element) {
//         if (current_pinterest_column == num_columns) {
//             current_pinterest_column = 0;
//         }
//         var bucket = $(".pinterest_column[data-column=" + current_pinterest_column + "]");
//         bucket.append(element);
//         current_pinterest_column += 1;
//     });
// }

// var scrollLoadLockout=false;
// function scrollFeed() {
//     if  (($(window).scrollTop() >= $(document).height() - $(window).height())) {
//         if (scrollLoadLockout==false) {
//             getFeed(-1);
//             scrollLoadLockout = true;
//         }
//     }
// }

// /* shows display select appropriately */
// function visualSelectDisplayWrapper(wrapper) {
//     $(".display-red").hide();
//     $(".display-gray").show();
//     visualDisplayWrapperShow(wrapper);
// }
// function visualDisplayWrapperShow(wrapper) {
//     wrapper.find(".display-gray").hide();
//     wrapper.find(".display-red").show();
// }
// function visualDisplayWrapperHide(wrapper) {
//     wrapper.find(".display-gray").show();
//     wrapper.find(".display-red").hide();
// }

// /**
//  * Binds feed items with UI functionality
//  */
// function bindFeedItems()
// {
//     /**
//      * Binds link of news URL to the image for the URL
//      */
//     $('.link-img img').unbind();
//     $('.link-img img').click(function(event)
//     {
//         var url = $(this).siblings('a').attr('href');
//         // middle mouse button or control + leftclick will open new tab for link
//         if(event.ctrlKey || (!$.browser.msie && event.button == 1) || ($.browser.msie && event.button == 4))
//         {
//             window.open(url, '_blank');
//         }
//         // normal leftclick on link
//         else
//         {
//             window.location = url;
//         }
//     });

//     /**
//      * Adds border on hover to image
//      */
//     $('.link-img img').hover
//         (
//             function(event) { $(this).css("border-color","#f0503b"); }, // hover over
//             function(event) { $(this).css('border-color','#FFFFFF'); }  // hover out
//         );

//     $('.feed-username').click(function(event)
//     {
//         var url = $(this).children('a').attr('href');
//         // middle mouse button or control + leftclick will open new tab for link
//         if(event.ctrlKey || (!$.browser.msie && event.button == 1) || ($.browser.msie && event.button == 4))
//         {
//             window.open(url, '_blank');
//         }
//         // normal leftclick on link
//         else
//         {
//             ajaxLink(url,true);
//         }
//     });

//     // bind newly loaded feed items with comparison hover over
//     loadHoverComparison();
//     loadAjaxifyAnchors();
// }

// /* binds everyting */
// var feed_metadata;
// function loadNewFeed() {

//     $(".how-does").click(function(event) {
//         event.preventDefault();
//         ajaxPost({
//             data: {'action':'likeThis'},
//             success: function(data)
//             {
//                 var returned = eval('(' + data + ')');
//                 var old = $("body").html();
//                 $("body").html(returned.html);
//                 setTimeout(function() {
//                     $("body").html(old);
//                     setTimeout(function() {
//                         location.reload();
//                     }, 500);
//                 }, 2000);
//             },
//             error: function(jqXHR, textStatus, errorThrown)
//             {
//                 $("body").html(jqXHR.responseText);
//             }
//         });
//     });

//     // parse json for metadata
//     feed_metadata = $("#feed_metadata").data('json');
//     updateFeedVisual();

//     var more_options_wrapper = $(".more-options-wrapper");
//     more_options_wrapper.css('height', '0px');
//     more_options_wrapper.css('opacity', 0);
//     more_options_wrapper.css("padding", "0px");
//     //more_options_wrapper.show();
//     //more_options_wrapper.css("overflow", "visible");
//     $(".more_options").click(function(event) {
//         event.preventDefault();
//         $(this).toggleClass("clicked");
//         var wrapper = $(".more-options-wrapper");
//         if (wrapper.hasClass("out")) {
//             wrapper.css("overflow", "hidden");
//             wrapper.animate({"height": '0px', 'padding': '0px', 'opacity':0}, 100);
//             wrapper.removeClass("out");
//             wrapper.find(".menu_toggle").removeClass("clicked");
//             wrapper.find(".menu").hide();
//             wrapper.find(".save-dialog").hide();
//         }
//         else {
//             wrapper.show();
//             wrapper.animate({"height": '105px', 'padding':"10px", 'opacity':1.0}, 100,
//                 function() { wrapper.css('overflow', 'visible'); });
//             wrapper.addClass("out");
//         }
//     });


//     $(".get_feed").click(function(event) {
//         event.preventDefault();;
//         getFeed(-1);
//     });

//     $(".refresh_feed").click(function(event) {
//         event.preventDefault();
//         refreshFeed(-1);
//     });

//     $(".feed-topic-img").click(function(event) {
//         var wrapper = $(this).parents(".topic-icon-wrapper");
//         toggleTopicIcon(wrapper);
//         var value = $(this).parents(".feed-topic-icon-wrapper").data('t_id');
//         listToggleHelper(feed_metadata.topics, value);
//         refreshFeed(-1);
//     });

//     $(".feed-display-selector").click(function(event) {
//         event.preventDefault();
//         var display = $(this).data("display");
//         feed_metadata.display = display;
//         refreshFeed(-1);
//     });

//     $(".open_save_button").click(function(event) {
//         $(".save-dialog").toggle();
//     });

//     $(".save_filter_button").click(function(event) {
//         event.preventDefault();
//         var name = $(".save_filter_input").val();
//         if (name!='' && name!='enter a name for your filter.') {
//             saveFilter(name);
//             $(".save-dialog").hide();
//         }
//         else {
//             $(".save_filter_input").val('enter a name for your filter.');
//         }
//     });

//     $(".delete_saved_filter").click(function(event) {
//         event.preventDefault();
//         var wrapper = $(this).parents(".saved-filter-selector");
//         var f_name = wrapper.data('f_name');
//         deleteFilter(f_name);
//         event.stopPropagation();
//     });

//     $(".saved-filter-selector").click(function(event) {
//         event.preventDefault();
//         var value = $(this).data("f_id");
//         getFilter(value);
//         $(".save_filter_input").val($(this).data('f_name'));
//     });

//     $(".feed_clear").click(function(event) {
//         event.preventDefault();
//         clearFilterParameters();
//     });

//     /* display menu */
//     $(".display-choice").click(function(event) {
//         setDisplay($(this).data('display'));
//         var num = 6;
//         var already = feed_metadata.start;
//         if (already > num) {
//             num = already;
//         }
//         refreshFeed(num);
//     });

//     /* sort-by menu */
//     $(".feed-ranking-selector").click(function(event) {
//         event.preventDefault();
//         setRanking($(this).data('ranking'));
//         refreshFeed(-1);
//     });

//     /* group and network menu  visual */
//     defaultHover($(".group_box"));
//     $(".group_box").click(function(event) {
//         event.preventDefault();
//         defaultClick($(this));
//         event.stopPropagation();
//     });
//     /* group menu  functional */
//     $(".feed_group_selector").click(function(event) {
//         var value = $(this).data('g_id');
//         listToggleHelper(feed_metadata.groups, value);
//         refreshFeed(-1);
//     });

//     /* levels menu */
//     $(".feed-level-selector").click(function(event) {
//         var value = $(this).data('level');
//         listToggleHelper(feed_metadata.levels, value);
//         refreshFeed(-1);
//         event.stopPropagation();
//     });

//     /* types menu */
//     $(".feed-type-selector").click(function(event) {
//         var value = $(this).data('type');
//         listToggleHelper(feed_metadata.types, value);
//         refreshFeed(-1);
//         event.stopPropagation();
//     });

//     /* gray hover for all dropdown menu options */
//     defaultHoverClickSingle($(".menu-option.single"));
//     defaultHoverClick($(".menu-option.multi"));


//     $(".menu-option").hover(
//         function(event) {
//             event.stopPropagation();
//         },
//         function(event) {
//             event.stopPropagation();
//         });

//     getFilterByName(feed_metadata.filter_name);

//     $(window).scroll(scrollFeed);

//     bindCreateButton();
//     loadCreate();
//     bindCloseFirstLoginModal();

// }

// /***********************************************************************************************************************
//  *
//  *      ~CreateModal
//  *
//  **********************************************************************************************************************/
// function bindCreateButton()
// {
//     $('.create_button').click( function(event) {
//         event.preventDefault();
//         $('div.overdiv').fadeToggle("fast");
//         $('div.create_modal').fadeToggle("fast");
//     });

//     $('div.overdiv').click(function() {
//         $('div.overdiv').hide();
//         $('div.create_modal').hide();
//     });

//     $('div.create_modal_close').click(function() {
//         $('div.overdiv').hide();
//         $('div.create_modal').hide();
//     });
// }

// function bindGroupPrivacyRadio()
// {
//     $("div.group_privacy_radio").unbind();
//     $("div.group_privacy_radio").click(function(event)
//     {
//         var prev = $("input:radio[name=group_privacy]:checked");
//         prev.attr('checked',false);
//         prev.parent('.group_privacy_radio').removeClass("create-radio-selected");

//         $(this).children("input:radio[name=group_privacy]").attr('checked',true);
//         $(this).addClass("create-radio-selected");
//     });
// }

// function bindScaleRadio()
// {
//     $("div.group_scale_radio").unbind();
//     $("div.group_scale_radio").click(function(event)
//     {
//         var prev = $("input:radio.group_scale:checked");
//         prev.attr('checked',false);
//         prev.parent('.group_scale_radio').removeClass("create-radio-selected");

//         $(this).children("input:radio.group_scale").attr('checked',true);
//         $(this).addClass("create-radio-selected");
//     });

//     $("div.petition_scale_radio").unbind();
//     $("div.petition_scale_radio").click(function(event)
//     {
//         var prev = $("input:radio.petition_scale:checked");
//         prev.attr('checked',false);
//         prev.parent('.petition_scale_radio').removeClass("create-radio-selected");

//         $(this).children("input:radio.petition_scale").attr('checked',true);
//         $(this).addClass("create-radio-selected");
//     });

//     $("div.news_scale_radio").unbind();
//     $("div.news_scale_radio").click(function(event)
//     {
//         var prev = $("input:radio.news_scale:checked");
//         prev.attr('checked',false);
//         prev.parent('.news_scale_radio').removeClass("create-radio-selected");

//         $(this).children("input:radio.news_scale").attr('checked',true);
//         $(this).addClass("create-radio-selected");
//     });
// }

// function createGroupValidation( event )
// {
//     event.preventDefault();
//     var valid = true;

//     /* Title */
//     var title = $('#group_title').val();
//     var title_error = $('#group_name_error');
//     title = title.replace(" ","");
//     if( title == "" )
//     {
//         title_error.text("Please enter a group title.");
//         title_error.show();
//         valid = false;
//     }
//     else
//     {
//         title_error.hide();
//     }

//     /* Description */
//     var description = $('#group_description').val();
//     var desc_error = $('#group_description_error');
//     description = description.replace(" ","");
//     if( description == "" )
//     {
//         desc_error.text("Please enter a group description.");
//         desc_error.show();
//         valid = false;
//     }
//     else
//     {
//         desc_error.hide();
//     }

//     /* Privacy */
//     var privacy = $('input:radio[name=group_privacy]:checked').length;
//     var privacy_error = $('#group_privacy_error');
//     if( privacy < 1 )
//     {
//         privacy_error.text("Please select a group privacy.");
//         privacy_error.show();
//         valid = false;
//     }
//     else if( privacy > 1 )
//     {
//         privacy_error.text("You have selected multiple group privacy settings.");
//         privacy_error.show();
//         valid = false;
//     }
//     else
//     {
//         privacy_error.hide();
//     }

//     /* Scale */
//     var scale = $('input:radio.group_scale:checked').length;
//     var scale_error = $('#group_scale_error');
//     if( scale > 1 )
//     {
//         scale_error.text("You have selected multiple group scales.");
//         scale_error.show();
//         valid = false;
//     }
//     else
//     {
//         scale_error.hide();
//     }

//     /* Image */
//     var image = $('input#group_image').val();
//     var image_error = $('#group_image_error');
//     if( image == "" )
//     {
//         image_error.text("Please select a group image.");
//         image_error.show();
//         valid = false;
//     }
//     else
//     {
//         image_error.hide();
//     }

//     /* Topics */
//     var topic = $('#group_input_topic').find('input:radio[name=topics]:checked').length;
//     var topic_error = $('#group_topic_error');
//     if( topic > 1 )
//     {
//         topic_error.text("You have selected multiple group topics.");
//         topic_error.show();
//         valid = false;
//     }
//     else
//     {
//         topic_error.hide();
//     }

//     /* submit if valid! */
//     if( valid )
//     {
//         $('#group_form').submit();
//     }
// }

// function createPetitionValidation( event )
// {
//     event.preventDefault();
//     var valid = true;

//     /* Title */
//     var title = $('#petition_title').val();
//     var title_error = $('#petition_name_error');
//     title = title.replace(" ","");
//     if( title == "" )
//     {
//         title_error.text("Please enter a petition title.");
//         title_error.show();
//         valid = false;
//     }
//     else
//     {
//         title_error.hide();
//     }

//     /* Description */
//     var description = $('#petition_description').val();
//     var desc_error = $('#petition_description_error');
//     description = description.replace(" ","");
//     if( description == "" )
//     {
//         desc_error.text("Please enter a petition description.");
//         desc_error.show();
//         valid = false;
//     }
//     else
//     {
//         desc_error.hide();
//     }

//     /* Scale */
//     var scale = $('input:radio.petition_scale:checked').length;
//     var scale_error = $('#petition_scale_error');
//     if( scale > 1 )
//     {
//         scale_error.text("You have selected multiple petition scales.");
//         scale_error.show();
//         valid = false;
//     }
//     else
//     {
//         scale_error.hide();
//     }

//     /* Topics */
//     var topic = $('#petition_input_topic').find('input:radio[name=topics]:checked').length;
//     var topic_error = $('#petition_topic_error');
//     if( topic > 1 )
//     {
//         topic_error.text("You have selected multiple petition topics.");
//         topic_error.show();
//         valid = false;
//     }
//     else
//     {
//         topic_error.hide();
//     }

//     /* submit if valid! */
//     if( valid )
//     {
//         $('#petition_form').submit();
//     }
// }

// function createNewsValidation( event )
// {
//     event.preventDefault();
//     var valid = true;

//     /* Title */
//     var title = $('#news-input-link').val();
//     var title_error = $('#news_name_error');
//     title = title.replace(" ","");
//     if( title == "" )
//     {
//         title_error.text("Please enter a news link.");
//         title_error.show();
//         valid = false;
//     }
//     else
//     {
//         title_error.hide();
//     }

//     /* Scale */
//     var scale = $('input:radio.news_scale:checked').length;
//     var scale_error = $('#news_scale_error');
//     if( scale > 1 )
//     {
//         scale_error.text("You have selected multiple news scales.");
//         scale_error.show();
//         valid = false;
//     }
//     else
//     {
//         scale_error.hide();
//     }

//     /* Topics */
//     var topic = $('#news_input_topic').find('input:radio[name=topics]:checked').length;
//     var topic_error = $('#news_topic_error');
//     if( topic > 1 )
//     {
//         topic_error.text("You have selected multiple news topics.");
//         topic_error.show();
//         valid = false;
//     }
//     else
//     {
//         topic_error.hide();
//     }

//     /* submit if valid! */
//     if( valid )
//     {
//         postNews();
//     }
// }

// function postNews()
// {
//     var title = $('#news-input-title').val();
//     var summary = $('#news-input-summary').val();
//     var link = $('#news-input-link').val();
//     var description = $('#news-link-generation-description').text();
//     var screenshot = $('.news_link_selected').attr("src");
//     var scale = $('input:radio.news_scale:checked').val();
//     var topic = $('input:radio[name=topics]:checked').val();
//     ajaxPost({
//         data: {'action':'create','title':title,'summary':summary,'link':link,
//             'type':'N', 'description':description, 'screenshot':screenshot, 'topics':topic, 'scale':scale },
//         success: function(data)
//         {
//             var returned = eval('(' + data + ')');
//             if (returned.success == false)
//             {
//                 $("#news-errors-link").html(returned.errors.link);
//                 $("#news-errors-title").html(returned.errors.title);
//                 $("#news-errors-summary").html(returned.errors.summary);
//                 $("#news-errors-topic").html(returned.errors.topics);
//                 $("#news-errors-non_field").html(returned.errors.non_field_errors);
//             }
//             else
//             {
//                 window.location=returned.url;
//             }
//         },
//         error: function(jqXHR, textStatus, errorThrown)
//         {
//             $("body").html(jqXHR.responseText);
//         }
//     });
// }

// function loadCreate()
// {
//    $("div.button-placeholder").bindOnce("click", function(e) {
//        $("div.button-placeholder").removeClass("selected");
//        $(this).addClass("selected");
//    })

//     $('#create_petition_button').bindOnce('click.create',
//         function()
//         {
//             $('.create_content_div').hide();
//             $('#create_petition_div').toggle();
//         });

//     $('#create_news_button').bindOnce('click.create',
//         function()
//         {
//             $('.create_content_div').hide();
//             $('#create_news_div').toggle();
//         });

//     $('#create_group_button').bindOnce('click.create',
//         function()
//         {
//             $('.create_content_div').hide();
//             $('#create_group_div').toggle();
//         });

//     bindGroupPrivacyRadio();
//     bindScaleRadio();

//     $('#submit_group_button').bindOnce('click.create',
//         function(event)
//         {
//             event.preventDefault();
//             lockoutFunction(createGroupValidation, [event]);
//         }
//     );


//     $('#submit_petition_button').bindOnce('click.create',
//         function(event)
//         {
//             event.preventDefault();
//             lockoutFunction(createPetitionValidation, [event]);
//         }
//     );

//     $('#submit_news_button').bindOnce('click.create',
//         function(event)
//         {
//             event.preventDefault();
//             lockoutFunction(createNewsValidation, [event]);
//         }
//     );

//     var timeout;
//     var delay = 750;
//     var isLoading = false;
//     var currentURL;
//     var currentLink = 1;
//     var image_count = 0;
//     var returned;

//     $('#news-input-link').bind('keyup',function()
//     {
//         var text = $(this).val();

//         function selectImageToggle()
//         {
//             $('#cycle-img-span').text(currentLink + " / " + image_count);
//             $('.news_link_image').removeClass("news_link_selected").hide();
//             $('.news_link_image').eq(currentLink-1).addClass("news_link_selected").show();
//         }


//         if (timeout)
//         {
//             clearTimeout(timeout);
//         }

//         if (!isLoading && text != currentURL)
//         {
//             timeout = setTimeout(function()
//             {
//                 isLoading = true;
//                 if (regUrl.test(text))
//                 {
//                     $('#news-link-generation-wrapper').empty();
//                     $('#news-link-generation').show();
//                     $('#news-link-generation-wrapper').append('<div style="width:530px;margin-bottom:25px">' +
//                         '<img style="width:75px;height:75px;margin-left:235px;" id="loading-img" src="' + STATIC_URL + '/images/ajax-loader.gif"></div>');
//                     $('#news-summary').show();
//                     ajaxPost({
//                         data: {'action':'getLinkInfo','remote_url':text},
//                         success: function(data)
//                         {
//                             if (data != "-")
//                             {
//                                 returned = eval('(' + data + ')');
//                                 $('#news-link-generation-wrapper').html(returned.html);
//                                 image_count = $('.news_link_image_container').children().length;
//                                 $('#cycle-img-left').bind('click',function()
//                                 {
//                                     if (currentLink-1 < 1) { currentLink = image_count; }
//                                     else { currentLink--; }
//                                     selectImageToggle();

//                                 });
//                                 $('#cycle-img-right').bind('click',function()
//                                 {
//                                     if (currentLink+1 > image_count) { currentLink = 1; }
//                                     else { currentLink++; }
//                                     selectImageToggle();
//                                 });
//                             }
//                             else
//                             {
//                                 $('#news-link-generation').hide();
//                                 $('#news-summary').hide();
//                             }
//                             currentURL = text;
//                         },
//                         error: null
//                     });
//                 }
//                 else
//                 {
//                     $('#news-link-generation').hide();
//                     $('#news-summary').hide();
//                 }
//                 // Simulate a real ajax call
//                 setTimeout(function() { isLoading = false; }, delay);
//             }, delay);
//         }
//     });

//     /**
//      * Handles selecting topic image for content creation
//      */
//     $(".create-topic-img").click(function(event)
//     {

//         var wrapper = $(this).parents(".topic-icon-wrapper");
//         var icons_wrapper = wrapper.parents(".topic-icons-wrapper");

//         icons_wrapper.find('.topic-radio').attr('checked',false);

//         if (!wrapper.hasClass('chosen'))
//         {
//             wrapper.find(".topic-radio").attr("checked",true);
//         }
//         toggleTopicSingle(wrapper);
//     });

//     function clearPetitionErrors()
//     {
//         $("#errors-title").empty();
//         $("#errors-summary").empty();
//         $("#errors-full_text").empty();
//         $("#errors-topic").empty();
//         $("#errors-non_field").empty();
//     }

//     /* post to group visual */
//     $(".share_group_box").click(function(event) {
//         event.preventDefault();
//         defaultClickSingle($(this), $(".share_group_box"));
//     });
// }

// var my_lockout_boolean = false;
// function lockoutFunction(fun, args) {
//     if (!my_lockout_boolean) {
//         my_lockout_boolean = true;
//         fun.apply(undefined, args);
//         setTimeout(function() {
//             my_lockout_boolean = false;
//         }, 6000);
//     }
// }


// /***********************************************************************************************************************
//  *
//  *      ~Histogram
//  *
//  **********************************************************************************************************************/
// var histogram = new Object();

// function refreshHistogramData(data) {

//     histogram.total += data.total;
//     histogram.identical += data.identical;
//     histogram.identical_uids.push.apply(histogram.identical_uids, data.identical_uids);

//     $.map(data.buckets, function(item, key) {

//         var bar = $(".bar[data-bucket=" + key + "]");

//         bar.children('.red_bar').css("background-color",data.color);
//         $('.histogram-footer').css("background-color",data.color);
//         $('.histogram-wrapper').css("border-color",data.color);

//         var num = bar.data('num') + item.num;
//         bar.data('num', num);
//         if (num == 1) {
//             var mouseover = String(num) + " person.";
//         }
//         else {
//             var mouseover = String(num) + " people.";
//         }
//         bar.find(".red_bar").attr("data-original-title", mouseover);

//         if (histogram.total != 0) {
//             var percent = (num / histogram.total)*100;
//         }
//         else {
//             var percent = 0;
//         }
//         bar.data("percent", percent);

//         var bucket_uids = histogram.bucket_uids[parseInt(key)];
//         bucket_uids.push.apply(bucket_uids, item.u_ids);
//     });
// }

// function renderHistogram() {

//     if (histogram.which == 'mini') {
//         $(".bar").each(function(index, element) {
//             var percent = $(this).data("percent");
//             var total_height = 200;
//             var zero_height = 5;
//             var height = zero_height+((total_height-zero_height)*(percent/100));
//             $(this).find(".white_bar").css("height", total_height-height);
//             $(this).find(".red_bar").css("height", height);
//         });
//     }

//     else {
//         $(".bar").each(function(index, element) {
//             // width and position
//             var total_width = 850;
//             var margin_left = 15;
//             var margin_space = margin_left * histogram.resolution;
//             var width = (total_width-margin_space) / histogram.resolution;
//             $(this).css("width", width);
//             $(this).css("margin-left", margin_left);
//             $(this).find(".red_bar").css("width", width);

//             // height
//             var percent = $(this).data("percent");
//             var total_height = 300;
//             var zero_height = 5;
//             var height = zero_height+((total_height-zero_height)*(percent/100));
//             $(this).find(".white_bar").css("height", total_height-height);
//             $(this).find(".red_bar").css("height", height);
//         });
//     }

//     $(".histogram_count").text(histogram.total);
//     $(".histogram_identical").text(histogram.identical);

// }

// function loadHistogram() {

//     histogram = $(".histogram").data('metadata');
//     histogram.members_displayed = 0;
//     histogram.identical_displayed = 0;
//     updateHistogram(true);

//     $('.update_histogram').bindOnce("click.histogram", function(event) {
//         event.preventDefault();
//         updateHistogram();
//     });

//     $(".histogram-topic-img").bindOnce("click.histogram", function(event) {
//         var wrapper = $(this).parents(".topic-icon-wrapper");
//         if (wrapper.hasClass("chosen")) {
//             var alias = 'all';
//             var topic_text = "All Topics"
//         }
//         else {
//             var alias = wrapper.data('t_alias');
//             var topic_text = wrapper.data('t_text');
//         }
//         $(".histogram-topic").text(topic_text);
//         histogram.topic_alias = alias;
//         toggleTopicSingle(wrapper);
//         refreshHistogram();
//     });

//     $(".bar_label").bindOnce("click.histogram", function(event) {
//         if ($(this).hasClass("clicked")) {
//             histogram.current_bucket = -1;
//             $(this).removeClass("clicked");
//         }
//         else {
//             $(".bar_label").removeClass("clicked");
//             var bar = $(this).parents(".bar");
//             histogram.current_bucket = bar.data('bucket');
//             $(this).addClass("clicked");
//         }
//         histogram.members_displayed = 0;
//         getHistogramMembers();
//     });

//     $(".get_more_members").bindOnce("click.histogram", function(event) {
//         event.preventDefault();
//         getHistogramMembers();
//     });
// }

// function refreshHistogram() {

//     histogram.total = 0;

//     $(".bar").data('num', 0);
//     $.map(histogram.bucket_uids, function(item, key) {
//         histogram.bucket_uids[key] = [];
//     });
//     histogram.members_displayed = 0;

//     histogram.identical = 0;
//     histogram.identical_uids = [];
//     histogram.identical_displayed = 0;

//     updateHistogram(true);
// }

// function updateHistogram(recursive) {
//     ajaxPost({
//             data: {
//                 'action':'updateHistogram',
//                 'start': histogram.total,
//                 'num': histogram.increment,
//                 'topic_alias':histogram.topic_alias,
//                 'g_id': histogram.g_id,
//                 'resolution': histogram.resolution,
//                 'log-ignore': true
//             },
//             success: function(data)
//             {
//                 var returned =  eval('(' + data + ')');

//                 refreshHistogramData(returned);
//                 renderHistogram();
//                 getHistogramMembers();
//                 getIdenticalMembers();

//                 if (returned.total != 0 && recursive) {
//                     updateHistogram(true);
//                 }
//             }
//         }
//     );
// }

// var getHistogramMembersLockout = false;
// function getHistogramMembers() {
//     if (!getHistogramMembersLockout) {
//         getHistogramMembersHelper(false);
//     }
// }

// var getIdenticalMembersLockout = false;
// function getIdenticalMembers() {
//     if (!getIdenticalMembersLockout) {
//         getHistogramMembersHelper(true);
//     }
// }

// function getHistogramMembersHelper(identical) {

//     if (identical) {
//         var start = histogram.identical_displayed;
//         var u_ids = histogram.identical_uids;
//     }
//     else {
//         var start = histogram.members_displayed;
//         if (histogram.current_bucket != -1) {
//             var u_ids = histogram.bucket_uids[histogram.current_bucket];
//         }
//         else {
//             setHistogramExplanation();
//             return getAllGroupMembers(start, 10, histogram.g_id);
//         }
//     }

//     var replace = (start== 0);

//     if (replace && u_ids.length==0) {
//         if (identical) {
//             $(".identical-avatars").html("");
//         }
//         else {
//             setHistogramExplanation();
//             $(".members-avatars").html("");
//         }
//     }

//     if (start <= (u_ids.length-1)) {

//         if (identical) {
//             getIdenticalMembersLockout = true;
//         }
//         else {
//             getHistogramMembersLockout = true;
//         }

//         var end = Math.min(u_ids.length, start+10);
//         u_ids = u_ids.slice(start, end);

//         u_ids = JSON.stringify(u_ids);

//         ajaxPost({
//                 data: {
//                     'action':'getHistogramMembers',
//                     'u_ids': u_ids,
//                     'log-ignore': true
//                 },
//                 success: function(data)
//                 {
//                     var returned =  eval('(' + data + ')');

//                     if (identical) {
//                         var $wrapper = $(".identical-avatars");
//                         histogram.identical_displayed += returned.num;
//                         getIdenticalMembersLockout = false;
//                     }
//                     else {
//                         var $wrapper = $(".members-avatars");
//                         histogram.members_displayed += returned.num;
//                         getHistogramMembersLockout = false;
//                         setHistogramExplanation();
//                     }

//                     if (replace) {
//                         $wrapper.html(returned.html);
//                     }
//                     else {
//                         $wrapper.append(returned.html);
//                     }
//                     loadHoverComparison();
//                 },
//                 error: function(error, textStatus, errorThrown)
//                 {
//                     $('body').html(error.responseText);
//                 }
//             }
//         );
//     }
// }

// function setHistogramExplanation() {
//     var lower = histogram.current_bucket;
//     if (lower != -1) {

//         var inc = 100 / histogram.resolution;
//         var higher = lower + inc;
//         var message = String(lower) + '-' + String(higher) + "% similar to you";
//     }
//     else {
//         var message = "";
//     }
//     $(".in_percentile").html(message);
// }

// function getAllGroupMembers(start, num, g_id) {

//     var replace = (start== 0);
//     getHistogramMembersLockout = true;

//     ajaxPost({
//         data: {
//             'action':'getAllGroupMembers',
//             'start':start,
//             'num':num,
//             'g_id':g_id,
//             'log-ignore': true
//         },
//         success: function(data)
//         {
//             var returned =  eval('(' + data + ')');

//             var $wrapper = $(".members-avatars");
//             histogram.members_displayed += returned.num;
//             getHistogramMembersLockout = false;

//             if (replace) {
//                 $wrapper.html(returned.html);
//             }
//             else {
//                 $wrapper.append(returned.html);
//             }
//             loadHoverComparison();
//         },
//         error: function(error, textStatus, errorThrown)
//         {
//             $('body').html(error.responseText);
//         }
//     });
// }


// /***********************************************************************************************************************
//  *
//  *      ~Match page
//  *
//  **********************************************************************************************************************/
// var match_hover_off = true;
// var match_autoswitch;
// var match_latitude;
// var match_longitude;
// var match_state;
// var match_district;
// var match_location = false;
// function loadNewMatch() {

//     swapFeatured(match_current_section);

//     $('.match-item').hoverIntent(
//         function() {
//             swapInHover($(this));
//         },
//         function() {
//         });

//     /*
//      clearInterval(match_autoswitch);
//      match_autoswitch= setInterval(function()
//      {
//      if (match_hover_off) {
//      swapFeatured("right");
//      }

//      }, 10000); */

//     $('body').bindOnce("click.auto", function(event) {
//         clearInterval(match_autoswitch);
//     });

//     $("#match-arrow-right").click(function(event) {
//         swapFeatured("right");
//     });
//     $("#match-arrow-left").click(function(event) {
//         swapFeatured("left");
//     });

//     $("#match-mid-content").hover(
//         function() {
//             match_hover_off = false;
//         },
//         function() {
//             match_hover_off = true;
//         }
//     );

//     $(".circle-div").click(function(event) {
//         swapFeatured($(this).data('sequence'));
//     });

//     $(".find_out_now").click(function(event) {
//         event.preventDefault();
//         submitAddress($(this).parents(".address-box"));
//     });

//     $('div.first-login-modal div.modal-close').bindOnce('click', function() {
//         alert('clicky');
//         $('div.first-login-modal').hide();
//     });

//     bindCloseFirstLoginModal();
// }

// function submitAddress(wrapper) {
//     var address = wrapper.find(".address-input").val();
//     var city = wrapper.find(".city-input").val();
//     var zip = wrapper.find(".zip-input").val();
//     var state = wrapper.find(".state-input").val();
//     ajaxPost({
//         data: {
//             'action':'submitAddress',
//             'address':address,
//             'city':city,
//             'zip':zip,
//             'state':state
//         },
//         success: function(data)
//         {
//             if( data == 'success' )
//             {
//                 location.reload();
//                 $('#address_input_error').hide();
//             }
//             else
//             {
//                 $('#address_input_error').html(data);
//                 $('#address_input_error').fadeIn(300);
//             }
//         },
//         error: function(error, textStatus, errorThrown)
//         {
//             $('body').html(error.responseText);
//         }
//     });
// }

// function submitZip(zip, successCallback, errorCallback) {
//     ajaxPost({
//         data: {
//             'action': 'submitAddress',
//             'zip': zip
//         },
//         success: function(data)
//         {
//             if (data=='success') {
//                 successCallback();
//             } else {
//                 errorCallback(data);
//             }
//         },
//         error: function(error, textStatus, errorThrown)
//         {
//             $('body').html(error.responseText);
//         }
//     });
// }

// var match_current_section;
// function swapFeatured(direction) {
//     if (direction=='right') {
//         var match_next_section = nextSection();
//     }
//     else {
//         if (direction=='left') {
//             var match_next_section = previousSection();
//         }
//         else {
//             var match_next_section = direction;
//         }
//     }
//     var current = getSection(match_current_section);
//     var next = getSection(match_next_section);
//     current.hide();
//     next.show();
//     var current_circle = getCircle(match_current_section);
//     var next_circle = getCircle(match_next_section);
//     current_circle.removeClass("circle-div-red").addClass("circle-div-gray");
//     next_circle.removeClass("circle-div-gray").addClass("circle-div-red");
//     match_current_section = match_next_section;
//     if ((match_next_section==3) && match_location) {
//         loadGoogleMap();
//     }
// }

// function nextSection() {
//     if (match_current_section==3) {
//         var next_num = 0;
//     }
//     else {
//         var next_num = match_current_section + 1;
//     }
//     return next_num;
// }
// function previousSection() {
//     if (match_current_section==0) {
//         var next_num = 3;
//     }
//     else {
//         var next_num = match_current_section - 1;
//     }
//     return next_num;
// }

// function getSection(num) {
//     return $(".match-section[data-sequence=" + num + "]");
// }
// function getCircle(num) {
//     return $(".circle-div[data-sequence=" + num + "]");
// }

// function swapInHover(div) {
//     var item_url = div.attr('href');
//     ajaxPost({
//             data: {
//                 'action':'matchComparison',
//                 'item_url': item_url,
//                 'log-ignore': true
//             },
//             success: function(data)
//             {
//                 var $wrapper = $('.match-box-div-wrapper');
//                 //$wrapper.hide({effect:'slide',speed:2000,direction:'down'});
//                 $wrapper.promise().done(function() {
//                     var returned = eval('(' + data + ')');
//                     $wrapper.html(returned.html);
//                     //$wrapper.show({effect:'slide',speed:2000,direction:"up"});
//                 });
//             },
//             error: function(error, textStatus, errorThrown)
//             {
//                 $('body').html(error.responseText);
//             }
//         }
//     );
// }

// function loadGoogleMap()
// {
//     function createDistrictsOverlay(outlines_only, opacity, state, district)
//     {
//         return {
//             getTileUrl: function(coord, zoom)
//             {
//                 return "http://www.govtrack.us/perl/wms/wms.cgi?google_tile_template_values=" + coord.x + "," + coord.y + "," + zoom
//                     + "&LAYERS=cd-110" + (outlines_only ? "-outlines" : "")
//                     + (state ? ":http://www.rdfabout.com/rdf/usgov/geo/us/" + state
//                     + (!district ? "%25"
//                     : "/cd/110/" + district)
//                     : "")
//                     + "&FORMAT=image/png";
//             },
//             tileSize: new google.maps.Size(256,256),
//             minZoom: 2,
//             maxZoom: 28,
//             opacity: opacity,
//             isPng: true
//         };
//     }

//     var map;

//     function initialize()
//     {
//         var myOptions =
//         {
//             zoom: 10,
//             center: new google.maps.LatLng(match_latitude, match_longtitude),
//             mapTypeId: google.maps.MapTypeId.ROADMAP,
//             panControl: false,
//             zoomControl: true,
//             mapTypeControl: false,
//             scaleControl: true,
//             streetViewControl: false
//         };
//         map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

//         overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(false, .2, match_state, match_district));
//         map.overlayMapTypes.insertAt(0, overlayWMS);

//         overlayWMS = new google.maps.ImageMapType(createDistrictsOverlay(true, .7, match_state, match_district));
//         map.overlayMapTypes.insertAt(0, overlayWMS);
//     }

//     initialize();

// }



// /***********************************************************************************************************************
//  *
//  *      ~Content Privacy
//  *
//  **********************************************************************************************************************/

// function bindChangeContentPrivacy() {

//     $('div.change-privacy').bindOnce('click.changeprivacy', function() {
//         var content_id = $(this).data('content_id');
//         var meDiv = $(this);
//         $(this).tooltip('hide');
//         ajaxPost({
//             data: {
//                 'action': 'changeContentPrivacy',
//                 'content_id': content_id
//             },
//             success: function(data) {
//                 var returned = eval('('+data+')');
//                 if(returned.error) {
//                     alert("Error: "+data.error);
//                 } else {
//                     meDiv.parent().html(returned.html);
//                 }
//                 bindChangeContentPrivacy();
//                 bindTooltips();
//             },
//             error: function(error, textStatus, errorThrown)
//             {
//                 $('body').html(error.responseText);
//             }
//         });
//     });
// }

// /***********************************************************************************************************************
//  *
//  *      ~First login experience
//  *
//  **********************************************************************************************************************/

// function setFirstLoginStage(stage, success) {
//     success = typeof success !== 'undefined' ? success : function() {};
//     ajaxPost({
//         data: {action: 'setFirstLoginStage', stage: stage},
//         success: success
//     });
// }

// function bindCloseFirstLoginModal() {
//     $('div.first-login-modal div.modal-close').bindOnce('click', function() {
//         $('div.first-login-modal').hide();
//     });
// }


// /***********************************************************************************************************************
//  *
//  *      ~Footer
//  *
//  **********************************************************************************************************************/

// function showFooter() {
//     $('footer').show();

//     $('.footer_invite').bindOnce('click.footer_invite', function (event)
//     {
//         event.preventDefault();
//         var wrapper = $('#left-side-wrapper-invite');
//         leftSideToggle(wrapper);
//     });
//     $('.footer_feedback').bindOnce('click.footer_feedback', function (event)
//     {
//         event.preventDefault();
//         var wrapper = $('#left-side-wrapper-feedback');
//         leftSideToggle(wrapper);
//     });
// }

// function hideFooter() {
//     $('footer').hide();
// }


// /***********************************************************************************************************************
//  *
//  *      ~Login page
//  *
//  **********************************************************************************************************************/
// var login_state;
// function loadLogin() {
//     if (login_state == 'login_error') {
//         $(".sign_in_dialogue").show();
//     }

//     $(".no_login_link").bindOnce("click.no_login_link", function(e)
//     {
//         e.preventDefault();
//         var target = $(this).data('link');

//         $('#modal_browse_anyways_login').bindOnce("click.browse_anyways_modal", function(e)
//         {
//             e.preventDefault();
//             window.location = target;
//         });

//         $('.no_login_modal').show();
//         $('.overdiv').show();
//     });

//     $('.overdiv').bindOnce('click.no_login_modal_hide' , function(e)
//     {
//         $(this).hide();
//         $('.no_login_modal').hide();
//     });

//     $('.no_login_modal_close').bindOnce('click.no_login_modal_close' , function(e)
//     {
//         $('.overdiv').hide();
//         $('.no_login_modal').hide();
//     });
// }


// /***********************************************************************************************************************
//  *h
//  *      ~Blog
//  *
//  **********************************************************************************************************************/
// function loadBlog() {
//     alert("blog!");
// }


// /***********************************************************************************************************************
//  *
//  *      -Legislation checkboxes
//  *
//  **********************************************************************************************************************/

// function hiddenFilters() {
//     $('#session_filter').hide(0);
//     $('#type_filter').hide(0);
//     $('#introduced_filter').hide(0);
//     $('#sponsor_filter').hide(0);
// }

// function checkboxClick1() {
//     $('.col1').click(function(){
//         if($(this).hasClass("unchecked"))
//         {
//             $('#leg_session').attr('checked',true);
//             $(this).removeClass("unchecked");
//             $(this).addClass("checked");
//             $('#type_filter').hide('fast');
//             $('#introduced_filter').hide('fast');
//             $('#sponsor_filter').hide('fast');
//             $('#session_filter').show('fast');
//         }
//         else
//         {
//             $('#leg_session').attr('checked',false);
//             $(this).addClass("unchecked");
//             $(this).removeClass("checked");
//             $('#session_filter').hide('');
//         }
//     });
// }

// function checkboxClick2() {
//     $('.col2').click(function(){
//         if($(this).hasClass("unchecked"))
//         {
//             $('#leg_type').attr('checked',true);
//             $(this).removeClass("unchecked");
//             $(this).addClass("checked");
//             $('#session_filter').hide('fast');
//             $('#introduced_filter').hide('fast');
//             $('#sponsor_filter').hide('fast');
//             $('#type_filter').show('fast');
//         }
//         else
//         {
//             $('#leg_type').attr('checked',false);
//             $(this).addClass("unchecked");
//             $(this).removeClass("checked");
//             $('#type_filter').hide('');
//         }
//     });
// }

// function checkboxClick3() {
//     $('.col3').click(function(){
//         if($(this).hasClass("unchecked"))
//         {
//             $('#leg_introduced').attr('checked',true);
//             $(this).removeClass("unchecked");
//             $(this).addClass("checked");
//             $('#session_filter').hide('fast');
//             $('#type_filter').hide('fast');
//             $('#sponsor_filter').hide('fast');
//             $('#introduced_filter').show('fast');
//         }
//         else
//         {
//             $('#leg_introduced').attr('checked',false);
//             $(this).addClass("unchecked");
//             $(this).removeClass("checked");
//             $('#introduced_filter').hide('');
//         }
//     });
// }

// function checkboxClick4() {
//     $('.col4').click(function(){
//         if($(this).hasClass("unchecked"))
//         {
//             $('#leg_sponsor').attr('checked',true);
//             $(this).removeClass("unchecked");
//             $(this).addClass("checked");
//             $('#session_filter').hide('fast');
//             $('#type_filter').hide('fast');
//             $('#introduced_filter').hide('fast');
//             $('#sponsor_filter').show('fast');
//         }
//         else
//         {
//             $('#leg_sponsor').attr('checked',false);
//             $(this).addClass("unchecked");
//             $(this).removeClass("checked");
//             $('#sponsor_filter').hide('');
//         }
//     });
// }

























