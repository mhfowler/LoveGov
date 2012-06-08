/* feed buttons */
var how_many = 5;
var feed_type = 'H';

function loadHomeFeed()
{
    $(".feed").hide();
    $("#hotfeed").show();
    $("#hot_button").css('background-color','#f0503b');

    // set heart buttons
    heartButtons();
    // heart display
    heartDisplay();

    /* set feed buttons */
    $('#new_button').click(function() {
        clearButtons();
        $("#newfeed").show();
        $("#new_button").css('background-color','#f0503b');
        feed_type = 'N';
    });

    $('#hot_button').click(function() {
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

    $(window).scroll(function()
    {
        if  ($(window).scrollTop() == $(document).height() - $(window).height())
        {
            var more_button;
            if ($('#newfeed').css("display")=="block")
            {
                more_button = $('#newfeed').find('.more-button');
            }
            else if ($('#hotfeed').css("display")=="block")
            {
                more_button = $('#hotfeed').find('.more-button');
            }
            else if ($('#bestfeed').css("display")=="block")
            {
                more_button = $('#bestfeed').find('.more-button');
            }
            getMore(more_button);
        }
    });
}

/* heart stuff */
function heartButtons()
{

    var container = $(".not-processed");
    container.hide();

    container.find(".heart").hover(
        function() {
            $(this).parent().children(".grey").hide();
            $(this).parent().children(".blue").show();

        },
       function() {
           var blue = $(this).parent().children(".blue");
           if (blue.hasClass("hide")) {
               blue.hide();
               $(this).parent().children(".grey").show();
               }
           }
       );

    container.find(".plus").click(function() {
        var content_id = $(this).parent().siblings(".c_id").val();
        var v='L';
        vote($(this),content_id, v);
    });

    container.find(".minus").click(function() {
        var content_id = $(this).parent().siblings(".c_id").val();
        var v='D';
        vote($(this),content_id, v);
    });

    container.removeClass("not-processed");
    container.fadeIn('slow');
}

function heartDisplay()
{
    $(".hide").hide();
    $(".show").show();
}

function vote(div, content_id, v)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'vote','c_id':content_id, 'vote':v},
        success: function(data){
            var returned = eval('(' + data + ')');
            var my_vote = parseInt(returned.my_vote);
            var status = returned.status;
            if (my_vote==1) {
                like(div);
            }
            if (my_vote==0) {
                neutral(div);
            }
            if (my_vote==-1) {
                dislike(div);
            }
            heartDisplay();
            // change status
            div.parent().parent().find(".post-score").text(status);
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload()
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
function clearButtons() {
    $(".feed").hide();
    $(".dialogue-buttons").css('background-color','#ccc');
    $(".dialogue-buttons:hover").css('background-color','#f0503b');
}

$(".more-button").click(function(event) {
   event.preventDefault();
   getMore($(this));
});


function getMore(div) {
    var len = div.siblings(".length");
    var s = parseInt(len.val());
    len.val(s + how_many);
    ajaxFeed(feed_type, s);
}


function scrollHandler(event, direction) {
    alert("triggered");
    getMore($(this));
}

function ajaxFeed(feed_type, start)
{
    $.ajax({
        url:'/ajax/feed',
        type: 'POST',
        data: {'feed_type':feed_type,'start':start, 'how_many':how_many},
        success: function(data){
            var returned = eval('(' + data + ')');
            var feed = returned.feed;
            // append new items
            $("#" + feed_type).append(feed);
            // update position in feed
            $("#length" + feed_type).val(returned.position);
            // set heart buttons
            heartButtons();
            heartDisplay();
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert("failure");
            $("body").html(jqXHR.responseText);
        }
    });
}

