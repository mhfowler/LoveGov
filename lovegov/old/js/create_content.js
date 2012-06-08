/**
 * Created by PyCharm.
 * User: CLAY
 * Date: 2/6/12
 * Time: 12:07 PM
 * To change this template use File | Settings | File Templates.
 */
/*
* This script handles assigning click, mouseover, and mouseout functionality to the image icons standing in place
* of checkboxes.
*
* Checkbox ID format: type_#, ex. P_3, E_8, N_2
* Checkbox Img IDs format: img_type_3, ex. img_P_3, img_E_8, img_N_2
*
*/
function resetCreateContentDisplay(selectionID)
{
    var elemID = '#' + selectionID;
    $("#form").children().hide();
    $(elemID.replace("_img","")).show();
    $("#formdialog").dialog('option','height','650');
    $("#formdialog").addClass("opened")
}

$(document).ready(function()
{
    // AJAX
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: '{{ csrf_token }}' }
    });
    $("#form").children().hide();
    $(".create_icons").click(function()
    {
        resetCreateContentDisplay($(this).attr('id'))
    });
// stylistic
    $("#choice").children().hover(
        function(){ $(this).css("text-decoration", "underline"); },
        function(){ $(this).css("text-decoration", "none");}
    );
    $.fx.speeds._default = 1000;
    /**
     * This script handles assigning click, mouseover, and mouseout functionality to the image icons standing in place
     * of checkboxes.
     *
     * Checkbox ID format: type_#, ex. P_3, E_8, N_2
     * Checkbox Img IDs format: img_type_3, ex. img_P_3, img_E_8, img_N_2
     *
     */
    $(".topicSelection img").each(function()
    {
        $(this).bind('click', function()
        {
            var checkBoxID = '#' + $(this).attr('id').replace("img_","");
            if ($(checkBoxID).attr('checked')=='checked')
            {
                $(checkBoxID).attr('checked',false);
                $(this).attr('src', '/static/icons/environment_icon.gif');
                $(this).removeClass("clicked");
            }
            else
            {
                $(checkBoxID).attr('checked',true);
                $(this).attr('src', '/static/icons/environment_icon_mouseover.gif');
                $(this).addClass('clicked');
            }
        });
        $(this).bind('mouseover', function()
        {
            $(this).attr('src', '/static/icons/environment_icon_mouseover.gif');
        });
        $(this).bind('mouseout', function()
        {
            if (!$(this).hasClass("clicked"))
            {
                $(this).attr('src', '/static/icons/environment_icon.gif');
            }
        });
    });

    /**
     * Handles assigning a datetimepicker to the datetime of the event
     */
    /*
    $( "#id_datetime_of_event" ).datetimepicker({
            ampm: true,
            stepHour: 1,
            stepMinute: 15}
    );
    */

    /**
     * Handles figuring out if a link was typed.  If a link was typed, AJAX request
     * is made to the server.  The server processes the url, gets the title and description,
     * and returns this data to the client.
     */
    var lastURL = null;
    var urlpattern = /(http:\/\/www|www|en)\..+\.(.{1,4}$|.{1,4}\/.*$)/;
    // var urlpattern = /^(((http|https|ftp):\/\/)?([[a-zA-Z0-9]\-\.])+(\.)([[a-zA-Z0-9]]){2,4}([[a-zA-Z0-9]\/+=%&_\.~?\-]*))*$/;
    $('#id_link').change(function(e)
    {
        if (urlpattern.test($('#id_link').val()))
        {
            $.ajax({
                url:'/actionGET/',
                type: 'GET',
                data: {'access':'linkInfo', 'url':$('#id_link').val().toString()},
                success: function(data)
                {
                    var linkData = eval('(' + data + ')');
                    $('#linkData').html(linkData['title'].toString() + "<br>" + linkData['description'].toString());
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $('#linkData').html("");
                }
            });
        }
    });

    /*
     * Handles the dialog generation and click functionality
     */
    $("#formdialog").dialog({
        autoOpen:false,
        resizable:false,
        draggable:true,
        height:250,
        width:675,
        modal:true,
        style:{background:'black'},
        position:["center",50]
        /*
         close: function()
         {
         var $this = $(this);
         $this.dialog("widget").effect("puff",150, function()
         {
         $this.hide();
         });
         */
    });

    $("#create").click(function()
    {
        $("#formdialog").dialog("open");
        if ($("#formdialog").hasClass("opened"))
        {
            $("#formdialog").scrollTop(0);
            $("#formdialog").height('650px');
        }
        return false;
    });

    $("#formdialog").bind("clickoutside", function(event)
    {
        $(this).dialog("close");
        $('body').css('overflow','hidden');
        return false;
    });
});
