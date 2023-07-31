from django.urls import path
from workflows.views import *

urlpatterns = [
    path(
        "",
        WorkflowListingView.as_view({
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }),
    ),
]
