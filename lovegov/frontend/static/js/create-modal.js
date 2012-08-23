// Create button click
bind('td.create-button', 'click', function(e) {
    getModal('create_modal');
});

// Selection of type of content to create
bind("div.create-modal div.selection", "click", function(e) {
    var selection = $(this).data('selection');
    $('div.create-modal div.type-select').hide();
    $('div.'+selection).fadeIn(250);
});


// Modal's back button
bind("div.create-modal div.create-section span.back", "click", function(e) {
   $("div.create-modal div.create-section").hide();
   $('div.create-modal div.type-select').fadeIn(250);
});

// Post as user or anonymous selection
bind("div.create-modal span.post-as", "click", function(e) {
    $(this).siblings("span.post-as").removeClass("selected");
   $(this).addClass("selected");
});

// Add questions to create poll
bind("div.create-modal div.add-question", "click", function(e) {
   var newQuestion = $('div.create-modal div.question.model').clone();
    $('div.add-question').before(newQuestion);
});