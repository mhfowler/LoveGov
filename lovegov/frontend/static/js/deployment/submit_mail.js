$(document).ready(function()
{
    var csrf = $("#default_variables").children("#csrftoken").val();
    $.ajaxSetup({
        data: {csrfmiddlewaretoken: csrf }});

    var emailInput = '#emailInput';

    $('#emailForm').submit(function()
    {
        return false;
    });

    $('#emailSubmit').bind('click', function(event)
    {
        event.preventDefault();
        var email = $(emailInput).val();
        if (checkValidEmail(email))
        {
            submitEmail(email)
        }
    });

    $(emailInput).bind('keypress', function(event)
    {
        if (event.keyCode == 13 && checkValidEmail($(emailInput).val()))
        {
            submitEmail($(emailInput).val());
        }
    });

    $(emailInput).bind('keyup', function(event)
    {
        if (event.keyCode != 13)
        {
            checkValidEmail($(emailInput).val());
        }
    });

});

/**
 * Checks if user's input is a valid email address.
 *
 * @param text      the text the user entered
 */
function checkValidEmail(text)
{
    var emailfilter=/^\w+[\+\.\w-]*@([\w-]+\.)*\w+[\w-]*\.([a-z]{2,4}|\d+)$/i;
    if (emailfilter.test(text))
    {
        $('#emailSubmit').html("submit");
        $('#emailInput').css({"background-color":"#DBFFD6"});
        return true;
    }
    else if (text=="")
    {
        $('#emailSubmit').html("");
        $('#emailInput').css({"background-color":"#FFFFFF"});
        return false;
    }
    else
    {
        $('#emailSubmit').html("");
        $('#emailInput').css({"background-color":"#FFD6D6"});
        return false;
    }
}

/**
 * Sends the user's inputted email address to the database
 *
 * @param email     a valid email address
 */
function submitEmail(email)
{
    $.ajax({
        type: 'POST',
        url:'/postEmail/',
        data: {'email':email},
        success: function()
        {
            $('#emailMessage').html("Thanks!  We'll keep you updated!");
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            $('#emailMessage').html("Server error, e-mail not added");
        }
    });
}
