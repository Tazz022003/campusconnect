"""
Who can do what in CampusConnect.

Roles (stored in Profile.role):
    student -> can view everything and submit maintenance reports
    staff   -> can also manage rooms, facilities, events, announcements, and reports
    admin   -> can do everything, including buildings, departments, and users
    (a Django superuser is always treated as admin)

Anyone, even logged out, can view (GET) pages and API data.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission

ADMIN = ['admin']
ADMIN_STAFF = ['admin', 'staff']

# key = model name; 'create' = who can add new records; 'manage' = who can edit or delete
ROLE_RULES = {
    'department': {'create': ADMIN, 'manage': ADMIN},
    'building': {'create': ADMIN, 'manage': ADMIN},
    'room': {'create': ADMIN_STAFF, 'manage': ADMIN_STAFF},
    'facility': {'create': ADMIN_STAFF, 'manage': ADMIN_STAFF},
    'event': {'create': ADMIN_STAFF, 'manage': ADMIN_STAFF},
    'announcement': {'create': ADMIN_STAFF, 'manage': ADMIN_STAFF},
    'maintenancereport': {'create': ['student', 'staff', 'admin'], 'manage': ADMIN_STAFF},
}


def get_role(user):
    """Return 'admin', 'staff', 'student', or None (not logged in)."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    profile = getattr(user, 'profile', None)
    return profile.role if profile else 'student'


class RolePermission(BasePermission):
    """DRF permission: everyone can read; writing depends on the user's role."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        role = get_role(request.user)
        if role is None:
            return False

        rules = ROLE_RULES.get(view.queryset.model._meta.model_name, {'create': ADMIN, 'manage': ADMIN})
        needed = rules['create'] if request.method == 'POST' else rules['manage']
        return role in needed