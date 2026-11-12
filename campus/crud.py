"""
Generic CRUD pages for CampusConnect.

Each table is described by one CrudConfig below. From that config we build:
    list   -> /buildings/              (search + pagination)
    create -> /buildings/add/          (login required)
    update -> /buildings/<id>/edit/    (login required)
    delete -> /buildings/<id>/delete/  (login required, with confirmation)

URL names follow the pattern  <name>_list / <name>_create / <name>_update / <name>_delete
e.g. building_list, building_create, building_update, building_delete.
"""
from dataclasses import dataclass, field
from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import redirect
from django.urls import path, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import (
    Announcement, Building, Department, Event, Facility,
    MaintenanceReport, Room,
)
from .permissions import ROLE_RULES, get_role


@dataclass
class CrudConfig:
    name: str                 # used for url names, e.g. 'building'
    slug: str                 # used in the url, e.g. 'buildings'
    model: type
    title: str                # plural title, e.g. 'Buildings'
    singular: str             # e.g. 'Building'
    columns: list             # [(header, 'attribute.path'), ...] shown in the list table
    fields: list              # model fields shown in the add/edit form
    search: list = field(default_factory=list)            # fields searched by the search box
    user_field: str = ''                                  # filled with the logged-in user on create
    datetime_fields: list = field(default_factory=list)   # fields shown with a date-time picker

    # who may add / edit+delete records of this table (rules live in permissions.py)
    @property
    def create_roles(self):
        return ROLE_RULES[self.model._meta.model_name]['create']

    @property
    def manage_roles(self):
        return ROLE_RULES[self.model._meta.model_name]['manage']


# ----------------------------------------------------------------------------
# One config per table. To add a new table, add one more CrudConfig here.
# ----------------------------------------------------------------------------
CONFIGS = [
    CrudConfig(
        name='department', slug='departments', model=Department,
        title='Departments', singular='Department',
        columns=[('Name', 'name'), ('Description', 'description')],
        fields=['name', 'description'],
        search=['name', 'description'],
    ),
    CrudConfig(
        name='building', slug='buildings', model=Building,
        title='Buildings', singular='Building',
        columns=[('Name', 'name'), ('Department', 'department.name'),
                 ('Latitude', 'latitude'), ('Longitude', 'longitude')],
        fields=['name', 'description', 'latitude', 'longitude', 'image', 'department'],
        search=['name', 'description'],
    ),
    CrudConfig(
        name='room', slug='rooms', model=Room,
        title='Rooms & Offices', singular='Room',
        columns=[('Name', 'name'), ('Building', 'building.name'), ('Floor', 'floor'),
                 ('Type', 'get_room_type_display'), ('Department', 'department.name')],
        fields=['name', 'floor', 'room_type', 'building', 'department'],
        search=['name', 'building__name'],
    ),
    CrudConfig(
        name='facility', slug='facilities', model=Facility,
        title='Facilities', singular='Facility',
        columns=[('Name', 'name'), ('Type', 'get_facility_type_display'),
                 ('Building', 'building.name'), ('Open', 'is_open')],
        fields=['name', 'facility_type', 'building', 'description', 'is_open'],
        search=['name', 'building__name'],
    ),
    CrudConfig(
        name='event', slug='events', model=Event,
        title='Events', singular='Event',
        columns=[('Title', 'title'), ('Start', 'date_start'), ('End', 'date_end'),
                 ('Building', 'building.name')],
        fields=['title', 'description', 'date_start', 'date_end', 'building'],
        search=['title', 'building__name'],
        user_field='created_by',
        datetime_fields=['date_start', 'date_end'],
    ),
    CrudConfig(
        name='announcement', slug='announcements', model=Announcement,
        title='Announcements', singular='Announcement',
        columns=[('Title', 'title'), ('Posted', 'posted_at'), ('By', 'posted_by.username')],
        fields=['title', 'body'],
        search=['title', 'body'],
        user_field='posted_by',
    ),
    CrudConfig(
        name='report', slug='reports', model=MaintenanceReport,
        title='Maintenance Reports', singular='Maintenance Report',
        columns=[('Report', 'description'), ('Status', 'get_status_display'),
                 ('Room', 'room.name'), ('Facility', 'facility.name'),
                 ('Reported by', 'reported_by.username')],
        fields=['description', 'status', 'room', 'facility'],
        search=['description', 'status'],
        user_field='reported_by',
    ),
]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def resolve(obj, dotted):
    """Follow a path like 'building.name'. Returns '' if something along the way is empty."""
    value = obj
    for part in dotted.split('.'):
        value = getattr(value, part, None)
        if value is None:
            return ''
        if callable(value):
            value = value()
    return value


def cell_text(obj, accessor):
    """Turn a value into display text for the list table."""
    value = resolve(obj, accessor)
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, datetime):
        return timezone.localtime(value).strftime('%b %d, %Y %I:%M %p')
    text = str(value)
    return text if len(text) <= 60 else text[:57] + '...'


def url_names(cfg):
    return {
        'list_url': f'{cfg.name}_list',
        'create_url': f'{cfg.name}_create',
        'update_url': f'{cfg.name}_update',
        'delete_url': f'{cfg.name}_delete',
    }


def base_context(cfg, user):
    role = get_role(user)
    return {
        'title': cfg.title,
        'singular': cfg.singular,
        'can_create': role in cfg.create_roles,   # shows the "Add" button
        'can_manage': role in cfg.manage_roles,   # shows the Edit / Delete buttons
        **url_names(cfg),
    }


# ----------------------------------------------------------------------------
# Views
# ----------------------------------------------------------------------------
class CrudListView(ListView):
    cfg = None
    template_name = 'campus/crud/list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = self.cfg.model.objects.all()
        q = self.request.GET.get('q', '').strip()
        if q and self.cfg.search:
            condition = Q()
            for name in self.cfg.search:
                condition |= Q(**{name + '__icontains': q})
            qs = qs.filter(condition)
        if not qs.ordered:
            qs = qs.order_by('pk')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(base_context(self.cfg, self.request.user))
        ctx['q'] = self.request.GET.get('q', '').strip()
        ctx['headers'] = [label for label, _ in self.cfg.columns]
        ctx['rows'] = [
            {'obj': obj, 'cells': [cell_text(obj, accessor) for _, accessor in self.cfg.columns]}
            for obj in ctx['object_list']
        ]
        return ctx


class RoleRequiredMixin(UserPassesTestMixin):
    """Only users whose role is allowed (see permissions.py) can open the page."""
    cfg = None
    required = 'manage'     # 'create' or 'manage'

    def test_func(self):
        rules = ROLE_RULES[self.cfg.model._meta.model_name]
        return get_role(self.request.user) in rules[self.required]

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Your account does not have permission to do that.')
            return redirect(f'{self.cfg.name}_list')
        return super().handle_no_permission()      # not logged in -> go to the login page


class CrudFormMixin(RoleRequiredMixin):
    cfg = None
    template_name = 'campus/crud/form.html'
    is_edit = False

    def get_queryset(self):
        return self.cfg.model.objects.all()

    def get_form_class(self):
        return modelform_factory(self.cfg.model, fields=self.cfg.fields)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for f in form.fields.values():
            widget = f.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = 'form-select'
            else:
                widget.attrs['class'] = 'form-control'
            if isinstance(widget, forms.Textarea):
                widget.attrs['rows'] = 4
        for name in self.cfg.datetime_fields:
            if name in form.fields:
                form.fields[name].widget = forms.DateTimeInput(
                    attrs={'type': 'datetime-local', 'class': 'form-control'},
                    format='%Y-%m-%dT%H:%M',
                )
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(base_context(self.cfg, self.request.user))
        ctx['is_edit'] = self.is_edit
        return ctx

    def get_success_url(self):
        return reverse_lazy(f'{self.cfg.name}_list')

    def form_valid(self, form):
        # on create, remember who made it (event.created_by, announcement.posted_by, ...)
        if self.cfg.user_field and not form.instance.pk:
            setattr(form.instance, self.cfg.user_field, self.request.user)
        response = super().form_valid(form)
        messages.success(self.request, f'{self.cfg.singular} saved.')
        return response


class CrudCreateView(CrudFormMixin, CreateView):
    is_edit = False
    required = 'create'


class CrudUpdateView(CrudFormMixin, UpdateView):
    is_edit = True
    required = 'manage'


class CrudDeleteView(RoleRequiredMixin, DeleteView):
    cfg = None
    required = 'manage'
    template_name = 'campus/crud/confirm_delete.html'

    def get_queryset(self):
        return self.cfg.model.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(base_context(self.cfg, self.request.user))
        return ctx

    def get_success_url(self):
        return reverse_lazy(f'{self.cfg.name}_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'{self.cfg.singular} deleted.')
        return response


# ----------------------------------------------------------------------------
# URL patterns (imported by campus/urls.py)
# ----------------------------------------------------------------------------
crud_urlpatterns = []
for _cfg in CONFIGS:
    crud_urlpatterns += [
        path(f'{_cfg.slug}/',
             CrudListView.as_view(cfg=_cfg), name=f'{_cfg.name}_list'),
        path(f'{_cfg.slug}/add/',
             CrudCreateView.as_view(cfg=_cfg), name=f'{_cfg.name}_create'),
        path(f'{_cfg.slug}/<int:pk>/edit/',
             CrudUpdateView.as_view(cfg=_cfg), name=f'{_cfg.name}_update'),
        path(f'{_cfg.slug}/<int:pk>/delete/',
             CrudDeleteView.as_view(cfg=_cfg), name=f'{_cfg.name}_delete'),
    ]