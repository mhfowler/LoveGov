/***********************************************************************************************************************
 * .js for actions on content
 *
 ***********************************************************************************************************************/

// global variables
var content_id;

/**
 *   Document Preparation
 */
$(document).ready(function(){
    content_id = $("#actions_variables").children("#content_id").val();
});

/**
 *   Choose new content to linkfrom.
 */
$("#linkfrom").click(function() {
        $.post('/action/', {'action':'linkfrom','c_id':content_id },
// call back function
function(data) {
        location.reload();
        });
});

/**
 *  Link current linkfrom content to this content.
 */
$("#linkto").click(function() {
        $.ajax({
            url:'/action/',
            type: 'POST',
            data: {'action':'linkto','c_id': content_id},
success: function(data){
        location.reload();
        },
error: function(jqXHR, textStatus, errorThrown){
        $('.errors_div').html(jqXHR.responseText);
        }
});
});

/**
 *   Like this content.
 */
$("#contentlike").click(function() {
        $.ajax({
            url:'/action/',
            type: 'POST',
            data: {'action':'vote','c_id':content_id, 'vote':'L'},
success: function(data){
        location.reload();
        },
error: function(jqXHR, textStatus, errorThrown){
        $('body').replaceWith(jqXHR.responseText);
        }
});
});

/**
 *  Dislike this content.
 */
$("#contentdislike").click(function(){
        $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
// call back function
function(data) {
        location.reload();
        });
});

/**
 *   Share this content.
 */
$("#share").click(function(){
        $.post('/action/', {'action':'share','c_id':content_id},
// call back function
function(data) {
        location.reload();
        });
});

/**
 *  Follow this content.
 */
$("#follow").click(function(){
        $.post('/action/', {'action':'follow','c_id':content_id},
// call back function
function(data) {
        location.reload();
        });
});

/**
 *   Follow this content.
 */
$("#deletecontent").click(function(){
        $.post('/action/', {'action':'delete','c_id':content_id},
// call back function
function(data) {
        location.reload();
        });
});

/**
 * For answering question.
 */
$("#answerform").submit(function(event){
    event.preventDefault();
    var choice = $('input:radio[name=choice]:checked').val();
    var q_id = content_id;
    var exp = $("#explanation").val();
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'answer','q_id': q_id,'choice':choice,'explanation':exp},
        success: function(data) {
            //var dict = jQuery.parseJSON(data); // why did this suddenly stop working?
            var dict = eval('(' + data + ')');
            window.location = dict.url;
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});

