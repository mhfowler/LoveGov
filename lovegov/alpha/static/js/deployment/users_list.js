function loadUserListHover()
{
    $('.user-list-item').hover
    (
        function()
        {
            $(this).addClass("user-list-item-hover");
        },
        function()
        {
            $(this).removeClass("user-list-item-hover");
        }
    );

    $('.user-list-item').click(function()
    {
        window.location = $(this).children('a').attr('href');
    });
}