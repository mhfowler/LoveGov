// Create button click
bind('td.create-button', 'click', function(e) {
    getModal('create_modal', {}, function() {
        $('div.create-modal > div').hide();
        $('div.create-modal div.type-select').show();
    });
});

// Create group link click
bind('div.navbar_links_wrapper.groups_wrapper a.create-link', 'click', function(e) {
   getModal('create_modal', {}, function() {
       $('div.create-modal > div').hide();
       $('div.create-modal div.create-section.group').show();
       $('div.create-modal div.create-section.group select.state-select').select2({
           placeholder: 'Select a state to associate with this group.'
       })
   });
});

// Create scorecard link click
bind('div.group-action.create_scorecard', 'click', function(e) {
   var gid = $(this).data('g_id');
   getModal('create_modal', {'gid': gid}, function() {
        $('div.create-modal > div').hide();
        $('div.create-modal div.create-section.scorecard').show();
        $('div.create-modal div.create-section.scorecard select.group-select').select2({
          "placeholder": "Select a group you moderate to post this scorecard to."
        });
        $('div.create-modal div.create-section.scorecard select.poll-select').select2({
           "placeholder": "Select a poll for this scorecard."
        });
   });
});

// Create election link click
bind('div.navbar_links_wrapper.elections_wrapper a.create-link', 'click', function(e) {
    getModal('create_modal', {}, function() {
        $('div.create-modal > div').hide();
        $('div.create-modal div.create-section.election').show();
        evalDate.call($('div.create-modal input.date_autofill'));
        $('div.create-modal div.create-section.election select.state-select').select2({
            placeholder: 'Select a state to associate with this election.'
        })
    });
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

// Show add source
bind("div.create-modal div.questions span.add-source", "click", function(e) {
   $(this).closest("div.question").children("div.question-source").toggle();
});

// "Save" button clicked
bind("div.create-modal div.save", "click", function(e) {
    var section = $(this).closest('div.create-section');
    var form = section.children("form");

    if(!validField('input.title', 'title', form) ||
        !validField('input.link', 'link', form) ||
        !validField('textarea.full_text', 'description', form) ||
        !validField('textarea.description', 'description', form)) {
        return false;
    }

    var post_as = section.find("span.post-as.selected").data("poster");
    form.append('<input type="hidden" name="post_as" value="'+post_as+'">');

    var topic = section.find("span.topic_button.selected").data("t_alias");
    form.append('<input type="hidden" name="topic" value="'+topic+'">');

    if(section.hasClass('news')) {
        var screenshot = $('.news_link_selected').attr("src");
        form.append('<input type="hidden" name="screenshot" value="'+screenshot+'">');
    }

    if(section.hasClass("poll")) {
        var questions = extractQuestions();
        questions = JSON.stringify(questions);
        $('<input type="hidden" name="questions">').attr('value', questions).appendTo(form);

    }

    form.append('<input type="hidden" name="action" value="createContent">');
    form.submit();
});

function validField(field, name, form) {
    var fieldToFind = form.find(field);

    if(fieldToFind.length > 0 && fieldToFind.val()=='') {
        alert('Enter a '+name+', plox');
        return false;
    }
    return true;
}



// extract questions and answers from the DOM
function extractQuestions() {
    var questionsList = [];
    var questionsDiv = $('div.create-modal div.create-section.poll div.questions');""
    questionsDiv.children("div.question:not(.model)").each(function() {
       var q = {};
       q['question'] = $(this).find('div.question-title input').val();
       q['answers'] = [];
       $(this).find('div.question-answers textarea').each(function() {
          q['answers'].push($(this).val());
       });
       q['source'] = $(this).find('div.question-source input').val();
        questionsList.push(q);
    });
    return questionsList;
}


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
    if(e.keyCode==13) {
        e.preventDefault();
        getLinkInfo(text, $(this));
    }
});

bind("div.create-modal span.topic_button", "click", function(e) {
    $(this).siblings("span.topic_button").removeClass("selected");
    $(this).addClass("selected");
})

function selectImageToggle() {
    $('#cycle-img-span').text(currentLink + " / " + image_count);
    $('.news_link_image').removeClass("news_link_selected").hide();
    $('.news_link_image').eq(currentLink-1).addClass("news_link_selected").show();
}

var currentLink = 1;
var image_count;
bind('#cycle-img-left','click',function(e) {
    e.preventDefault();
    if (currentLink-1 < 1) { currentLink = image_count; }
    else { currentLink--; }
    selectImageToggle();
});

bind('#cycle-img-right','click',function(e) {
    e.preventDefault();
    if (currentLink+1 > image_count) { currentLink = 1; }
    else { currentLink++; }
    selectImageToggle();
});

bind("div.create-modal input.date_autofill", "keyup", evalDate);

function evalDate() {
    var messages = ["Nope", "Keep trying", "Nada", "Sorry", "Bummer", "Whoops",
        "Snafu", "Blunder", "Almost there", "Invalid date", "Whoopsie daisy", "Try again",
        "I don't understand", "No comprendo", "That doesn't work", "Your input is bad and you should feel bad"];
    var val = $(this).val();
    var datelabel = $(this).siblings("span.date_autofill_label");
    var gendate = $(this).siblings('input[name="gendate"]');
    if(val=='') {
        datelabel.text('');
        return;
    }
    var dobj = Date.parse(val);
    if(dobj==null) {
        var randMsg = messages[Math.round(messages.length * Math.random())] + "...";
        datelabel.text(randMsg);
        datelabel.removeClass("goodinput");
        gendate.val('');
    } else {
        var dt = dobj.toString('dddd, MMMM d, yyyy');
        datelabel.text('✓ '+dt);
        datelabel.addClass("goodinput");
        var dategenval = dobj.toString('yyyy-MM-dd')
        gendate.val(dategenval);

    }
}