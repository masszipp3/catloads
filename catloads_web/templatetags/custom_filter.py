from django import template
import base64

register = template.Library()

@register.filter
def encode_base64(value):
    # Assuming the value is an integer and needs to be bytes for base64 encoding
    return base64.b64encode(str(value).encode()).decode()