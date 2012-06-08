// submit answer
$("#submitquestion").click(function(event)
{
    event.preventDefault();
    $("#questionform").submit();
});

// nextquestion click functions replaces current question with new random question
$("#nextquestion").click(function(event) {
    event.preventDefault();
    ajaxQuestion(-1);
});

// toggle reply form for comment
$(".reply").click(function()
{
    $(this).parent().children('.replyform').toggle();
});


// like comment
$(".commentlike").click(function(event)
{
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
        function(data)
        {
            location.reload();
        });
});

// dislike comment
$(".commentdislike").click(function(event)
{
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
        function(data)
        {
            location.reload();
        });
});

// delete comment
$(".commentdelete").click(function()
{
    var content_id = $(this).parent().next().next().next().children(".hidden_id").val();
    $.post('/action/', {'action':'delete','c_id':content_id},
        function(data)
        {
            location.reload();
        });
});


// reply to comment
$(".replyform").submit(function(event)
{
    event.preventDefault();
    var comment_text = $(this).children(".comment-text").val();
    var comment_text_length = comment_text.length;
    if (comment_text_length <= 1000)
    {
        var content_id = $(this).children(".hidden_id").val();
        $.ajax({
            url:'/action/',
            type: 'POST',
            data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
            success: function(data){
                location.reload();
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $('body').replace(jqXHR.responseText);
            }
        });
    }
    else
    {
        alert("Please limit your response to 1000 characters.  You have currently typed " + comment_text_length + " characters.");
    }
});

$(".comment-text").click(function()
{
    if ($(this).val() == "what's your opinion?")
    {
        $(this).val("");
    }
});

$(".comment-text").bind("clickoutside", function(event)
{
    if ($(this).val()=="")
    {
        $(this).val("what's your opinion?");
    }
    $(this).blur();
});

var preventDoubleClick = false;
$('.submit-comment').click(function(event)
{
    if (preventDoubleClick)
    {
        event.preventDefault();
    }
    preventDoubleClick = true;
});

// submit new comment
$("#commentform").submit(function(event)
{
    event.preventDefault();
    var comment_text = $(this).children(".comment-text").val();
    var comment_text_length = comment_text.length;
    if (comment_text_length <= 1000)
    {
        var content_id = $("#content_id").val();
        $.ajax({
            url:'/action/',
            type: 'POST',
            data: {'action':'postcomment','c_id': content_id,'comment':comment_text},
            success: function(data){
                location.reload();
            },
            error: function(jqXHR, textStatus, errorThrown){
                $('body').replace(jqXHR.responseText);
            }
        });
    }
    else
    {
        preventDoubleClick = false;
        alert("Please limit your response to 1000 characters.  You have currently typed " + comment_text_length + " characters.");
    }
});


// ajax question replaces current content focus with returned html for posted question
function ajaxQuestion(q_id) {
    $.ajax({
        url:'/ajax/',
        type: 'POST',
        data: {'get':'question','q_id':q_id},
        success: function(data){
            var returned = eval('(' + data + ')');
            $("#content-div").html(returned.html);
            History.pushState({state:1}, returned.title, returned.url);
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('body').html(jqXHR.responseText);
        }
    });
}
