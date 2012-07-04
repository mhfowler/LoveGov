/**
 * Handles initial value of input fields fading and disapearing when user begins typing.
 */
(function( $ )
{
    $.fn.inputFade = function()
    {
        this.each(function()
        {
            var self = $(this);
            var inputText;
            self.addClass("input_default");

            if (self.attr("type") == "password" && !self.data("state"))
            {
                inputText = self.clone();
                inputText.attr("type","text");
                inputText.data('state','password');
                self.replaceWith(inputText);
                inputText.inputFade();
            }
            else
            {
                var floaterspan = "";
                if (self.css('float')) { floaterspan = 'float:' + self.css('float') + ';'; }
                self.after('<span style="position:relative;' + floaterspan + '"></span>');
                self.next().append(self.detach());

                if (!self.data('init_text')) { self.data('init_text', self.val()); }
                self.parent().append('<input tabindex="-1" style="display:none;position:absolute;top:1px;left:1px;border:0;width:1px"/>');
                if (!self.data('blinker')) {self.data('blinker',self.siblings('input'));}

                var height = self.css('height');
                var padding = self.css('padding');
                var fontSize = self.css('font-size');

                self.data('blinker').css({'height':height,'padding-left':padding,'padding-top':padding,'padding-bottom':padding,'font-size':fontSize});

                self.data('blinker').bind('paste',function()
                {
                    if (self.attr("type") == "text" && self.data('state') == "password")
                    {
                        var inputText = self.clone();
                        inputText.attr("type","password");
                        inputText.data("state","password");
                        self.parent().replaceWith(inputText);
                        inputText.inputFade();
                        inputText.val("");
                        inputText.focus();
                        inputText.removeClass("input_default").removeClass("input_focus").addClass("input_typing");
                    }
                    else
                    {
                        self.val(self.data('blinker').val());
                        if (self.hasClass("input_focus"))
                        {
                            self.removeClass("input_focus");
                            self.addClass("input_typing");
                        }
                        self.focus();
                        self.data('blinker').val("");
                        self.data('blinker').addClass('select-none');
                    }
                });

                self.data('blinker').keypress(function(event)
                {
                    if (self.attr("type") == "text" && self.data('state') == "password")
                    {
                        var inputText = self.clone();
                        inputText.attr("type","password");
                        inputText.data("state","password");
                        self.parent().replaceWith(inputText);
                        inputText.inputFade();
                        inputText.val("");
                        inputText.focus();
                        inputText.removeClass("input_default").removeClass("input_focus").addClass("input_typing");
                    }
                    else
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
                    }
                });

                function removeFocus()
                {
                    if (self.data('state') && self.data("state") == 'password' && self.val() == "")
                    {
                        self.removeClass("input_focus").removeClass("input_typing").removeClass("input_default");
                        self.data('blinker').removeClass('select-none');
                        self.data('blinker').hide();
                        var init_text = self.data("init_text");
                        var inputText = self.clone();
                        inputText.attr("type","text");
                        inputText.data('state','password');
                        self.parent().replaceWith(inputText);
                        inputText.val(init_text);
                        inputText.inputFade();
                    }
                    else
                    {
                        self.val(self.data('init_text'));
                        self.addClass("input_default").removeClass("input_focus").removeClass("input_typing");
                        self.data('blinker').removeClass('select-none');
                        self.data('blinker').hide();
                        self.blur();
                    }
                }

                self.data("blinker").focusout(function()
                {
                    if (self.hasClass("input_focus")) { removeFocus(); }
                });

                self.focusout(function(event)
                {
                    if (self.hasClass("input_typing") && self.val() == "") { removeFocus(); }
                });

                self.focusin(function()
                {
                    if (self.val() == self.data('init_text') && !self.hasClass('input_typing'))
                    {
                        self.data('blinker').show().focus();
                        self.addClass("input_focus").removeClass("input_default");
                        self.data('blinker').css("border","none");
                        self.data('blinker').css("outline","none");
                    }
                });

                self.bind("clickoutside", function(event)
                {
                    if (self.val()== "" || self.val() == self.data('init_text')) { removeFocus(); }
                });
            }
        });
    };
})( jQuery );