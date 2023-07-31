import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from dateutil.relativedelta import relativedelta
import datetime
from django.db.models import Q, UniqueConstraint
from LCLPD_backend.settings import *
from area_management.models import *
from utils.base_models import LogsMixin
from utils.reusable_methods import generate_access_token

# Create your models here.

class NotificationFeatures(LogsMixin):
    """Model for storing features"""

    name = models.TextField(max_length=50, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "is_deleted"],
                name="unique_notification_feature",
                condition=Q(is_deleted="f"),
            )
        ]

class EmailTemplate(LogsMixin):
    name = models.CharField(max_length=500)
    subject = models.TextField(max_length=500)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    notification_feature = models.ForeignKey(NotificationFeatures, on_delete=models.CASCADE,
                                             related_name="notification_feature_name", blank=True, null=True)
