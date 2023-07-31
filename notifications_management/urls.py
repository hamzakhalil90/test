"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from notifications_management.views import *

urlpatterns = [
    path(
        "email",
        EmailTempleteListingView.as_view(
            {"get": "get", "post": "create", "patch": "update", "delete": "destroy"}
        ),
    ),
    path(
        "notification_features",
        NotificationFeaturesListingView.as_view(
            {"get": "get", "post": "create", "delete": "destroy"}
        ),
    ),
]
