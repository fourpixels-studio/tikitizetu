from django import template

register = template.Library()


@register.filter
def custom_intcomma(value):
    try:
        value = int(float(value))
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value
