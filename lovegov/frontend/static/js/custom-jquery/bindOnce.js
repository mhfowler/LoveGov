/* binds handler once */
(function( $ )
{
    $.fn.bindOnce = function(events, handler)
    {

        this.each(function()
        {
            $(this).off(events);
            $(this).on(events, handler);
        });
    };
})( jQuery );