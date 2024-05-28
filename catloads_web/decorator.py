from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from functools import wraps

def custom_login_required(function=None, redirect_field_name='next', login_url=None):
    """
    Custom login_required decorator that wraps the standard login_required decorator
    to add extra functionality and possibly override the login_url.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Custom logic before checking login
            print("Custom check before proceeding")
            # Use a custom login_url if provided, otherwise fallback to default
            actual_decorator = login_required(
                function=view_func,
                redirect_field_name=redirect_field_name,
                login_url=login_url
            )
            return actual_decorator(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator