
from django.core.management.base import BaseCommand
import json
from property.models import Property
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Load properties from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        
        try:
            with open(json_file, 'r') as file:
                properties_data = json.load(file)
        
            for property_data in properties_data:
                user_id = property_data.pop('user')
                user_instance = User.objects.get(pk=user_id)
                Property.objects.create(user=user_instance, **property_data)
        
            self.stdout.write(self.style.SUCCESS('Successfully loaded properties.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))