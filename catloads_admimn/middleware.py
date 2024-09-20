from django.contrib.gis.geoip2 import GeoIP2

class GeoIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if session contains country data
        # if 'country_data' not in request.session:
            # Get user's IP address
            ip_address = request.META.get('REMOTE_ADDR', None)
            
            # Use GeoIP2 to get country data
            if ip_address:
                g = GeoIP2()
                try:
                    country = g.country(ip_address)
                    # Store country data in session
                    request.session['country_data'] = {
                        'country_code': country['country_code'],
                        'country_name': country['country_name'],
                    }
                except Exception as e:
                    # Handle case where GeoIP2 lookup fails
                    request.session['country_data'] = {
                        'country_code': 'US',  # Fallback to 'US' or some default country
                        'country_name': 'United States',
                    }
                    print(e)

        # Proceed with the request
            response = self.get_response(request)
            return response
