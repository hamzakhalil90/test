"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from area_management.views import *

urlpatterns = [

    path('country', CountryView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),

    path('region', RegionView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('city', CityView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('zone', ZoneView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('sub_zone', SubZoneView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('temporary_stored_countries', TemporaryCountryView.as_view(
        {
            "get": "get",
        }
    )
         )
]
