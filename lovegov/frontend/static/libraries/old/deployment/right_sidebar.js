var right_sidebar_topic;

function bindRightSideBar()
{
    // sidebar stuff, for question-topic select
    $(".topic-div").hide();
    $(".selected").hide();

    if (right_sidebar_topic!='')
    {
        var alias_div = $('input[value="' + topic + '"]');
        selectTopic(alias_div.siblings(".normal"));
    }

    $(".topic-img").click(function(event)
    {
        selectTopic($(this));
    });

    $(".topic-img").hover
    (
        function(event)
        {
            $(this).parent().children(".normal").hide();
            $(this).parent().children(".selected").show();
        },
        function(event)
        {
            var selected = $(this).parent().children(".selected");
            if (!(selected.hasClass("chosen")))
            {
                $(this).parent().children(".selected").hide();
                $(this).parent().children(".normal").show();
            }
        }
    );
}

// shows questions from the selected topic and adjusts icons appropriately
function selectTopic(div)
{
    var t = div.siblings(".t-alias").val();
    // switch to selected
    $(".selected").hide();
    $(".normal").show();
    div.parent().children(".normal").hide();
    div.parent().children(".selected").show();
    $(".selected").removeClass("chosen");
    div.parent().children(".selected").addClass("chosen");
    // display questions
    $(".topic-div").hide();
    $("#topic-"+t).show();
}
