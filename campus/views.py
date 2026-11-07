from django.shortcuts import render
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    Announcement, Building, Department, Event, Facility,
    MaintenanceReport, Room,
)
from .serializers import (
    AnnouncementSerializer, BuildingSerializer, DepartmentSerializer,
    EventSerializer, FacilitySerializer, MaintenanceReportSerializer,
    RoomSerializer,
)


class BaseViewSet(viewsets.ModelViewSet):
    """Anyone can read; only logged-in users can create/update/delete."""
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    # /api/rooms/?search=registrar  -> also matches the building name
    search_fields = ['name', 'building__name', 'department__name']


class FacilityViewSet(BaseViewSet):
    queryset = Facility.objects.select_related('building')
    serializer_class = FacilitySerializer
    search_fields = ['name', 'facility_type', 'building__name']


class EventViewSet(BaseViewSet):
    queryset = Event.objects.select_related('building', 'created_by')
    serializer_class = EventSerializer
    search_fields = ['title', 'building__name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.select_related('posted_by')
    serializer_class = AnnouncementSerializer
    search_fields = ['title', 'body']

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class MaintenanceReportViewSet(BaseViewSet):
    queryset = MaintenanceReport.objects.select_related('reported_by', 'room', 'facility')
    serializer_class = MaintenanceReportSerializer
    search_fields = ['description', 'status']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

def map_page(request):
    return render(request, 'campus/map.html')
# Create your views here.
