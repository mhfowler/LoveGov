/***********************************************************************************************************************
 * .js for groups
 *
 ***********************************************************************************************************************/

// global variables
var group_id;

/**
 *   Document Preparation
 */
$(document).ready(function(){
    group_id = $("#group_variables").children("#g_id").val();
});

/**
 *  Underlines on mouseover.
 */
$("#postto").hover(function (){
            $(this).css("text-decoration", "underline");
        },function(){
            $(this).css("text-decoration", "none");
        }
);

/**
 *   Post content to group from linkfrom... also links linkfrom to group.
 */
$("#postto").click(function() {
    $.post('/action/', {'action':'linkto','c_id':group_id},
            // call back function
            function(data) {
                var dict = jQuery.parseJSON(data);
                var from_id = dict.from_id;
                // post from content to group it was linked to
                postToGroup(from_id);
            });
});
/**
 *   Helper method for post-to.
 */
function postToGroup(content_id){
    $.post('/action/', {'action':'posttogroup','c_id':content_id, 'g_id':group_id},
            // call back function
            function(data) {
                location.reload();
            });
}

/**
 *  Join group
 */
$(".join").click(function(){
    $.post('/action/', {'action':'join','g_id':group_id},
            // call back function
            function() {
                location.reload();
            });
});

/**
 *   Leave group
 */
$(".leave").click(function(){
    $.post('/action/', {'action':'leave','g_id':group_id},
            // call back function
            function() {
                location.reload();
            });
});

/**
 *   Update group view.
 */
$(".updateGroupView").click(function(){
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':"updateGroupView",'g_id':group_id},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});


/**
 * Create a motion.
 */
$(".motionform").submit(function(){
    event.preventDefault();
    var motion_text = $("#motion").val();
    createMotion(group_id, motion_text, "O");
});

/**
 * This is real function, which creates a motion for a group.
 * @param group_id
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
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}