from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('buildings', views.BuildingViewSet)
router.register('rooms', views.RoomViewSet)
router.register('facilities', views.FacilityViewSet)
router.register('events', views.EventViewSet)
router.register('announcements', views.AnnouncementViewSet)
router.register('reports', views.MaintenanceReportViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]