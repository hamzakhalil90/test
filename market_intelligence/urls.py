"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from market_intelligence.views import *

urlpatterns = [
    path(
        "brand",
        BrandListingView.as_view(
            {"get": "get", "post": "create", "patch": "update", "delete": "destroy"}
        ),
    ),
    path(
        "brand_type",
        BrandTypeListingView.as_view(
            {"get": "get", "post": "create", "patch": "update", "delete": "destroy"}
        ),
    ),
]
