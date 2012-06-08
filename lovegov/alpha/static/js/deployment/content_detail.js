$(document).ready(function()
{
    $("#sign-button").click(function(event) {
        alert("why");
        event.preventDefault();
        $.ajax
            ({
                type:'POST',
                url:'/action/',
                data: {'action':'sign','c_id':c_id},
                success: function(data)
                {
                    var returned = eval('(' + data + ')');
                    if (returned.success) {
                        $("#signers").append(returned.signer);
                    }
                    else {
                        $("#errors").append(returned.error);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    $("body").html(jqXHR.responseText);
                }
            });
    });

});