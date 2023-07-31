from django.db import models
from django.utils import timezone


class LogsMixin(models.Model):
    status_choices = (
        ("INACTIVE", "INACTIVE"),
        ("ACTIVE", "ACTIVE"),
    )
    """Add the generic fields and relevant methods common to support mostly
    models
    """
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_active = models.CharField(max_length=8, default="ACTIVE", choices=status_choices)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        """meta class for LogsMixin"""
        abstract = True
