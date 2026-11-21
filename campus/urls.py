from django.contrib.auth.views import LogoutView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import accounts, dashboard, routing, views
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

    path('login/', accounts.CampusLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', accounts.register, name='register'),
    path('users/', accounts.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/role/', accounts.UserRoleUpdateView.as_view(), name='user_role'),
    path('users/<int:pk>/delete/', accounts.UserDeleteView.as_view(), name='user_delete'),
] + crud_urlpatterns