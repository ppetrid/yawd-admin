from django import template

register = template.Library()

@register.filter
def divide(value, num):
    return int(value / num)