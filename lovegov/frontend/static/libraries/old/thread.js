// toggle reply form for comment
$(".reply").click(function(){
    $(this).parent().next().toggle();
});

// focus on comment
$("#comment_text").focus(function(event){
    if ($("#comment_text").val() == "...add comment")
    {
        $("#comment_text").val("")
    }
});

// remove focus from comment
$("#comment_text").focusout(function(event){
    if ($("#comment_text").val()=="")
    {
        $("#comment_text").val("...add comment");
    }
});

// like comment
$(".commentlike").click(function(event){
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
            function(data) {
                location.reload();
            });
});

// dislike comment
$(".commentdislike").click(function(event){
    event.preventDefault();
    var content_id = $(this).parent().next().children(".hidden_id").val();
    $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
            function(data) {
                location.reload();
            });
});

// delete comment
$(".commentdelete").click(function(){
    var content_id = $(this).parent().next().next().next().children(".hidden_id").val();
    $.post('/action/', {'action':'delete','c_id':content_id},
            function(data) {
                location.reload();
            });
});


// reply to comment
$(".replyform").submit(function(event) {
    event.preventDefault();
    var comment_text = $(this).children(".comment_text").val();
    var content_id = $(this).children(".hidden_id").val();
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'comment','c_id': content_id,'comment':comment_text},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('body').replace(jqXHR.responseText);
        }
    });
});

// submit new comment
$("#commentform").submit(function(event) {
    event.preventDefault();
    var comment_text = $("#comment_text").val();
    var content_id = $("#content_id").val()
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'comment','c_id': content_id,'comment':comment_text},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('body').replace(jqXHR.responseText);
        }
    });
});
