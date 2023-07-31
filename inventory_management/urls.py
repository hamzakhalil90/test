"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from inventory_management.views import *

urlpatterns = [
    path('product_type', ProductTypeListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('product', ProductListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),

    path('warehouse', WarehouseListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('plant', PlantListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('launch-product', LaunchProductView.as_view(
            {
                "get": "get",
                "patch": "update"
            }
        )
             ),
]
