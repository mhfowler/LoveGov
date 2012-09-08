/***********************************************************************************************************************
 *
 *      ~ account settings
 *
 ***********************************************************************************************************************/
function bindSettings()
{

    var currently_selected =  $('.account_button[data-url="' + path + '"]');
    var starting_url = '/settings/profile/';
    if (currently_selected.length==0) {
        currently_selected = $('.account_button[data-url="' + starting_url + '"]');
    }
    selectAccountButton(currently_selected);

    var pencil = $('.edit_link').detach();

    /* account input visual indicator */
    $('.account_input').hover(
        function() { $(this).parent().next().append(pencil); },
        function() { pencil = pencil.detach(); }
    );

    /* party selection */
    $('img.party_choice').each( function(i)
    {
        var checkbox = $(this).siblings('input.party_input');
        if( checkbox.attr('checked') )
        {
            $(this).addClass("party-choice-selected");
        }
    });

    $('img.party_choice').click(function()
    {
        var checkbox = $(this).siblings('input.party_input');
        checkbox.attr('checked', !checkbox.prop('checked'));
        $(this).toggleClass("party-choice-selected");
        if (!$(this).hasClass("party-choice-selected"))
        {
            $(this).addClass("party-choice-deselected");
        }
    });

    $('img.party_choice').mouseout(function()
    {
        $(this).removeClass("party-choice-deselected");
    });
}

bind(".account_button", "click", null, function(event) {
    selectAccountButton($(this));
});

function selectAccountButton(button) {
    // visual indicator
    var pointer = $('.account-button-pointer');
    $('.account_button').removeClass("account-button-selected");
    button.addClass("account-button-selected");
    button.prepend(pointer);
    // show account div
    $('.account_div').hide();
    var this_url= button.data('url');
    $('.account_div[data-url="' + this_url + '"]').show();
    History.pushState( {k:1}, "LoveGov: Beta", this_url);
    evalDate.call($("div.account_div input[name=age]"));
}

/* voting address */
bind(".save_voting_address", "click", null, function(event) {

    var state = $(".location_state_select").val();
    var city = $(".voting_city_input").val();
    var street = $(".voting_street_address").val();
    var zip = $(".voting_zip_input").val();
    action({
        'data': {'action':'submitAddress', 'state':state, 'city':city, 'address':street, 'zip':zip},
        success: function(data)
        {
            $('.address_success_message').show();
        }
    });
});


/* politician settings */
bind(".i_am_politician_checkbox", "click", null, function(event) {
    if ($(this).is(':checked')) {
        $(".i_am_politician").show();
    }
    else {
        $(".i_am_politician").hide();
    }
});

bind(".politician_choice", "click", null, function(event) {
    if ($(this).is(':checked')) {
        $(".politician_choice").attr("checked", false);
        $(this).attr("checked", true);

        if ($(this).hasClass("has_office")) {
            $(".office_description").show();
        }
        else {
            $(".office_description").hide();
        }
    }

});


bind(".save_politician_settings", "click", null, function(event) {

    var politician = $(".i_am_politician_checkbox").is(':checked');
    var political_status_chosen = $(".politician_choice:checked");
    var office_title = $(".office_title_input").val();
    var office_description = $(".office_description_textarea").val();

    // if politician, validate other fields
    if (politician == 1) {

        var valid = true;

        if (political_status_chosen.length == 0) {
            $(".political_status_error").show();
            valid = false;
        }
        else {
            var political_status = political_status_chosen.val();
        }


        if (political_status_chosen.hasClass("has_office")) {
            if (office_title == "") {
                $(".office_title_error").show();
                valid = false;
            }

            if (office_description == "") {
                $(".office_description_error").show();
                valid = false;
            }
        }

        if (valid) {
            savePoliticianSettings(politician, political_status, office_title, office_description);
        }
    }
    else {
        savePoliticianSettings(politician, "", "", "");
    }
});


function savePoliticianSettings(politician, political_status, office_title, office_description) {
    action({
        'data': {'action':'savePoliticianSettings', 'politician':politician, 'political_status':political_status,
            'office_title':office_title, 'office_description':office_description},
        success: function(data)
        {
            $('.politician_success_message').show();
            $('.politician_success_message').fadeOut(2000);
        }
    });
}


/* mis */
bind(".back_to_button", "click", function(e) {
    History.back();
});

// bind change content privacy
bind('div.change-privacy','click', function() {
    var content_id = $(this).data('content_id');
    var meDiv = $(this);
    $(this).tooltip('hide');
    action({
        data: {
            'action': 'changeContentPrivacy',
            'content_id': content_id
        },
        success: function(data) {
            var returned = eval('('+data+')');
            if(returned.error) {
                alert("Error: "+data.error);
            } else {
                meDiv.parent().html(returned.html);
                bindTooltips();
            }
        }
    });
});

bind("div.account_div input[name=age]", "keyup", evalDate);