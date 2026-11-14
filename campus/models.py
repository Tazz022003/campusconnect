from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extends Django's User with a role (table 1: users)."""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    image = models.ImageField(upload_to='buildings/', blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='buildings',
    )

    def __str__(self):
        return self.name


class Room(models.Model):
    TYPE_CHOICES = [
        ('classroom', 'Classroom'),
        ('laboratory', 'Laboratory'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)          # e.g. "Room 201" or "Registrar"
    floor = models.PositiveSmallIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='classroom')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rooms',
    )

    def __str__(self):
        return f'{self.name} - {self.building.name}'


class Facility(models.Model):
    TYPE_CHOICES = [
        ('library', 'Library'),
        ('clinic', 'Clinic'),
        ('canteen', 'Canteen'),
        ('gym', 'Gym'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    facility_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    description = models.TextField(blank=True)
    is_open = models.BooleanField(default=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='facilities')

    class Meta:
        verbose_name_plural = 'facilities'

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='events',
    )

    class Meta:
        ordering = ['date_start']

    def __str__(self):
        return self.title


class Announcement(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements',
    )

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return self.title


class MaintenanceReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
    ]
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reports',
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report #{self.pk} ({self.status})'