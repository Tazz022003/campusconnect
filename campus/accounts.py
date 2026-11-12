import re

from django import forms
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
    """Log in with your email (or your username)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)
        self.fields['username'].label = 'Email or username'
        self.fields['username'].widget.attrs['placeholder'] = 'you@example.com'

    def clean(self):
        identifier = self.cleaned_data.get('username', '')
        if '@' in identifier:
            # swap the email for the matching username, then let Django check the password
            match = User.objects.filter(email__iexact=identifier).first()
            if match:
                self.cleaned_data['username'] = match.username
        return super().clean()


def make_username(email):
    """Build a unique username from the email, e.g. juan@gmail.com -> juan (or juan2 if taken)."""
    base = re.sub(r'[^\w.+-]', '', email.split('@')[0])[:140] or 'user'
    username, n = base, 1
    while User.objects.filter(username__iexact=username).exists():
        n += 1
        username = f'{base}{n}'
    return username


class RegisterForm(UserCreationForm):
    """No username to think about: it is created from the email automatically."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].widget.attrs['placeholder'] = 'you@example.com'
        self.fields['email'].help_text = ''
        self.fields['password1'].help_text = 'At least 8 characters, not only numbers.'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].help_text = ''
        self.fields['password2'].widget.attrs['placeholder'] = 'Type it again'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = make_username(self.cleaned_data['email'])
        if commit:
            user.save()
        return user


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