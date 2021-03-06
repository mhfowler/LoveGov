bind('div.search input', 'keydown', function(e) {
    // Capture certain keyboard press events
    switch(e.which) {
        // Enter
        case 13:
            var val = $(this).val();
            if(val) {
                clearTimeout(searchTimeout);
                stopSearch();
                homeReload('/search/' + val);
            }
            break;
        // Up
        case 38:
            e.stopPropagation();
            break;
        // Down
        case 40:
            e.stopPropagation();
            break;
        // Backspace
        case 8:
            e.stopPropagation();
            $("div.search div.search-dropdown").fadeOut();
            break;
    }

});

// Checks whether the user seems to be typing and calls callback when they stop
var searchTimeout;
function whenTypingStops(handler) {
    if(searchTimeout != undefined) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(handler, 250);
}

bind('div.search input', 'keypress', function(e) {
   var length = $(this).val().length;
   if(length > 2) {
        whenTypingStops(function(e) {
            search(searchVal());
        });
   }
});

bind('div.search input', 'focusout', function(e) {
   var dropdown = $("div.search div.search-dropdown");
    if(hideResFlag) {
        dropdown.fadeOut(100);
    } else {
        hideResFlag = true;
    }
});

var hideResFlag = true;

bind('div.search div.search-dropdown', 'mousedown', function(e) {
    hideResFlag = false;
});

bind('div.search input', 'click', function(e) {
    if(!$(this).hasClass('long')) $(this).addClass('long');
    var dropdown = $("div.search div.search-dropdown");
    if(dropdown.html()) {
        dropdown.fadeIn(100);
    }
});

bind('div.search img.mag-glass', 'click', function(e) {
   search(searchVal());
});

// returns the value of the input from selector
// if selector is not passed, gets value from search bar
function searchVal(selector) {
    if(selector==undefined) {
        selector = $('div.search input');
    }
    return selector.val();
}


var lastSearch = '';
// Does the actual search
function search(str) {
    lastSearch = str;
    $('<img src="/static/images/ajax-spinner.gif" class="loading-gif">').insertBefore('div.search img.mag-glass');
    action({
        data: {'action':'searchAutoComplete','string':str},
        success: function(data)
        {
            // ensure desired search hasn't changed
            if(lastSearch!=str) return;
            var obj = $.parseJSON(data);
            var dropdown = $("div.search div.search-dropdown");
            dropdown.html(obj.html);
            dropdown.fadeIn(100);
        },
        timeout: 10000,
        complete: function() {
            stopSearch();
        }
    });
}

function stopSearch() {
    $('div.search img.loading-gif').remove();
}