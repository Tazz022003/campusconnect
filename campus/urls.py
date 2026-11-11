from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import dashboard, routing, views
from .crud import crud_urlpatterns

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('buildings', views.BuildingViewSet)
router.register('rooms', views.RoomViewSet)
router.register('facilities', views.FacilityViewSet)
router.register('events', views.EventViewSet)
router.register('announcements', views.AnnouncementViewSet)
router.register('reports', views.MaintenanceReportViewSet)

urlpatterns = [
    path('', dashboard.dashboard_view, name='dashboard'),
    path('map/', views.map_page, name='map'),
    path('api/route/', routing.campus_route, name='route'),
    path('api/', include(router.urls)),
] + crud_urlpatterns