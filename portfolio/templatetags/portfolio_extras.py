from django import template
from django.templatetags.static import static

from portfolio.images import variant_url

register = template.Library()


@register.simple_tag
def loc(obj, field):
    return obj.loc(field)


@register.simple_tag
def icon_src(url):
    if url.startswith(("http://", "https://", "/")):
        return url
    return static(url)


@register.simple_tag
def image_variant(field, key="card"):
    return variant_url(field, key) if field else ""
