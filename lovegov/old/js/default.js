/***********************************************************************************************************************
 * .js for default base.
 *
 ***********************************************************************************************************************/

// global variables
var path;

/**
 *   Document Preparation
 */
$(document).ready(function()
{
    path = $("#default_variables").children("#pagepath").val();
    var csrf = $("#default_variables").children("#csrftoken").val();
    // To bypass csrf protection on ajax posts.
    $.ajaxSetup({
            data: {csrfmiddlewaretoken: csrf }});
});

/**
 * Action get underlined on mouseover.
 */
$(".action").hover(function (){
            $(this).css("text-decoration", "underline");
        },function(){
            $(this).css("text-decoration", "none");
        }
);

/**
 *   Go to private mode.
 */
$(".private").click(function(){
        $.ajax({
            url:'/action/',
            type: 'POST',
            data: {'action':'setprivacy','mode':'PRI','path':path},
success: function(data){
        location.reload();
        },
error: function(jqXHR, textStatus, errorThrown){
        $('.errors_div').html(jqXHR.responseText);
        }
});
});

/**
 *   Go to public mode.
 */
$(".public").click(function()
{
        $.post('/action/', {'action':'setprivacy','mode':'PUB','path':path},
        // call back function
        function() {
            location.reload();
        });
});

/**
 *   Go to public mode.
 */
$(".followers").click(function()
{
    $.post('/action/', {'action':'setprivacy','mode':'FOL','path':path},
            // call back function
            function() {
                location.reload();
            });
});

/**
 *   Update feed with new best content you haven't seen.
 */
$(".updatefeed").click(function(){
        $.post('/action/', {'action':'updatefeed'},
// call back function
function() {
        location.reload();
        });
});

/**
 *   Get all new content for feed.
 */
$(".refreshfeed").click(function(){
        $.post('/action/', {'action':'refreshfeed'},
// call back function
function() {
        location.reload();
        });
});

/**
 *   Submit feedback about site.
 */
$(".feedback").submit(function(event){
        event.preventDefault();
        var feedtext = $(this).children(".myfeedback").val();
        $.post('/action/', {'action':'feedback', 'text':feedtext, 'path': path},
// call back function
function(data) {
        $(".myfeedback").val(data);
        });
});












