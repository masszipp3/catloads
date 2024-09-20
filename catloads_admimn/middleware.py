from django.contrib.gis.geoip2 import GeoIP2
from catloads_web.models import Country
from django.shortcuts import get_object_or_404

class GeoIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if 'country_data' not in request.session:
            ip_address = request.META.get('REMOTE_ADDR', None)
            
            try:
                if ip_address:
                    g = GeoIP2()
                    country_info = g.country(ip_address)
                    country_code = country_info['country_code']
                    country = get_object_or_404(Country, code=country_code)
                else:
                    raise Exception("No IP address found")
            except Exception as e:
                country, _ = Country.objects.get_or_create(code='US', defaults={
                    'name': 'United States',
                    'symbol': '$'
                })
                print(f"GeoIP lookup failed: {e}")

            # Store country data in session
            request.session['country_data'] = {
                'country_code': country.code,
                'country_name': country.name,
                'country_id': country.id,
                'ip':ip_address,
                'e':str(e)
            }

            return self.get_response(request)
