/***********************************************************************************************************************
 * .js for persistent debate.
 *
 ***********************************************************************************************************************/
/***********************************************************************************************************************
 * Page specific variables and style.
 *
 ***********************************************************************************************************************/

// global variables
var d_id;

/**
 * assign global variables values.
 */
$(document).ready(function(){
    d_id = $("#debate_variables").children("#d_id").val();
});

/***********************************************************************************************************************
 * UI  [TEST]
 *
 ***********************************************************************************************************************/

$("#vote_affirmative").click(function() {
    debateVote(d_id, 1);
});

$("#vote_negative").click(function() {
    debateVote(d_id, -1);
});

$("#message_form").submit(function() {
    event.preventDefault();
    m = $(this).children(".message").val();
    debateMessage(d_id, m);
});

$("#accept_affirmative").click(function() {
    acceptInvitation(d_id, 1);
});

$("#accept_negative").click(function() {
    acceptInvitation(d_id, -1);
});

$(".reject").click(function() {
    rejectInvitation(d_id);
});

$("#persistent_update").click(function(){
    debateUpdate(d_id);
});

/***********************************************************************************************************************
 * ACTIONS [REAL]
 *
 ***********************************************************************************************************************/


/**
 * Real function for user to vote who they think won the debate.
 * @param debate_id
 * @param vote
 */
function debateVote(debate_id, vote)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'persistent_vote', 'd_id':debate_id, 'vote':vote},
        success: function(data) {
            location.reload()
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}

/**
 * Real function for debater to add message to debate.
 * @param debate_id
 * @param message
 */
function debateMessage(debate_id, message)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'persistent_message', 'd_id':debate_id, 'message':message},
        success: function(data) {
            location.reload()
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}


/**
 * Real function to accept invitation to debate.
 * @param debate_id
 * @param side
 */
function acceptInvitation(debate_id, side)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'persistent_accept', 'd_id':debate_id, 'side':side},
        success: function(data) {
            location.reload()
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}

/**
 * Real function to reject invitation to debate.
 * @param debate_id
 */
function rejectInvitation(debate_id)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'persistent_reject', 'd_id':debate_id},
        success: function(data) {
            location.reload()
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}

/**
 * updates debate, checks for winner, checks turn.. etc
 * @param debate_id
 */
function debateUpdate(debate_id)
{
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'persistent_update', 'd_id':debate_id},
        success: function(data) {
            location.reload()
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
}