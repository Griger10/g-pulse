import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    webhook_url = models.URLField(blank=True, default="")

    class Meta:
        db_table = "users"
