import uuid

from django.db import models

from apps.projects.models import Service


class HealthCheckResult(models.TextChoices):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNEXPECTED_STATUS = "unexpected_status"


class HealthCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    result = models.CharField(max_length=50, choices=HealthCheckResult)
    status_code = models.PositiveIntegerField(default=200, null=True, blank=True)
    response_time_ms = models.PositiveIntegerField()
    error_message = models.TextField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-checked_at"]
        indexes = [models.Index(fields=["service", "-checked_at"])]
        db_table = "health_checks"


class UptimeRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    hour = models.DateTimeField()
    total_checks = models.PositiveIntegerField(default=0)
    successful_checks = models.PositiveIntegerField(default=0)
    avg_response_time_ms = models.PositiveIntegerField(blank=True, default=0)
    min_response_time_ms = models.PositiveIntegerField(blank=True, default=0)
    max_response_time_ms = models.PositiveIntegerField(blank=True, default=0)

    class Meta:
        ordering = ["-hour"]
        db_table = "uptime_records"
        constraints = [
            models.UniqueConstraint(
                fields=["service", "hour"], name="unique_service_hour"
            )
        ]
