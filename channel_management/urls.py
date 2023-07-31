"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from channel_management.views import *

urlpatterns = [
    path('', ChannelView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('outlet', OutletView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('gis-dashboard', GisOutletView.as_view(
            {
                "get": "get",
            }
        )
             ),
    path('bulk-assignment', BulkAssignmentView.as_view(
            {
                "patch": "update",
            }
        )
             ),
    path('distributor', OutletView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
             ),
    path('distributor-listing', DistributorListingView.as_view(
            {
                "get": "get"
            }
        )
                 )

]
