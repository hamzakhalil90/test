from django.db import models
from utils.base_models import LogsMixin
from user_management.models import User


class AuditLogs(LogsMixin):
    operation_choices = (
        ("CREATED", "CREATED"),
        ("UPDATED", "UPDATED"),
        ("DELETED", "DELETED"),
        ("LOGIN", "LOGIN"),
    )
    feature = models.CharField(max_length=20, null=True, blank=True)
    object = models.CharField(max_length=20, null=True, blank=True)
    operation = models.CharField(max_length=10, null=True, blank=True, choices=operation_choices)
    user = models.ForeignKey(User, related_name="audits", on_delete=models.PROTECT, null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
