from django import template
import base64

register = template.Library()

@register.filter
def encode_base64(value):
    # Assuming the value is an integer and needs to be bytes for base64 encoding
    return base64.b64encode(str(value).encode()).decode()

@register.filter
def round_amount(value):
    return round(float(value))

@register.simple_tag
def get_range(value):
    return range(1,int(value))