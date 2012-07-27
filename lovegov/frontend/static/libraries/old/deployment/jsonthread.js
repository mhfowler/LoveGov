var threadHTML = $('#threadHTML');

function loadJSONThread()
{
    reloadThread($("#threadJSON").text());
    // submit new comment
    $("#commentform").submit(function(event)
    {
        event.preventDefault();
        var comment_text = $(this).children(".comment-text").val();
        $(this).children(".comment-text").val("");
        var comment_text_length = comment_text.length;
        if (comment_text_length <= 1000)
        {
            var content_id = $("#content_id").val();
            $.ajax({
                url:'/action/',
                type: 'POST',
                data: {'action':'comment','c_id': content_id,'comment':comment_text},
                success: function(data)
                {
                    reloadThread(data);
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    alert("Oops we made an error.  Try submitting again.")
                }
            });
        }
        else
        {
            alert("Please limit your response to 1000 characters.  You have currently typed " + comment_text_length + " characters.");
        }
    });
}

function reloadThread(data)
{
    var thread = eval('(' + data + ')');
    threadHTML.empty();
    initializeThread(thread);
}

function initializeThread(thread)
{
    printThread(thread,0);
    // submit answer
    $("#submitquestion").click(function(event)
    {
        event.preventDefault();
        $("#questionform").submit();
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
                reloadThread(data);
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
                reloadThread(data);
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
                data: {'action':'comment','c_id': content_id,'comment':comment_text},
                success: function(data)
                {
                    reloadThread(data);
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    alert("failed to submit");
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
}


function printThread(thread, depth)
{
    if (thread.length >0)
    {
        for (var i=0;i<thread.length;i++)
        {
            var startDiv =  "<div class='feed-item' style='margin-left:" + (thread[i].depth*30) + "px;width:" + (650 - (thread[i].depth*30)) + "px;'>" + "<div class='feed-item-username'>";
            var state;
            if (thread[i].comment_active) { state = thread[i].creator_name + "</div>" + thread[i].comment_text }
            else { state = "deleted</div>deleted" }
            var reply = "<div class='seemore reply'>reply</div>";
            var footer = "<div class='comment-footer'><div class='metadata'>";
            if (thread[i].comment_status > 0)
            {
                footer += "+" + thread[i].comment_status;
            }
            else if (thread[i].comment_status == 0)
            {
                footer += "0";
            }
            else
            {
                footer += "-" + thread[i].comment_status;
            }
            footer += "</div>";
            var dislike = "<div class='metadata commentdislike";
            if (thread[i].my_vote == -1) { dislike+= " voted'>"; }
            else { dislike+="'>";}
            dislike+= "down</div>";
            var like = "<div class='metadata commentlike";
            if (thread[i].my_vote == 1) { like+= " voted'>"; }
            else { like+="'>";}
            like+= "up</div></div>";

            var form = "<form class='replyform' name='postcomment' action='/comment/' method='post'>" +
            "<textarea class='comment-text' type='text' name='comment' style='height:125px;width:" + (650 - (thread[i].depth*30)) + "px;'>" + "what's your opinion?</textarea>" +
            "<input class='hidden_id' type='hidden' name='c_id' value='" + thread[i].comment_id + "'/>" +
            "<input class='submit-comment' type='submit' value='Comment' /> </form>";

            threadHTML.append((startDiv + state + reply + footer + dislike + like + form));
            printThread(thread[i].childList,++depth);
        }
    }
}
