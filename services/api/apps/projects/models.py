import uuid

from django.conf import settings
from django.db import models


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "projects"


class ServiceType(models.TextChoices):
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"


class CurrentStatusTypes(models.TextChoices):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField()
    service_type = models.CharField(
        max_length=50,
        choices=ServiceType,
        default=ServiceType.HTTP,
    )
    check_interval = models.PositiveIntegerField(default=60)
    expected_status_code = models.PositiveIntegerField(default=200)
    current_status = models.CharField(
        max_length=50,
        choices=CurrentStatusTypes,
        default=CurrentStatusTypes.UNKNOWN,
    )
    timeout = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="services"
    )

    class Meta:
        ordering = ["name"]
        db_table = "services"
