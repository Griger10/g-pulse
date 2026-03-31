import uuid

from django.conf import settings
from django.db import models

from apps.projects.models import Service


class AlertCondition(models.TextChoices):
    STATUS_CHANGE = "status_change"
    CONSECUTIVE_FAILURES = "consecutive_failures"
    RESPONSE_TIME = "response_time"


class TransportType(models.TextChoices):
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"


class AlertRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="alert_rules"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="alert_rules"
    )
    condition = models.CharField(
        max_length=50, choices=AlertCondition, default=AlertCondition.STATUS_CHANGE
    )
    transport = models.CharField(max_length=20, choices=TransportType)
    threshold = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    cooldown_minutes = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alert_rules"


class StatusAlertEvent(models.TextChoices):
    SENT = "sent"
    FAILED = "failed"
    COOLDOWN = "cooldown"


class AlertEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(
        AlertRule, on_delete=models.CASCADE, related_name="alert_events"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="alert_events"
    )
    status = models.CharField(
        max_length=50, choices=StatusAlertEvent, default=StatusAlertEvent.SENT
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alert_events"
