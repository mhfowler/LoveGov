function loadQAWebIntro()
{
    var screenWidth = ($(window).width()/2)-500;
    $('#introhover').css('left', screenWidth + 'px');
    $('#introhover').css('top', '90px');

    $('#intro-confused').click(function()
    {
        $('#intro-main').css('display','none');
        $('#intro-main-help').css('display','block');
    });

    $('.intro-hide').click(function()
    {
        $('#intro-main').css('display','none');
        $('#intro-main-help').css('display','none');
    });
}

