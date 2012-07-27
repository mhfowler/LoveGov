/** question dialogs **/
$(".q-title").click(function(event) {
    $(".q-dialog").hide();
    event.preventDefault();
    var me = $(this);
    var id = $(this).attr('href');
    var d = $("#" + id);
    d.css('top', Math.max(me.offset().top - 300, 0));
    d.css('left',d.css('left')-1200);
    d.show();
});

$(".cancel").click(function(event) {
    event.preventDefault();
    $(this).parents(".everything").hide();
});

$(".submit").click(function(event)
{
    event.preventDefault();
    $(this).parents(".answerform").submit();
});

$("#change-password").click(function(event) {
    event.preventDefault();
    $(".password-dialog").show();
});
