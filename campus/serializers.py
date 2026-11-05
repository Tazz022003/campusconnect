from rest_framework import serializers

from .models import (
    Announcement, Building, Department, Event, Facility,
    MaintenanceReport, Room,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Building
        fields = [
            'id', 'name', 'description', 'latitude', 'longitude',
            'image', 'department', 'department_name',
        ]


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    latitude = serializers.DecimalField(
        source='building.latitude', max_digits=9, decimal_places=6, read_only=True)
    longitude = serializers.DecimalField(
        source='building.longitude', max_digits=9, decimal_places=6, read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'floor', 'room_type', 'building', 'building_name',
            'department', 'latitude', 'longitude',
        ]


class FacilitySerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'description', 'is_open',
            'building', 'building_name',
        ]


class EventSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date_start', 'date_end',
            'building', 'building_name', 'created_by',
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by = serializers.ReadOnlyField(source='posted_by.username')

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'posted_at', 'posted_by']


class MaintenanceReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.ReadOnlyField(source='reported_by.username')

    class Meta:
        model = MaintenanceReport
        fields = [
            'id', 'description', 'status', 'created_at',
            'reported_by', 'room', 'facility',
        ]