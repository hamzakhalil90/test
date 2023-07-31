"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from system_logs.views import *

urlpatterns = [
    path(
        "", AuditLogsAPIView.as_view({"get": "get",
                                      "delete": "destroy"}),
    ),
]
