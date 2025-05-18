from django.core.management.base import BaseCommand
from api.models import Location

class Command(BaseCommand):
    help = 'Populates the database with Kazakhstan cities and their GPS coordinates'

    def handle(self, *args, **options):
        # Kazakhstan cities with actual GPS coordinates
        city_coordinates = {
            'Almaty': {'latitude': 43.238949, 'longitude': 76.889709},
            'Nur-Sultan': {'latitude': 51.169392, 'longitude': 71.449074},
            'Shymkent': {'latitude': 42.315514, 'longitude': 69.586907},
            'Karaganda': {'latitude': 49.807754, 'longitude': 73.088504},
            'Taraz': {'latitude': 42.900799, 'longitude': 71.378102},
            'Atyrau': {'latitude': 47.095585, 'longitude': 51.877508},
            'Aktau': {'latitude': 43.635921, 'longitude': 51.198199},
            'Aktobe': {'latitude': 50.300374, 'longitude': 57.154882},
            'Oral': {'latitude': 51.227821, 'longitude': 51.386104},
            'Pavlodar': {'latitude': 52.285577, 'longitude': 76.940947},
            'Semey': {'latitude': 50.413728, 'longitude': 80.258585},
            'Oskemen': {'latitude': 49.948027, 'longitude': 82.627949},
            'Kyzylorda': {'latitude': 44.853108, 'longitude': 65.498416},
        }

        # Create locations for each city
        locations_created = 0
        for city_name, coords in city_coordinates.items():
            location, created = Location.objects.get_or_create(
                name=city_name,
                defaults={
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude']
                }
            )
            
            if created:
                locations_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created location for {city_name}'))
            else:
                self.stdout.write(f'Location for {city_name} already exists')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {locations_created} locations'))
