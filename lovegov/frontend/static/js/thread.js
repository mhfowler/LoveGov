// Cancel button click
bind("div.reply .tab-button.cancel", "click", function(event) {

    $(this).parent("div.reply").hide();
});


var lockThreadReply = false;

// Save click - append, reply, or new comment
bind("div.reply .tab-button.save", "click", function(event) {
    var reply = $(this).parent("div.reply");
    var textarea = $(this).siblings("textarea.comment-textarea");
    var text = textarea.val();
    var content_id = reply.data("reply-to");
    var depth = reply.data("depth") + 1;
    if(goodLength(text)) {
        if(lockThreadReply) {
            return;
        }
        // New comment or reply
        if(reply.hasClass("reply-reply") || reply.hasClass("reply-new")) {
            lockThreadReply = true;
            action({
                'data': {'action':'comment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    var returned = eval('(' + data + ')');
                    var html = returned['html'];
                    var cid = returned['cid'];
                    if(depth > 0) {
                        reply.hide();
                        $(html).hide().appendTo(reply.closest('div.threaddiv')).fadeIn(500);
                    } else {
                        textarea.val('');
                        $(html).hide().prependTo('div.thread').fadeIn(500);
                        new_comments.push(cid);
                    }
                    lockThreadReply = false;
                }
            });
        // Append to comment
        } else if(reply.hasClass("reply-append")) {
            lockThreadReply = true;
            action({
                'data': {'action':'appendComment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    reply.closest('div.comment').find('div.comment-text').html(data);
                    reply.hide();
                    lockThreadReply = false;
                }
            });
        }
    }

});

// Returns true if text length is short enough
// Otherwise alerts warning and returns false
function goodLength(text) {
    var len = text.length;
    if (len < 10000) {
        return true;
    } else {
        alert("Please limit your response to 10,000 characters.  You have currently typed " + len + " characters.");
        return false;
    }
}


//function incNumComments() {
//    var ncspan = $('span.num_comments');
//    var num_comments = parseInt(ncspan.text());
//    ncspan.text(num_comments + 1);
//}

// Reply button click toggles nearest reply form
bind("div.comment-actions div.reply-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-reply').toggle();
});

// Delete comment click
bind("div.comment-actions div.delete-action", "click",function()
{
    var comment = $(this).closest("div.comment");
    var content_id = $(this).data('cid');
    action({
        'data': {'action':'delete','c_id':content_id},
        'success': function(data) {
            comment.html("Comment deleted.");
        }
    });
});

// Append comment click
bind("div.comment-actions div.append-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-append').toggle();
});


// Collapse a thread (a comment and all its children)
bind('span.collapse','click',function(e) {
    var grandparent = $(this).parent().parent();
    var close = '[-]';
    var open = '[+]';
    if($(this).text()==close) {
        $(this).text(open);
        grandparent.siblings('div.threaddiv').children().hide();
        $(this).siblings("div.item-ranking").hide();
        grandparent.find('div.comment-text').hide();
        grandparent.find('div.comment-actions').hide();
    } else if($(this).text()==open) {
        $(this).text(close);
        grandparent.siblings('div.threaddiv').children().show();
        $(this).siblings("div.item-ranking").show();
        grandparent.find('div.comment-text').show();
        grandparent.find('div.comment-actions').show();
    }
});

//Flag a comment
bind('span.flag',"click", function(e) {
          var commentid = $(this).data('commentid');
          var comment = $(this).parent().children('div.comment-text').text();
          var conf = confirm("Are you sure you want to flag this comment?\n\n"+comment);
          if(conf) {
              action({
                  data: {'action': 'flag', 'c_id': commentid},
                  success: function(data) {
                      alert(data);
                      $(this).css("color", "red");
                  },
                  error: function(data) {
                      alert("Flagging comment failed.");
                  }
              });
          }
      });

// Load more comments click
bind('div.load-more-comments', 'click', function(e) {
    if(!$(this).hasClass('disabled')) {
        var num_to_load = 10;
        var thread = $(this).siblings('div.thread');
        if(thread.length) {
            var cid = thread.data('cid');
            var next_start = thread.data('num-showing');
            var div_load_more = $(this);
            action({
                data: {'action': 'ajaxThread', 'c_id': cid, 'limit': num_to_load, 'start': next_start, 'new_comments': JSON.stringify(new_comments)},
                success: function(data)
                {
                    var returned = eval('(' + data + ')');
                    var top_count = returned.top_count;
                    if(top_count==0) {
                        div_load_more.addClass('disabled');
                        div_load_more.text("there are no more comments to load");
                    } else {
                        $(returned.html).hide().appendTo('div.thread').fadeIn(500);
                        $('div.thread').data('num-showing', next_start + top_count);
                    }
                    bindTooltips();
                }
            });
        }
    }
});


