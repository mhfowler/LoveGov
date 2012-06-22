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
