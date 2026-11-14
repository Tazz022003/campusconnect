from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

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

# Empty view to satisfy browser requests for a service worker
def serviceworker(request):
    return HttpResponse("// Service Worker intentionally left blank.", content_type="application/javascript")

urlpatterns = [
    path('serviceworker.js', serviceworker, name='serviceworker'),
    path('', dashboard.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('map/', views.map_page, name='map'),
    path('api/route/', routing.campus_route, name='route'),
    path('api/', include(router.urls)),
] + crud_urlpatterns