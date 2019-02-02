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


@register.filter
def remove_underscore(word):
    return word.replace('_', ' ')


@register.filter
def from_to(value,args):
    args_list = args.split(',')
    return value.replace(args_list[0],args_list[1])