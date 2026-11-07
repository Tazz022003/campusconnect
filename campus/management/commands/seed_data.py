from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from campus.models import (
    Announcement, Building, Department, Event, Facility, Room,
)

# Palawan State University - Main Campus, Tiniguiban Heights, Puerto Princesa City.
# Campus center is about 9.7778, 118.7333.
#
# NOTE: the building coordinates below are PLACEHOLDERS spread around the campus
# center. Replace each one with the real spot: open openstreetmap.org, zoom in on
# the building, right-click it -> "Show address", and copy the coordinates.
# You can also fix them later in the Django admin.
DEPARTMENTS = [
    'Administration',
    'College of Sciences',
    'College of Engineering, Architecture and Technology',
    'College of Business and Accountancy',
    'College of Arts and Humanities',
    'College of Hospitality Management and Tourism',
]

BUILDINGS = [
    # name, description, lat, lng, department
    ('Administration Building', 'Central administration and executive offices.',
     '9.777800', '118.733300', 'Administration'),
    ('College of Sciences Building', 'Science classrooms and laboratories.',
     '9.778400', '118.733900', 'College of Sciences'),
    ('CEAT Building', 'Engineering, Architecture and Technology classrooms and workshops.',
     '9.777200', '118.734200', 'College of Engineering, Architecture and Technology'),
    ('College of Business and Accountancy Building', 'Business and accountancy classrooms.',
     '9.778900', '118.732600', 'College of Business and Accountancy'),
    ('University Library', 'Main campus library and study areas.',
     '9.777000', '118.732800', None),
]

ROOMS = [
    # name, floor, type, building, department
    ('Registrar Office', 1, 'office', 'Administration Building', 'Administration'),
    ('Cashier', 1, 'office', 'Administration Building', 'Administration'),
    ('Science Laboratory 1', 2, 'laboratory', 'College of Sciences Building', 'College of Sciences'),
    ('Computer Laboratory 1', 2, 'laboratory', 'College of Sciences Building', 'College of Sciences'),
    ('Room 101', 1, 'classroom', 'CEAT Building', 'College of Engineering, Architecture and Technology'),
    ('Accounting Room', 1, 'classroom', 'College of Business and Accountancy Building',
     'College of Business and Accountancy'),
]

FACILITIES = [
    # name, type, building
    ('University Library', 'library', 'University Library'),
    ('Clinic', 'clinic', 'Administration Building'),
    ('Canteen', 'canteen', 'CEAT Building'),
]


class Command(BaseCommand):
    help = 'Fill the database with sample PSU campus data (safe to run more than once).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Delete all existing buildings, rooms, facilities, events, '
                 'announcements and departments before seeding.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Room.objects.all().delete()
            Facility.objects.all().delete()
            Event.objects.all().delete()
            Announcement.objects.all().delete()
            Building.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write('Old data cleared.')

        depts = {}
        for name in DEPARTMENTS:
            depts[name], _ = Department.objects.get_or_create(name=name)

        buildings = {}
        for name, desc, lat, lng, dept in BUILDINGS:
            buildings[name], _ = Building.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'latitude': Decimal(lat),
                    'longitude': Decimal(lng),
                    'department': depts.get(dept),
                },
            )

        for name, floor, rtype, bname, dept in ROOMS:
            Room.objects.get_or_create(
                name=name, building=buildings[bname],
                defaults={'floor': floor, 'room_type': rtype, 'department': depts.get(dept)},
            )

        for name, ftype, bname in FACILITIES:
            Facility.objects.get_or_create(
                name=name, building=buildings[bname],
                defaults={'facility_type': ftype},
            )

        now = timezone.now()
        Event.objects.get_or_create(
            title='Campus Orientation',
            defaults={
                'description': 'Welcome event for new students.',
                'date_start': now + timedelta(days=3),
                'date_end': now + timedelta(days=3, hours=3),
                'building': buildings['Administration Building'],
            },
        )
        Announcement.objects.get_or_create(
            title='Welcome to CampusConnect',
            defaults={'body': 'Use the map to find buildings, offices, and rooms.'},
        )

        self.stdout.write(self.style.SUCCESS('Sample data added.'))