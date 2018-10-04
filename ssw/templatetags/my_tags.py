from django import template

register = template.Library()

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def sub(num, val):
    return num - val

@register.filter
def mul(num, val):
    return num * val

@register.filter
def div(num, val):
    return int(num / val)