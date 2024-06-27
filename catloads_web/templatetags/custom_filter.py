from django import template
import base64
from decimal import Decimal

register = template.Library()

@register.filter
def encode_base64(value):
    # Assuming the value is an integer and needs to be bytes for base64 encoding
    return base64.b64encode(str(value).encode()).decode()

@register.filter
def round_amount(value):
    return round(float(value))

@register.filter
def substract(value1,value2):
    return float(value1)-float(value2)

@register.filter(name='star_class')
def star_class(index, rating):
    # Ensure rating is a Decimal object
    rating = Decimal(rating)
    index = Decimal(index)
    half_star = Decimal('0.5')
    
    if index <= rating:
        return "star-fill"
    elif index <= rating + half_star:
        return "half fill"
    return ""


@register.filter(name='get_range')
def get_range(start, end):
    """Generates a range from start to end (inclusive)."""
    return range(int(start), int(end) + 1)