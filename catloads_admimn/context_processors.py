from catloads_web.models import Country

def get_countries(request):
    countries = Country.objects.all()
    return {
        'countries': countries
    }