// Create button click
bind('td.create-button', 'click', function(e) {
    var gid = $(this).data('g_id');
    getModal('create_modal', {'gid': gid, 'selected_group': gid}, function() {
        $('div.create-modal > div').hide();
        $('div.create-modal div.type-select').show();
        var post_tos = $('select.post-to');
        post_tos.select2();
    });
});

// Create group link click
bind('.create_group_link', 'click', function(e) {
   getModal('create_modal', {}, function() {
       $('div.create-modal > div').hide();
       $('div.create-modal div.create-section.group').show();
       $('div.create-modal div.create-section.group select.state-select').select2({
           placeholder: 'Select a state to associate with this group.'
       });
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
bind('.create_election_link', 'click', function(e) {
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
    if(selection=='poll') {
        if(getNumQuestions()==0) {
            $('div.create-modal div.add-question').click();
        }
    }
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
    var num_questions = getNumQuestions();
    if(num_questions==1) {
        // Adding another question - ask if it's a poll
        $('div.create-modal div.create-section.poll div.form-row.polltype').fadeIn(500);
        $('div.create-modal div.create-section.poll input:radio[value="p"]').click();
    }
    $(this).data('num-questions', num_questions+1);
   var newQuestion = $('div.create-modal div.question.model').clone();
    $('div.add-question').before(newQuestion);
    newQuestion.removeClass("model");
    bindTooltips();
});

function getNumQuestions() {
    return $("div.create-modal div.add-question").data('num-questions');
}

// Delete questions
bind("div.create-modal div.questions span.remove", "click", function(e) {
    var question = $(this).closest("div.question");
    if (!isEmptyQuestion(question)) {
        if(confirm("Remove this question?")) {
            question.remove();
       }
    } else {
        question.remove();
    }
});

function isEmptyQuestion(question) {
    var is_empty = true;
    question.find("input,textarea").each(function(i,e) {
        if($(this).val()!='') {
            is_empty = false;
        }
    });
    return is_empty;
}

function isFilledQuestion(question) {
    var is_filled = true;
    question.find("input,textarea").each(function(i,e) {
        if(!$(this).hasClass('optional') && $(this).val()=='') {
            // break loop
            is_filled = false;
        }
    });
    return is_filled;
}

// Show add source
bind("div.create-modal div.questions span.add-source", "click", function(e) {
   $(this).closest("div.question").children("div.question-source").toggle();
});

var createSaveLock = false;

// "Save" button clicked
bind("div.create-modal div.save", "click", function(e) {
    var section = $(this).closest('div.create-section');
    var form = section.children("form");

    if (createSaveLock) return;

    var invalid = false;
    var questions;

    if(section.hasClass('discussion') ||
        section.hasClass('petition') ||
        section.hasClass('election') ||
        section.hasClass('group') ||
        section.hasClass('scorecard')) {
            invalid = invalid || !validField('input.title', 'title', form);
            invalid = invalid || !validField('textarea.description', 'description', form);
    }

    if(section.hasClass('news') ||
        section.hasClass('discussion') ||
        section.hasClass('petition') ||
        section.hasClass('election') ||
        section.hasClass('scorecard')) {
            invalid = invalid || !validField('select.post_to', 'destination group', form);
    }

    if(section.hasClass('news')) {
        invalid = invalid || !validField('input.title', 'title', form);
        invalid = invalid || !validField('input.link', 'link', form);
    }

    if(section.hasClass('election')) {
        invalid = invalid || !validField('input.date_autofill', 'date', form);
    }

    if(section.hasClass('scorecard')) {
        invalid = invalid || !validField('select.poll-select', 'poll', form);
    }

    if(section.hasClass('poll')) {
        if(getPolltype()=='p') {
            invalid = invalid || !validField('input.title', 'title', form);
            invalid = invalid || !validField('textarea.description', 'description', form);
        }
        invalid = invalid || getNumQuestions() < 1;
        $('div.create-modal div.create-section.poll div.question:not(.model)').each(function(i,e) {
            if(!isFilledQuestion($(this))) {
                $(this).animate({'border-color': 'red'}, 500);
                invalid = true;
            }
        });
    }

    if(invalid) {
        section.find('div.error_msg').hide().text("Some required fields were not filled in. Please fill them in.").fadeIn(500);
        return false;
    }

    $(this).css({'background-color': '#ccc', 'cursor': 'default'});
    createSaveLock = true;

    var post_as = section.find("span.post-as.selected").data("poster");
    form.append('<input type="hidden" name="post_as" value="'+post_as+'">');

    var topic = section.find("span.topic_button.selected").data("t_alias");
    form.append('<input type="hidden" name="topic" value="'+topic+'">');

    if(section.hasClass('news')) {
        var screenshot = $('.news_link_selected').attr("src");
        form.append('<input type="hidden" name="screenshot" value="'+screenshot+'">');
        var link_title = $('#news-input-title').val();
        form.append('<input type="hidden" name="link_title" value="'+link_title+'">');
        var link_summary = $('#news-link-generation-description').text();
        form.append('<input type="hidden" name="link_summary" value="'+link_summary+'">');
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
        return false;
    }
    return true;
}



// extract questions and answers from the DOM
function extractQuestions() {
    var questionsList = [];
    var questionsDiv = $('div.create-modal div.create-section.poll div.questions');
    questionsDiv.children("div.question:not(.model)").each(function() {
       var q = {};
       q['question'] = $(this).find('div.question-title input').val();
       q['answers'] = [];
       $(this).find('div.question-answers textarea').each(function() {
          q['answers'].push($(this).val());
       });
       q['source'] = $(this).find('div.question-source input').val();
       q['topic'] = $(this).find('span.topic_button.chosen').data('t_alias');
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
    var link_image = $("div.create-modal div.create-section.news div.link-image");
    action({
        data: {'action':'getLinkInfo','remote_url':link},
        success: function(data)
        {
            var obj = eval('(' + data + ')');
            link_image.fadeIn(200);
            link_image.children("div.field").html(obj.html);
            image_count = $('.news_link_image_container').children().length;
        },
        complete: function() {
            // remove loading spinner
            input.parent().children('img.loading-gif').remove();
        },
        error: function(e) {
            link_image.fadeOut(200);
            alert("We were unable to fetch a description of the link.");
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

bind("div.create-modal div.field span.topic_button", "click", function(e) {
    if($(this).hasClass('selected')) {
        $(this).removeClass('selected');
    } else {
        $(this).siblings("span.topic_button").removeClass("selected");
        $(this).addClass("selected");
    }
});

bind("div.create-modal div.questions span.topic_button", "click", function(e) {
   $(this).siblings('div.qt-select').fadeToggle(200);
});

bind("div.create-modal div.qt-select span.topic_button", "click", function(e) {
    var qtselect = $(this).closest('div.qt-select');
    qtselect.siblings('span.topic_button').replaceWith($(this).clone().addClass('chosen'));
    qtselect.fadeOut(200);
    bindTooltips();
});

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

// click switch to Poll question type
bind('div.create-modal div.create-section.poll input:radio[value="p"]', "click", switchToPoll);

bind('div.create-modal div.create-section.poll input:radio[value="q"]', "click", switchToQuestion);

function switchToPoll() {
    $('div.create-modal div.create-section.poll div.poll-form').fadeIn(200);
}

function switchToQuestion() {
    $('div.create-modal div.create-section.poll div.poll-form').fadeOut(200);
}

function getPolltype() {
    return $('div.create-modal div.create-section.poll input:radio[name="polltype"]:checked').val();
}

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