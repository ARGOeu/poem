from django import template

register = template.Library()


@register.filter(name='get_version')
def get_version(value):
    return value.split('(')[-1][0:-1]
