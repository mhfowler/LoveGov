var helpMode = false;

$(document).ready(function()
{
    /**
     * Allows user to tab through main page feeds
     */
    $('#tab-wrapper').children().bind('click',function(e)
    {
        selectTab(this);
    });

    /**
     * Allows user to tab through profile pe
     */
    $('#profile-tab-wrapper').children().bind('click',function(e)
    {
        selectTab(this);
    });

    $('.security-unselected').bind('click',function(e)
    {
        selectSecurity(this);
    });

    $('#helpbutton').bind("click",function(e)
    {
        helpMode = !helpMode;
        $('#help-hover').css('visibility','hidden');
    });

    $('.help').bind('mouseover',function()
    {
        if (helpMode)
        {
            var pos = $(this).offset();
            var width = $(this).css('width');
            width = width.replace('px','');
            $('#help-hover').css('visibility','visible');
            $('#help-hover').css('top',pos.top-120);
            $('#help-hover').css('left',pos.left+(parseInt(width)));
            $(this).css('background-color', '#f7f7f7');

        }
    });

    $('.help').bind('mouseout',function()
    {
        if (helpMode)
        {
            $('#help-hover').css('visibility','hidden');
            $(this).css('background-color', '#FFFFFF');
        }
    });



});

function selectTab(tab)
{
    $('.tab-selected').addClass("tab-unselected");
    $('.tab-selected').removeClass("tab-selected");
    $(tab).removeClass("tab-unselected");
    $(tab).addClass("tab-selected");
}

function selectSecurity(security)
{
    $('.security-selected').addClass('security-unselected');
    $('.security-selected').removeClass("security-selected");
    $(security).removeClass('security-unselected');
    $(security).addClass('security-selected');
}
