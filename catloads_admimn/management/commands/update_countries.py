import requests
from django.core.management.base import BaseCommand
from catloads_web.models import Country

class Command(BaseCommand):
    help = 'Fetches and updates country information using the countriesnow API'

    def handle(self, *args, **kwargs):
        url = 'https://countriesnow.space/api/v0.1/countries/iso'

        response = requests.get(url)

        if response.status_code == 200:
            countries_data = response.json()['data']

            for country_data in countries_data:
                country_code = country_data['Iso2']
                country_name = country_data['name']

                country, created = Country.objects.update_or_create(
                    code=country_code,
                    defaults={'name': country_name}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added country: {country.name} ({country.code})"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated country: {country.name} ({country.code})"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to fetch countries data. Status code: {response.status_code}"))
