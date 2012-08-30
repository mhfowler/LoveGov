// Cancel button click
bind("div.reply .tab-button.cancel", "click", function(event) {

    $(this).parent("div.reply").hide();
});


bind("div.reply .tab-button.save", "click", function(event) {
    var reply = $(this).parent("div.reply");
    var textarea = $(this).siblings("textarea.comment-textarea");
    var text = textarea.val();
    var content_id = reply.data("reply-to");
    var depth = reply.data("depth") + 1;
    if(goodLength(text)) {
        if(reply.hasClass("reply-reply") || reply.hasClass("reply-new")) {
            action({
                'data': {'action':'comment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    if(depth > 0) {
                        reply.hide();
                        $(data).hide().appendTo(reply.closest('div.threaddiv')).fadeIn(500);
                    } else {
                        textarea.val('');
                        $(data).hide().prependTo('div.thread').fadeIn(500);
                    }
                }
            });
        } else if(reply.hasClass("reply-append")) {
            action({
                'data': {'action':'appendComment', 'c_id': content_id, 'comment':text, 'depth': depth},
                'success': function(data) {
                    reply.closest('div.comment').find('div.comment-text').html(data);
                    reply.hide();
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


function incNumComments() {
    var ncspan = $('span.num_comments');
    var num_comments = parseInt(ncspan.text());
    ncspan.text(num_comments + 1);
}

// bind("#commentform","submit",function(event)
//      {
//          event.preventDefault();
//          var comment_text = $(this).children(".comment-textarea").val();
//          var comment_text_length = comment_text.length;
//          if (comment_text_length <= 10000)
//          {
//              $(this).children(".comment-textarea").val("");
//              var content_id = $("#content_id").val();
//              action({
//                  'data': {'action':'comment','c_id': content_id,'comment':comment_text},
//                  'success': function(data) {
//                      ajaxThread();
//                      incNumComments();
//                  },
//                  'error': null
//              });
//          }
//          else
//          {
//              alert("Please limit your response to 10,000 characters.  You have currently typed " + comment_text_length + " characters.");
//          }
//      });

bind("div.comment-actions div.reply-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-reply').toggle();
});

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

bind("div.comment-actions div.append-action", "click",function()
{
    $(this).parent().siblings('div.reply.reply-append').toggle();
});


// bind("input.tab-button.alt","click",function()
//      {
//          $(this).parent().hide();
//      });


// bind(".commentlike","click",function(event)
//      {
//          event.preventDefault();
//          var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//          $.post('/action/', {'action':'vote','c_id':content_id,'vote':'L'},
//              function(data)
//              {
//                  ajaxThread();
//              });
//      });

// bind('commentdislike', 'click', function(event)
//      {
//          event.preventDefault();
//          var content_id = $(this).parent().parent().next().children(".hidden_id").val();
//          $.post('/action/', {'action':'vote','c_id':content_id,'vote':'D'},
//              function(data)
//              {
//                  ajaxThread();
//              });
//      });



// Collapse a thread (a comment and all its children)
bind('span.collapse','click',function(e) {
          var close = '[-]';
          var open = '[+]';
          if($(this).text()==close) {
              $(this).text(open);
              $(this).parent().parent().siblings('div.threaddiv').children().hide();
              $(this).siblings("div.item-ranking").hide();
              $(this).parent().parent().find('div.comment-text').hide();
              $(this).parent().parent().find('div.comment-actions').hide();
          } else if($(this).text()==open) {
              $(this).text(close);
              $(this).parent().parent().siblings('div.threaddiv').children().show();
              $(this).siblings("div.item-ranking").show();
              $(this).parent().parent().find('div.comment-text').show();
              $(this).parent().parent().find('div.comment-actions').show();
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

bind('div.load-more-comments', 'click', function(e) {
    var num_to_load = 10;
    var thread = $(this).siblings('div.thread');
    if(thread.length) {
        var cid = thread.data('cid');
        var next_start = thread.data('num-showing');
        action({
            data: {'action': 'ajaxThread', 'c_id': cid, 'limit': num_to_load, 'start': next_start},
            success: function(data)
            {
                var returned = eval('(' + data + ')');
                $(returned.html).hide().appendTo('div.thread').fadeIn(500);
                $('div.thread').data('num-showing', next_start + returned.top_count);
            }
        });
    }
});
