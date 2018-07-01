from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from core.constants import LANDLORD, TENANT
from core.models import CustomUser, OfficeSpace

User = get_user_model()


def office_space_factory(number):
    building_names = [
        'Central Tower', 'Centrum LIM', 'Generation Park', 'Intraco I',
        'Millennium Plaza', 'Oxford Tower', 'Palace of Culture and Science',
    ]
    for i in range(number):
        yield {
            # TODO make building names unique
            'name': building_names[i % len(building_names)],
            'street': 'Street 1',
            'city': 'City',
            'zip_code': '01-123',
            'lat': Decimal(random.randint(52, 53)),
            'lng': Decimal(random.randint(20, 21)),
        }


class Command(BaseCommand):
    """
    Populates local database for development with sample random
    objects.

    Never to be used in production.
    # TODO: prevent running in production.

    """
    # TODO add user factory and user number argument
    def add_arguments(self, parser):
        parser.add_argument(
            '--office-spaces',
            type=int,
            default=10
        )

    def handle(self, *args, **options):
        for office_space in office_space_factory(options['office_spaces']):
            OfficeSpace.objects.create(**office_space)

        CustomUser.objects.create(type=LANDLORD, email='lan@lan.lan')
        CustomUser.objects.create(type=TENANT, email='ten@ten.ten')
        # TODO create superuser
