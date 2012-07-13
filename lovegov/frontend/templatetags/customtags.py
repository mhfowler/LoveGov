from django import template
from django.template.base import TemplateSyntaxError, Node

from itertools import cycle as itertools_cycle

register = template.Library()

class CycleListNode(Node):
    def __init__(self, list_variable, template_variable):
        self.list_variable = list_variable
        self.template_variable = template_variable

    def render(self, context):
        if self not in context.render_context:
            # First time the node is rendered in template
            context.render_context[self] = itertools_cycle(context[self.list_variable])
        cycle_iter = context.render_context[self]
        value = cycle_iter.next()
        if self.template_variable:
            context[self.template_variable] = value
        return ''

@register.tag
def cycle_list(parser, token):
    args = token.split_contents()
    if len(args) != 4 or args[-2] != 'as':
        raise TemplateSyntaxError(u"Cycle_list tag should be in the format {% cycle_list list as variable %}")
    return CycleListNode(args[1], args[3])

@register.filter
def subtract(value, arg):
    return int(value) - int(arg)

@register.filter("truncate_chars")
def truncate_chars(value, max_length):
    if len(value) <= max_length:
        return value
 
    truncd_val = value[:max_length]
    if value[max_length] != " ":
        rightmost_space = truncd_val.rfind(" ")
        if rightmost_space != -1:
            truncd_val = truncd_val[:rightmost_space]
 
    return truncd_val + "..."