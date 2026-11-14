# campus/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from .models import (
    Announcement, Building, Department, Event, Facility,
    MaintenanceReport, Room,
)
from .serializers import (
    AnnouncementSerializer, BuildingSerializer, DepartmentSerializer,
    EventSerializer, FacilitySerializer, MaintenanceReportSerializer,
    RoomSerializer,
)
from .forms import ProfileForm


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class DepartmentViewSet(BaseViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    search_fields = ['name']


class BuildingViewSet(BaseViewSet):
    queryset = Building.objects.select_related('department')
    serializer_class = BuildingSerializer
    search_fields = ['name', 'description']


class RoomViewSet(BaseViewSet):
    queryset = Room.objects.select_related('building', 'department')
    serializer_class = RoomSerializer
    search_fields = ['name', 'building__name', 'department__name']


class FacilityViewSet(BaseViewSet):
    queryset = Facility.objects.select_related('building')
    serializer_class = FacilitySerializer
    search_fields = ['name', 'facility_type', 'building__name']


class EventViewSet(BaseViewSet):
    queryset = Event.objects.select_related('building')
    serializer_class = EventSerializer
    search_fields = ['title', 'building__name']


class AnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    search_fields = ['title', 'body']


class MaintenanceReportViewSet(BaseViewSet):
    queryset = MaintenanceReport.objects.select_related('room', 'facility')
    serializer_class = MaintenanceReportSerializer
    search_fields = ['description', 'status']


def map_page(request):
    return render(request, 'campus/map.html')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'campus/profile.html', {'form': form})