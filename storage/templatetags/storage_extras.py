import re

from django import template
from django.contrib.admin import register
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
def highlight(text, sterm, autoescape=None):
    """ 高亮过滤器

    https://djangosnippets.org/snippets/3049/
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    pattern = re.compile('(%s)' % esc(sterm), re.IGNORECASE)
    result = pattern.sub(r'<strong class="text-primary">\1</strong>', text)
    return mark_safe(result)
