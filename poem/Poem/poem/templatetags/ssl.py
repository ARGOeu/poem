import urlparse

from django import template
register = template.Library()

@register.filter(name='to_https')
def to_https(value):
    if not value.endswith('s'):
        return value.replace('http', 'https')

@register.simple_tag
def to_http(abs_url, path):
    url_obj = list(urlparse.urlparse(abs_url))
    if len(url_obj) > 2:
        url_obj[0] = 'http'
        url_obj[2] = path

    return (urlparse.urlunparse(url_obj))
