

/***********************************************************************************************************************
 *
 *     ~Delegated binding function, very similar to jquery's deprecated ".live()"
 *
 ***********************************************************************************************************************/

function bind(selector, events, data, handler) {
    $(document).on(events, selector, data, handler);
}


function action(action, data, success, error) {
    if( action==null ) {
        return;
    }
    data['action'] = action;
    $.ajax({
        url: '/action/',
        type: 'POST',
        data: data,
        success: success,
        error: error
    });
}



$(document).ready(function()
{
    // csrf protect
    $.ajaxSetup({ data: {csrfmiddlewaretoken: csrf} });

    // check browser compatability
    checkCompatability();

    // Prepare
    var History = window.History; // Note: We are using a capital H instead of a lower h
    if ( !History.enabled )
    {
        // History.js is disabled for this browser.
        // This is because we can optionally choose to support HTML4 browsers or not.
        return false;
    }
    // Bind to StateChange Event
    History.Adapter.bind(window,'statechange',function()
    {
        // Note: We are using statechange instead of popstate
        var State = History.getState(); // Note: We are using History.getState() instead of event.state
        History.log(State.data, State.title, State.url);
    });

    // back button reload
    window.onpopstate = function(event)
    {
        if (event.state != null) { window.location.reload(); }
    };

});

/***********************************************************************************************************************
 *
 *      ~Check browser compatibility using Modernizr
 *
 ***********************************************************************************************************************/


function checkCompatability() {
    var compatability_cookie =  $.cookie('compatability');
    var csrf_check = $.cookie('csrftoken');
    if (compatability_cookie == null) {
        var incompatible = [];
        $.each(Modernizr, function(index, element) {
            if (!element) {
                incompatible.push(index);
            }
        });
        var incompatible_json = JSON.stringify(incompatible);
        action('logCompatibility', 
            {'incompatibile': incompatible_json}, 
            function(data) {
                $.cookie('compatability', incompatible_json);
            }
        );
    }
}


/***********************************************************************************************************************
 *
 *      ~Bind popovers
 *
 ***********************************************************************************************************************/

bind("tooltip-top", "tooltip", {'placement': 'top', 'animation': 'true'});
bind("tooltip-bottom", "tooltip", {'placement': 'bottom', 'animation': 'true'});
bind("tooltip-right", "tooltip", {'placement': 'right', 'animation': 'true'});
bind("tooltip-left", "tooltip", {'placement': 'left', 'animation': 'true'});




bind(".bind_link", "click", function(event) {
        event.preventDefault();
        var url = $(this).data('url');
        window.location.href = url;
    });





























