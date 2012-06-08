/***********************************************************************************************************************
 * .js for profile
 *
 ***********************************************************************************************************************/

// global variables
var person_id;
var user_id;

/**
 * Doc Prep
 */
$(document).ready(function(){
    person_id = $("#profile_variables").children("#person_id").val();
    user_id = $("#profile_variables").children("#user_id").val();
});
/**
 * Invite user to debate inputted resolution... for testing.
 */
$(".resolutionform").submit(function(){
    event.preventDefault();
    var resolution = $("#resolution").val();
    inviteToDebate(person_id, resolution, "F");
});

/**
 * This is real function, which is an action for inviting someone to a debate.
 * @param person_id
 * @param resolution
 * @param type
 */
function inviteToDebate(person_id, resolution, type)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'invite_to_debate', 'to_invite':person_id, 'resolution':resolution, 'type':type},
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

/**
 * actions underline on hover
 */
$(".action").hover(function (){
            $(this).css("text-decoration", "underline");
        },function(){
            $(this).css("text-decoration", "none");
        }
);


/**
 * Friend this user.
 */
$("#connect").click(function(){
    $.post('/action/', {'action':'friend','p_id':person_id,'type':'C'},
            // call back function
            function(data) {
                location.reload();
            });
});

/**
 * Follow this user.
 */
$("#follow").click(function(){
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'userfollow', 'p_id':person_id},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});

/**
 * Stop following this user.
 */
$("#stopfollowing").click(function(){
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'stopfollow', 'p_id':person_id},
        success: function(data) {
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});


/**
 * View comparison of yourself with this user.
 */
$("#compare").click(function(){
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'viewCompare', 'a_id':user_id, 'b_id':person_id},
        success: function(data) {
            var dict = eval('(' + data + ')');
            window.location = dict.url;
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});