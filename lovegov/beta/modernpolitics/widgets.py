########################################################################################################################
########################################################################################################################
# Field Widgets
#   - Used to customize the appearance of field input.
#
#
########################################################################################################################
########################################################################################################################
################################################## IMPORT ##############################################################

from django.forms import widgets

#=======================================================================================================================
# widget for multiple checkbox select
#
#
#=======================================================================================================================
class TopicCheckboxSelectMultiple(widgets.CheckboxSelectMultiple):

    def __init__(self, content_type, topic_count, *args, **kwargs):
        super(TopicCheckboxSelectMultiple,self).__init__()
        self.content_type = content_type
        self.topic_count = topic_count

    def render(self, name, value, attrs, choices=()):
        html = u'<br><div class="topicSelection">'
        for i in range(1, self.topic_count+1):
            html += (u'<input type="checkbox" id="' + self.content_type + '_' + str(i) + u'" value="' + str(i) + u'"name="topics"/>')
        html += u'</div>'
        return widgets.mark_safe(html)