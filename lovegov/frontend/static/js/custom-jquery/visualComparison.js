(function( $ )
{
    $.fn.visualComparison = function()
    {
        this.each(function()
        {
            if (!$(this).hasClass("has_visualComparison"))
            {
                new VisualComparison($(this),$(this).data('json')).draw();
                $(this).addClass("has_visualComparison");
            }
        });
    };
})( jQuery );