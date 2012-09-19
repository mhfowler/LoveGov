
/***********************************************************************************************************************
 *
 *      ~Legislation
 *
 **********************************************************************************************************************/

//bind(".feed_by_subject" , "click" , null , function(event) {
//    var subject = $(this).html();
//    var subject_json = JSON.stringify(subject);
//    refreshFeed();
//});
//
//bind(".feed_by_committee" , "click" , null , function(event) {
//    var committee = $(this).html();
//    var committee_json = JSON.stringify(committee);
//    refreshFeed();
//});
//
//bind(".feed_by_related_bills" , "click" , null , function(event) {
//    var related_bills = $(this).html();
//    var related_bills_json = JSON.stringify(related_bills);
//    refreshFeed();
//});

bind( '.filter_box' , 'click' , null , function(event) {
    event.preventDefault();
    if ($(this).hasClass('clicked')) {
        $(this).removeClass('clicked');
    }
    else {
        $(this).addClass('clicked');
    }
});

function updateFeed() {
    $('div.feed-button').click();
}

function loadBillSelect2() {
    function formatSession(session) {
        return "Congress Session " + session.text;
    }
    $('.session_select').select2({
        placeholder: "Search for bill sessions",
        formatSelection: formatSession,
        change: updateFeed
    });
    $('.type_select').select2({
        placeholder: "Search for bill types",
        change: updateFeed
    });
    $('.subject_select').select2({
        placeholder: "Search for bill subjects",
        transport: $.post,
        minimumInputLength: 1,
        ajax: {
            url: '/action/',
            data: function(term, page) {
                return {
                    'action': 'getBillSubjects',
                    'term': term,
                    'page': page
                }
            },
            results: function(data, page) {
                var returned = $.parseJSON(data);
                return {'results': returned.subjects};
            }
        },
        quietMillis: 200,
        dataType: 'json',
        multiple: true,
        change: updateFeed

    });
    $('.committee_select').select2({
        placeholder: "Search for bill committees",
        change: updateFeed
    });
    $('.introduced_select').select2({
        placeholder: "Search by date period",
        change: updateFeed
    });
    $('.sponsor_select_body').select2({
        placeholder: "Search for bill sponsor body",
        change: updateFeed
    });
    $('.sponsor_select_name').select2({
        placeholder: "Search for bill sponsor name",
        change: updateFeed
    });
    $('.sponsor_select_party').select2({
        placeholder: "Search for bill sponsor party",
        change: updateFeed
    });
    $('.sponsor_select_district').select2({
        placeholder: "Search for bill sponsor district",
        change: updateFeed
    });
}

function showSelectors() {
    $('.legislation_selector_wrapper').children().hide();
}

function showLegSelectors() {
    $('.filter_box').click(function(event) {
        event.preventDefault();
        if ($(this).hasClass('unchecked')) {
            $(this).removeClass('unchecked');
            $(this).addClass('checked');
            var selector = $("." + $(this).data('selector'));
            //selector.siblings().hide('fast');
            selector.show('fast');
        }
        else {
            $(this).removeClass('checked');
            $(this).addClass('unchecked');
            var selector = $("." + $(this).data('selector'));
            //selector.siblings().hide('fast');
            selector.hide('fast');
        }
    });
}

function shortenLongText() {
    var ellipsestext = "...";
    var moretext = "read more";
    var lesstext = "less";
    if ($('.long_text').hasClass("bill_detail")) {
        var showChar = 600;
    }
    else {
        var showChar = 150;
    }
    $('.long_text').each(function() {

        var content = $(this).html();

        if(content.length > showChar) {

            var c = content.substr(0, showChar);
            var h = content.substr(showChar, content.length - showChar);

            if($(this).hasClass("bill_detail")) {
                var html = c + '<span class="moreellipses">' + ellipsestext + '&nbsp;</span><span class="morecontent"><span class="morecontent_span" style="display: none;">' + h + '</span>&nbsp;&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';
            }
            else {
                var html = c + '<span class="moreellipses">' + ellipsestext + '&nbsp;</span>';
            }
            $(this).html(html);
        }
    });

    if($('.long_text').hasClass("bill_detail")) {
        $('.morelink').click(function(){
            if($(this).hasClass("less")) {
                $(this).removeClass("less");
                $(this).html(moretext);
            } else {
                $(this).addClass("less");
                $(this).html(lesstext);
            }
            $('.morecontent_span').toggle();
            $('.moreellipses').toggle();
            return false;
        });
    }
}
