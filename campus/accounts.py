from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView

from .models import Profile
from .permissions import get_role


def style_fields(form):
    """Give every form field the Bootstrap look."""
    for f in form.fields.values():
        css = 'form-select' if hasattr(f.widget, 'choices') else 'form-control'
        f.widget.attrs['class'] = css


# ----------------------------------------------------------------------------
# Login and register
# ----------------------------------------------------------------------------
class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class CampusLoginView(LoginView):
    template_name = 'campus/auth/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()          # a Profile (role = student) is created automatically
        login(request, user)
        messages.success(request, 'Welcome to CampusConnect! Your account was created as a student.')
        return redirect('dashboard')

    return render(request, 'campus/auth/register.html', {'form': form})


# ----------------------------------------------------------------------------
# User management (admin only)
# ----------------------------------------------------------------------------
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return get_role(self.request.user) == 'admin'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Only admins can manage users.')
            return redirect('dashboard')
        return super().handle_no_permission()


class UserListView(AdminRequiredMixin, ListView):
    template_name = 'campus/auth/user_list.html'
    paginate_by = 15

    def get_queryset(self):
        # make sure every user has a Profile (older accounts may not)
        for user in User.objects.filter(profile__isnull=True):
            Profile.objects.create(user=user)
        return User.objects.select_related('profile').order_by('username')


class UserRoleUpdateView(AdminRequiredMixin, UpdateView):
    model = Profile
    fields = ['role']
    template_name = 'campus/crud/form.html'
    success_url = reverse_lazy('user_list')

    def get_object(self, queryset=None):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        style_fields(form)
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'singular': 'User Role',
            'subtitle': f'User: {self.object.user.username}',
            'list_url': 'user_list',
            'is_edit': True,
        })
        return ctx

    def form_valid(self, form):
        # don't let an admin lock themselves out
        if self.object.user_id == self.request.user.pk and form.cleaned_data['role'] != 'admin':
            messages.error(self.request, "You can't remove your own admin role.")
            return redirect('user_list')
        messages.success(self.request, 'Role updated.')
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'campus/crud/confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and kwargs.get('pk') == request.user.pk:
            messages.error(request, "You can't delete your own account here.")
            return redirect('user_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'singular': 'User', 'list_url': 'user_list'})
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User deleted.')
        return response