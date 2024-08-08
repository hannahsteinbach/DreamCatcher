from django import template
import re

register = template.Library()


@register.filter(name='highlight')
def highlight(text, search):
    pattern = re.compile(
        r'\b{}\b'.format(re.escape(search)),
        re.IGNORECASE
    )
    highlighted_text = pattern.sub(lambda m: f'<span class="highlight">{m.group()}</span>', text)
    return highlighted_text
