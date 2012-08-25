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

// "Save" button clicked
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
    var image = section.find("input.content-image").val();
    var link = section.find("input.link").val();
    var screenshot = $('.news_link_selected').attr("src");
    action({
       'data': {'action': 'createContent',
                'sectionType': sectionType,
                'title': title,
                'full_text': full_text,
                'post_to': post_to,
                'post_as': post_as,
                'link': link,
                'screenshot': screenshot,
                },
       'success': function(data) {
           var obj = eval('(' + data + ')');
           window.location = obj.redirect;
       }
   })
});


function getLinkInfo(link, input) {
    if(link=='') return;
    // check cache
    if(input.data('last-link')==link) return;
    // cache link to prevent double get
    input.data('last-link', link);
    input.parent().append('<img src="http://local.lovegov.com:8000/static/images/ajax-spinner.gif" class="loading-gif">')

    action({
        data: {'action':'getLinkInfo','remote_url':link},
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            $("div.create-modal div.create-section.news div.link-image div.field").html(obj.html);
            image_count = $('.news_link_image_container').children().length;
        },
        complete: function() {
            // remove loading spinner
            input.parent().children('img.loading-gif').remove();
        }
    });
}

bind("div.create-modal div.create-section.news input.link", "blur", function(e) {
    var text = $(this).val();
    getLinkInfo(text, $(this));
});

bind("div.create-modal div.create-section.news input.link", "keypress", function(e) {
    var text = $(this).val();
    if(e.keyCode==13) getLinkInfo(text, $(this));
});

function selectImageToggle() {
    $('#cycle-img-span').text(currentLink + " / " + image_count);
    $('.news_link_image').removeClass("news_link_selected").hide();
    $('.news_link_image').eq(currentLink-1).addClass("news_link_selected").show();
}

var currentLink = 1;
var image_count;
bind('#cycle-img-left','click',function() {
    if (currentLink-1 < 1) { currentLink = image_count; }
    else { currentLink--; }
    selectImageToggle();
});

bind('#cycle-img-right','click',function() {
    if (currentLink+1 > image_count) { currentLink = 1; }
    else { currentLink++; }
    selectImageToggle();
});