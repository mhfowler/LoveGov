/**
 * CSRF prep for ajax posts.
 */
$(document).ready(function()
{
    var csrf = $("#csrftoken").val();
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: csrf }});
});

/**
 * Creates a motion for a group
 * @param g_id
 * @param motion_text
 * @param type
 */
function createMotion(g_id, motion_text, type)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'create_motion', 'g_id':g_id, 'motion_text':motion_text, 'type':type},
        success: function(data) {
            // redirect to debate
            var dict = eval('(' + data + ')');
            window.location = dict.url;
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload();
        }
    });
}

/**
 * Requests to follow inputted user
 * @param person_id
 */
function userFollowRequest(person_id)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'userfollow', 'p_id':person_id},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload();
        }
    });
}

/**
 * If you are following someone, this action causes you to stop following
 * the inputted person.
 * @param person_id
 */
function userFollowStop(person_id)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'stopfollow', 'p_id':person_id},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload();
        }
    });
}

/**
 * Requests to follow inputted user
 * @param person_id
 * @param response : 'Y' or 'N'
 */
function userFollowResponse(person_id, response)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'followresponse', 'p_id':person_id, 'response':response},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload();
        }
    });
}

/**
 * Votes on inputted content with inputted vote.
 * @param content_id
 * @param v : 'L' or 'D'
 */
function vote(content_id, v)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'vote','c_id':content_id, 'vote':v},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload()
        }
    });
}

/**
 * Deletes inputted piece of content.
 * @param content_id
 */
function deleteContent(content_id)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'delete','c_id':content_id},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            location.reload()
        }
    });
}