"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from bulk_update_management.views import *

urlpatterns = [
    path('', BulkUpdateView.as_view(
        {
            "patch": "update"
        }
    )
         ),
    path('bulk-import', ImportView.as_view(
            {
                "post": "create"
            }
        )
             ),
    path('show-preview', ExcelPreviewAPI.as_view(
                {
                    "post": "create_preview"
                }
            )
                 ),
    path('get-template', GetTemplateAPI.as_view(
                    {
                        "get": "get_template"
                    }
                )
                     )
]
