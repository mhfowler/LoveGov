/***********************************************************************************************************************
 * .js for displaying content
 *
 ***********************************************************************************************************************/

// global variables
var c_id;

/**
 *   Document Preparation
 */
$(document).ready(function(){
    c_id = $("#display_variables").children("#c_id").val();
    // Hide stuff that needs to be hidden.
    $(".replyform").hide();
    $(".edit_field").hide();
    $(".save").hide();
    $(".hidden").hide();;
});

/**
 *   Toggle visibility of edit content form.
 */
$(".edit").click(function(){
    var val = $(this).siblings(".field").text();
    $(this).siblings(".field").hide();
    $(this).siblings(".edit_field").show();
    $(this).siblings(".edit_field").val(val);
    $(this).hide();
    $(this).siblings(".save").show();
});

/**
 *   Submit edited value.
 */
$(".save").click(function(){
    var field =  $(this).siblings(".hidden").val();
    var field_value = $(this).siblings(".edit_field").val();
    $.ajax({
        url:'/action/',
        type: 'POST',
        data: {'action':'edit','c_id': c_id, 'field':field,'value':field_value},
        success: function(data){
            location.reload();
        },
        error: function(jqXHR, textStatus, errorThrown){
            $('.errors_div').html(jqXHR.responseText);
        }
    });
});


/*
 * Handles edit form dialog.
 */
$("#editformdialog").dialog({
    autoOpen:false,
    resizable:false,
    draggable:true,
    height:500,
    width:675,
    modal:true,
    style:{background:'black'},
    position:["center",50]
});

$("#edit").click(function()
{
    $("#editformdialog").dialog("open");
    if ($("#editformdialog").hasClass("opened"))
    {
        $("#editformdialog").scrollTop(0);
        $("#editformdialog").height('650px');
    }
    return false;
});

$("#editformdialog").bind("clickoutside", function(event)
{
    $(this).dialog("close");
    $('body').css('overflow','hidden');
    return false;
});


