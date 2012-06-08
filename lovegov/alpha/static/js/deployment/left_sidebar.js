/**
 * AAttaches the functionality the left sidebar
 */
function loadLeftSidebar()
{
    $('.create-img').click(function()
    {
        var parent = $(this).parent();
        if (parent.hasClass('clicked'))
        {
            parent.removeClass('clicked');
            if (parent.hasClass('create-wrapper-large'))
            {
                parent.animate({left:'-602px'},500);
            }
            else
            {
                parent.animate({left:'-492px'},500);
            }
            setTimeout(function()
            {
                parent.css({'z-index':'100'});
                parent.children('.create-img').css({'z-index':'101'});
            },500);
        }
        else
        {
            parent.addClass('clicked');
            parent.css({'z-index':'101'});
            parent.children('.create-img').css({'z-index':'102'});
            parent.animate({left:'-1px'},500);
        }
    });

    // clicking image selects checkbox
    $(".topic-img-select").click(function(event)
    {
        alert('Hello');
        $(this).siblings(".topic-radio").attr("checked", "checked");
    });


    $('#create-petition').click(function(event)
    {
        event.preventDefault();
        var title = $('#input-title').val();
        var summary = $('#input-summary').val();
        var full_text = $('#input-full_text').val();
        var link = $('#input-link').val();
        var topics = [];
        $("#petition-topics").find("input[name='topics']:checked").each(function(){topics.push($(this).val());});
        alert(topics);
        $.ajax
        ({
            type:'POST',
            url:'/action/',
            data: {'action':'create','title':title,'summary':summary, 'full_text':full_text,'link':link, 'topics':topics, 'type':'P'},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (returned.success == false)
                {
                    $("#errors-json").append(data);
                    $("#errors-title").append(returned.errors.title);
                    $("#errors-summary").append(returned.errors.summary);
                    $("#errors-full_text").append(returned.errors.full_text);
                    $("#errors-topic").append(returned.errors.topics);
                    $("#errors-non_field").append(returned.errors.non_field_errors);
                }
                else
                {
                    window.location=returned.url;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

    $('#share-button').click(function(event)
    {
        event.preventDefault();
        var title = $('#news-input-title').val();
        var summary = $('#news-input-summary').val();
        var link = $('#news-input-link').val();
        $.ajax
        ({
            type:'POST',
            url:'/action/',
            data: {'action':'create','title':title,'summary':summary,'link':link, 'type':'N'},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                if (returned.success == false)
                {
                    $("#news-errors-json").append(data);
                    $("#news-errors-title").append(returned.errors.title);
                    $("#news-errors-summary").append(returned.errors.summary);
                    $("#news-errors-topic").append(returned.errors.topics);
                    $("#news-errors-non_field").append(returned.errors.non_field_errors);
                }
                else
                {
                    window.location=returned.url;
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });

    $('#feedback-submit').click(function(event)
    {
        event.preventDefault();
        var text = $('#feedback-text').val();
        $.ajax
        ({
            type:'POST',
            url:'/action/',
            data: {'action':'feedback','text':text,'path':path},
            success: function(data)
            {
                $('#feedback-name').val("");
                $('#feedback-text').val("");
                $('#feedback-default').css('display','none');
                $('#feedback-response').css('display','block');
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                alert("failure");
            }
        });
    });

    $("#invite-button").click(function(event)
    {
        event.preventDefault();
        var email = $("#email-input").val();
        $.ajax
        ({
            type:'POST',
            url:'/action/',
            data: {'action':'invite','email':email},
            success: function(data)
            {
                $("#email-input").val("thanks!");
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                $("body").html(jqXHR.responseText);
            }
        });
    });
}
