from django.contrib.auth.views import redirect_to_login

# Pages anyone can open without logging in (everything else needs a login)
OPEN_PREFIXES = (
    '/login/',
    '/register/',
    '/static/',
    '/media/',
    '/admin/',          # Django admin has its own login page
    '/favicon.ico',
)


class RequireLoginMiddleware:
    """Send visitors who are not logged in to the login page first."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.path.startswith(OPEN_PREFIXES):
            # after logging in, they are sent back to the page they wanted
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)