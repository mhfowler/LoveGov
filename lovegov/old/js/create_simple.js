/***********************************************************************************************************************
 * .js for actions on content
 *
 ***********************************************************************************************************************/

$(document).ready(function(){
    //$("#form").children().hide();
});
// choice links make one form visible on click
$("#make_event").click(function(){
    $("#form").children().hide();
    $("#event_form").show();
    document.body.overflow = 'scroll';
});
$("#make_petition").click(function(){
    $("#form").children().hide();
    $("#petition_form").show();
    document.body.overflow = 'scroll';
});
$("#make_news").click(function(){
    $("#form").children().hide();
    $("#news_form").show();
    document.body.overflow = 'scroll';
});
$("#make_group").click(function(){
    $("#form").children().hide();
    $("#group_form").show();
    document.body.overflow = 'scroll';
});
$("#make_album").click(function(){
    $("#form").children().hide();
    $("#album_form").show();
    document.body.overflow = 'scroll';
});

