/**
 * Handles initial value of input fields fading and disapearing when user begins typing.
 */
(function( $ )
{
    $.fn.inputFade = function()
    {
        var all = this;

        this.each(function()
        {
            var self = $(this);

            if (self.attr("type") == "password")
            {
                var test = self.clone();
                test.attr("type","text");
            }

            var floaterspan = "";
            if (self.css('float')) { floaterspan = 'float:' + self.css('float') + ';'; }
            self.after('<span style="position:relative;' + floaterspan + '"></span>');
            self.next().append(self.detach());

            if (!self.data('init_text')) { self.data('init_text', self.val()); }
            self.parent().append('<input style="display:none;position:absolute;top:1px;left:1px;border:0;width:1px"/>');
            if (!self.data('blinker')) {self.data('blinker',self.siblings('input'));}

            var height = self.css('height');
            var padding = self.css('padding');
            var fontSize = self.css('font-size');

            self.data('blinker').css({'height':height,'padding-left':padding,'padding-top':padding,'padding-bottom':padding,'font-size':fontSize});
            self.data('blinker').keypress(function(event)
            {
                self.val(String.fromCharCode(event.keyCode));
                if (self.hasClass("input_focus"))
                {
                    self.removeClass("input_focus");
                    self.addClass("input_typing");
                }
                self.focus();
                self.data('blinker').val("");
                self.data('blinker').addClass('select-none');
            });

            self.focusin(function()
            {
                if (self.val() == self.data('init_text') && !self.hasClass('input_typing'))
                {
                    self.addClass("input_focus").removeClass("input_default");
                    self.blur();
                    self.data('blinker').show().focus();
                    self.data('blinker').css("border","none");
                    self.data('blinker').css("outline","none");
                }
            });

            self.focusout(function()
            {
                if (self.val()== "" || self.val() == self.data('init_text'))
                {
                    self.data('blinker').hide();
                }
            });

            self.bind("clickoutside", function(event)
            {
                if (self.val()== "" || self.val() == self.data('init_text'))
                {
                    self.data('blinker').val("");
                    self.val(self.data('init_text'));
                    self.addClass("input_default").removeClass("input_focus").removeClass("input_typing");
                    self.data('blinker').removeClass('select-none');
                }
                self.data('blinker').hide();
                self.blur();
            });
        });
    };
})( jQuery );