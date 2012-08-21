bind('div.search input', 'keydown', function(e) {
    // Capture certain keyboard press events
    switch(e.which) {
        // Enter
        case 13:
            search($(this).val());
            break;
        // Up
        case 38:
            e.stopPropagation();
            break;
        // Down
        case 40:
            e.stopPropagation();
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
        whenTypingStops(function(e) { search($(this).val()); });
   }
});

bind('div.search input', 'focusout', function(e) {
   var dropdown = $("div.search div.search-dropdown");
   if(e.target!=dropdown) {
       dropdown.fadeOut(100);
   }
});

bind('div.search input', 'focus', function(e) {
    var dropdown = $("div.search div.search-dropdown");
    if(dropdown.html()) {
        dropdown.fadeIn(100);
    }
});

bind('div.search', 'click', function(e) {
   $('div.search input').focus();
});

// returns the value of the input from selector
// if selector is not passed, gets value from search bar
function searchVal(selector) {
    if(selector==undefined) {
        selector = $('div.search input');
    }
    return selector.val();
}

// Does the actual search
function search(str) {
    action({
        data: {'action':'searchAutoComplete','string':str},
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            var dropdown = $("div.search div.search-dropdown");
            dropdown.html(obj.html);
            dropdown.fadeIn(100);
        }
    });
}