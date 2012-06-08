function loadAbout()
{
    $(".about-element").hover
    (
        function()
        {
            $(this).css("background-color","#F9F9F9")
        },
        function()
        {
            $(this).css("background-color","#FFFFFF")
        }
    );
}