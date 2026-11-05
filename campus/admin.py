
from django.contrib import admin
from .models import (Profile, Department, Building, Room, Facility,
                     Event, Announcement, MaintenanceReport)

for model in (Profile, Department, Building, Room, Facility,
              Event, Announcement, MaintenanceReport):
    admin.site.register(model)
# Register your models here.
