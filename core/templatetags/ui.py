from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.icons import ICONS

register = template.Library()


@register.simple_tag
def icon(name, size=18, css=''):
    """Affiche une icône Lucide en SVG inline : {% icon "egg" 20 %}"""
    inner = ICONS.get(name, ICONS['circle-alert'])
    return format_html(
        '<svg class="ic {}" width="{}" height="{}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>',
        css, size, size, mark_safe(inner))


@register.filter
def fcfa(value):
    """12500 -> '12 500 FCFA'"""
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        return '-'
    return f"{n:,}".replace(',', ' ') + ' FCFA'


@register.filter
def num(value, decimals=0):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return '-'
    s = f"{n:,.{int(decimals)}f}".replace(',', ' ').replace('.', ',')
    return s


@register.filter
def initials(user):
    name = (user.get_full_name() or user.username or '?').strip()
    parts = name.split()
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else '')).upper()


@register.filter
def css_field(field, css):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': css})


@register.simple_tag(takes_context=True)
def qs(context, **kwargs):
    """Querystring courante avec remplacement de paramètres : {% qs page=3 %}"""
    q = context['request'].GET.copy()
    for k, v in kwargs.items():
        if v in (None, ''):
            q.pop(k, None)
        else:
            q[k] = v
    s = q.urlencode()
    return ('?' + s) if s else '?'
