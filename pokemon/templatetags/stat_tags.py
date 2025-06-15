from django import template

register = template.Library()

@register.filter(name="stat_color")
def stat_color(value):
    stat_color = [
        (20, "rgba(255, 103, 103, 1)"),
        (40, "rgba(234, 56, 0, 1)"),
        (55, "rgba(235, 105, 0, 1)"),
        (70, "rgba(250, 174, 0, 1)"),
        (85, "rgba(255, 236, 0, 1)"),
        (110, "rgba(211, 255, 135, 1)"),
        (140, "rgba(169, 255, 145, 1)"),
        (180, "rgba(138, 255, 178, 1)"),
        (255, "rgba(121, 255, 214, 1)"),
    ]
    for val, color in stat_color:
        if int(value) <= val:
            return color
    return "rgba(255, 103, 103, 1)"

@register.filter(name="replace")
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)

@register.filter(name="field_name_to_label")
def field_name_to_label(value):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    value = value.replace('_', ' ')
    value = value.replace('-', ' ')
    return value.title()