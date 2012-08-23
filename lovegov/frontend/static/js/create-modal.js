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
    newQuestion.removeClass("model");
});

// Delete questions
bind("div.create-modal div.questions span.remove", "click", function(e) {
    var hasContent = false;
    var question = $(this).closest("div.question");
    question.find("input,textarea").each(function(i,e) {
        if($(this).val()!='') {
            hasContent = true;
            // break loop
            return false;
        }
    });
    if (hasContent) {
        if(confirm("Remove this question?")) {
            question.remove();
       }
    } else {
        question.remove();
    }
});

bind("div.create-modal div.save", "click", function(e) {
    var section = $(this).closest('div.create-section');
    var sectionType;
    var types = ['discussion', 'poll', 'news', 'petition'];
    for(var i=0; i<types.length; i++) {
        if(section.hasClass(types[i])) {
            sectionType = types[i];
        }
    }
    var title = section.find("input.title").val();
    var full_text = section.find("textarea.description").val();
    var post_to = section.find("select.post-to").val();
    var post_as = section.find("span.post-as.selected").data("poster");
    var image = 
    action({
       'data': {'action': 'createContent',
                'sectionType': sectionType,
                'title': title,
                'full_text': full_text,
                'post_to': post_to,
                'post_as': post_as},
       'success': function(data) {
           var obj = eval('(' + data + ')');
           window.location = obj.redirect;
       }

   })
});