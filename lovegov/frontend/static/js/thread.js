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
                    var returned = $.parseJSON(data);
                    var html = returned['html'];
                    var cid = returned['cid'];
                    if(depth > 0) {
                        reply.hide();
                        $(html).hide().appendTo(reply.closest('div.threaddiv')).fadeIn(500);
                    } else {
                        textarea.val('');
                        $(html).hide().appendTo('div.thread').fadeIn(500);
                        new_comments.push(cid);
                    }
                    lockThreadReply = false;
                    updateThreadCommentCount();
                    bindTooltips();
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
        loadMoreComments();
    }
});

function updateThreadCommentCount() {
    var count = $('div.comment').length;
    $('div.thread').data('comments', count);
    return count;
}

function loadMoreComments() {
    var button = $('div.load-more-comments');
    var num_to_load = 10;
    var thread = button.siblings('div.thread');
    if(thread.length) {
        var cid = thread.data('cid');
        var next_start = thread.data('num-showing');
        var order = getSortValue();
        var div_load_more = button;
        var loadingimg = $('<div style="text-align: center; margin: 20px 0"><img src="/static/images/gifs/ajax-loader.gif"></div>');
        loadingimg.appendTo(thread);
        action({
            data: {'action': 'ajaxThread', 'c_id': cid, 'limit': num_to_load, 'start': next_start, 'order': order,
                'new_comments': JSON.stringify(new_comments)},
            success: function(data)
            {
                var returned = $.parseJSON(data);
                var top_count = returned.top_count;
                if(top_count==0) {
                    div_load_more.addClass('disabled');
                    div_load_more.text("there are no more comments to load");
                } else {
                    $(returned.html).hide().prependTo('div.thread').fadeIn(500);
                    $('div.thread').data('num-showing', next_start + top_count);
                }
                updateThreadCommentCount();
                bindTooltips();
            },
		    complete: function(data) {
			    loadingimg.remove();
		    }
        });
    }
}

bind('div.thread-filters select', 'change', function(e) {
    var value = $(this).val();
    clearThread();
    loadMoreComments();
});

function getSortValue() {
    return $('div.thread-filters select').val();
}

// Returns a dictionary mapping a comment id to the number of new child comments yet to be fetched and rendered
// Calls callback when done
function getNewCommentsStats(num_comments, callback) {
    var thread = $('div.thread');
    var c_id = thread.data('cid');
    var rendered_so_far = num_comments;
    action({
        data: {'action': 'getNewCommentsStats', 'c_id': c_id, 'rendered_so_far': rendered_so_far},
        success: function(data) {
            var returned = $.parseJSON(data);
            callback(returned);
        }
    });

}

function updateNewComments(comment_id, num) {
    var commentdiv = $("div.comment[data-cid='"+comment_id+"']");
    var show_new_replies = commentdiv.find('div.show-new-replies');
    show_new_replies.find('span.num-new-replies').text(num);
    show_new_replies.data('num-new-replies', num);
    show_new_replies.fadeIn(500);
}

function fetchAndUpdateNewComments() {
    var thread = $('div.thread');
    var num_comments = thread.data('comments');
    var callback = function(stats) {
        for(var comment_id in stats) {
            updateNewComments(comment_id, stats[comment_id]);
        }
    }
    getNewCommentsStats(num_comments, callback);
}

bind('div.show-new-replies', 'click', function(e) {
    var num = $(this).data('num-new-replies');
    var comment = $(this).closest('div.comment')
    var cid = comment.data('cid');
    var depth = comment.data('depth');
    var that = $(this);
    that.hide();
    var threaddiv = comment.siblings('div.threaddiv');
    if (!threaddiv.length) {
        threaddiv = $('<div class="threaddiv"></div>');
        comment.after(threaddiv);
    }
    if(num > 0) {
        action({
           data: {'action': 'getChildComments', 'cid': cid, 'depth': depth, 'num_to_fetch': num},
           success: function(data) {
               $(data).prependTo(threaddiv);
               updateThreadCommentCount();
           }
        });
    }
});

function clearThread() {
    var thread = $('div.thread');
    thread.children().remove();
    // clear top-level comment count
    thread.data('num-showing', 0);
    // clear total comment count
    thread.data('comments', 0);
}