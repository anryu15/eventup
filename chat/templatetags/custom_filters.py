import markdown
from bleach.sanitizer import Cleaner
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdownify(text):
    html = markdown.markdown(text, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite'])
    cleaner = Cleaner(tags=['p', 'a', 'ul', 'ol', 'li', 'code', 'pre', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'], attributes={'a': ['href']}, strip=True)
    sanitized_html = cleaner.clean(html)
    return mark_safe(sanitized_html)


register = template.Library()


@register.filter
def markdownify(text):
    """
    Converts Markdown text to HTML.
    """
    html = markdown.markdown(text, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite'])
    return mark_safe(html)
