bind('div.search input', 'keydown', function(e) {
    // Capture enter events
    if(e.which==13) {
        search($(this).val());
    }
});

// Does the actual search
function search(str) {
    alert("searching for "+str);
}