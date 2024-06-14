from django import template
import re

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    pattern = re.compile(re.escape(search), re.IGNORECASE)
    highlighted_text = pattern.sub(f'<span class="highlight">{search}</span>', text)
    return highlighted_text
