function loadHeader()
{
    $('#searchbar').focusin(function()
    {
        $(this).val("");
        $(this).css("color",'#000000');
    });

    $("#searchbar").bind("clickoutside", function(event)
    {
        if ($(this).val()=="")
        {
            $(this).val('Search Users');
            $(this).css("color",'#959595');
        }
        $(this).blur();
    });

    $('#top-logo').bind("click",function()
    {
        window.location = '/alpha/';
    });

    $('#logo-img').hover(
            function()
            {
                $(this).attr('src','/static/images/top-logo-hover.png');
            },
            function()
            {
                $(this).attr('src','/static/images/top-logo-default.png');
            }
    );

    function resetSecuritySelection()
    {
        $('.security-unselected').bind('click',function(e)
        {
            $('.security-selected').addClass('security-unselected');
            $('.security-selected').removeClass("security-selected");
            $(this).removeClass('security-unselected');
            $(this).addClass('security-selected');
        });
    }

    $("#public").click( function(event)
    {
        event.preventDefault();
        $.post('/action/', {'action':'setPrivacy','mode':'PUB','path':path},
                // call back function
                function()
                {
                    resetSecuritySelection();
                });
    });

    $("#private").click( function(event)
    {
        event.preventDefault();
        $.post('/action/', {'action':'setPrivacy','mode':'PRI','path':path},
                // call back function
                function()
                {
                    resetSecuritySelection();
                });
    });

    $("#custom").click( function(event)
    {
        event.preventDefault();
        $.post('/action/', {'action':'setPrivacy','mode':'FOL','path':path},
                // call back function
                function()
                {
                    resetSecuritySelection();
                });
    });
}


