/***********************************************************************************************************************
 * .js for comment threads
 *
 ***********************************************************************************************************************/

/**
 * Actions get underlined on mouseover.
 */
$(".actions").children().hover(function (){
            $(this).css("text-decoration", "underline");
        },function(){
            $(this).css("text-decoration", "none");
        }
);

/**
 * Actions get underlined on mouseover.
 */
$(".actions2").hover(function (){
            $(this).css("text-decoration", "underline");
        },function(){
            $(this).css("text-decoration", "none");
        }
);

/**
 * Reply forms for comment toggle on click.
 */
$(".reply").click(function(){
    $(this).parent().next().toggle();
});

/**
 * Focusing on comment form makes initial text disappear.
 */
$("#comment_text").focus(function(event){
    if ($("#comment_text").val() == "...add comment")
    {
        $("#comment_text").val("")
    }
});

/**
 * Removing focus returns ...add comment value.
 */
$("#comment_text").focusout(function(event){
    if ($("#comment_text").val()=="")
    {
        $("#comment_text").val("...add comment");
    }
});

/**
 * Like button on comment.
 */
$(".commentlike").click(function(event){
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
// call back function
            function(data) {
                location.reload();
            });
});

/**
 * Dislike button on comment.
 */
$(".commentdislike").click(function(event){
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
// call back function
            function(data) {
                location.reload();
            });
});

/**
 * Comment delete.
 */
$(".commentdelete").click(function(){
    var content_id = $(this).parent().next().next().next().children(".hidden_id").val();
    $.post('/action/', {'action':'delete','c_id':content_id},
// call back function
            function(data) {
                location.reload();
            });
});


/**
 * Reply to comment
 */
$(".replyform").submit(function(event) {
    // stop form from submitting normally
    event.preventDefault();
    // get comment text and content id
    var comment_text = $(this).children(".comment_text").val();
    var content_id = $(this).children(".hidden_id").val();
    // Send the data using post
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});

/**
 * Submit new comment
 */
$("#commentform").submit(function(event) {
    // stop form from submitting normally
    event.preventDefault();
    // get comment text and content id
    var comment_text = $("#comment_text").val();
    var content_id = $("#content_id").val()
    // Send the data using post
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});

