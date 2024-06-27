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
def subtract(value, arg):
    """Subtracts the arg from the value."""
    try:
        print(value - float(arg))
        return value - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def print_rating(rating):
    full_stars = int(rating)
    half_star = rating - full_stars > 0
    empty_slots = 5 - full_stars - half_star
    fullstarstr = '<li class="star star-fill"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16"><path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/></svg></li>'
    emptystarstr = '<li class="star star-fill"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star" viewBox="0 0 16 16"><path d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.56.56 0 0 0-.163-.505L1.71 6.745l4.052-.576a.53.53 0 0 0 .393-.288L8 2.223l1.847 3.658a.53.53 0 0 0 .393.288l4.052.575-2.906 2.77a.56.56 0 0 0-.163.506l.694 3.957-3.686-1.894a.5.5 0 0 0-.461 0z"/></svg></li>'
    halfstarstr = '<li class="star star-fill"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-half" viewBox="0 0 16 16"><path d="M5.354 5.119 7.538.792A.52.52 0 0 1 8 .5c.183 0 .366.097.465.292l2.184 4.327 4.898.696A.54.54 0 0 1 16 6.32a.55.55 0 0 1-.17.445l-3.523 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256a.5.5 0 0 1-.146.05c-.342.06-.668-.254-.6-.642l.83-4.73L.173 6.765a.55.55 0 0 1-.172-.403.6.6 0 0 1 .085-.302.51.51 0 0 1 .37-.245zM8 12.027a.5.5 0 0 1 .232.056l3.686 1.894-.694-3.957a.56.56 0 0 1 .162-.505l2.907-2.77-4.052-.576a.53.53 0 0 1-.393-.288L8.001 2.223 8 2.226z"/></svg></li>'
    result = fullstarstr * full_stars + (halfstarstr if half_star else '') + emptystarstr * empty_slots
    return result

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