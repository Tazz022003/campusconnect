from django.shortcuts import render
from django.utils import timezone

from .models import (
    Announcement, Building, Event, Facility, MaintenanceReport, Room,
)


def dashboard_view(request):
    now = timezone.now()

    context = {
        # stat cards
        'building_count': Building.objects.count(),
        'room_count': Room.objects.count(),
        'facility_count': Facility.objects.count(),
        'pending_reports': MaintenanceReport.objects.filter(status='pending').count(),

        # lists
        'upcoming_events': (
            Event.objects.filter(date_end__gte=now)
            .select_related('building')[:5]
        ),
        'announcements': Announcement.objects.all()[:5],
        'recent_reports': (
            MaintenanceReport.objects
            .select_related('room', 'facility')[:5]
        ),
    }
    return render(request, 'campus/dashboard.html', context)