"""
LCLPD_backend URL Configuration
"""
from django.urls import path
from user_management.views import *

urlpatterns = [
    path('login', LoginAPIView.as_view({"post": "post"})),
    path('change-password', ChangePasswordAPI.as_view({"post": "patch"})),
    path('forget-password', ForgetPasswordAPI.as_view({"post": "post"})),
    path('verify_otp', VerifyOtpAPI.as_view({"post": "post"})),
    path('department', DepartmentListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('sub-department', SubDepartmentListingView.as_view(
            {
                "get": "get",
                "post": "create",
                "patch": "update",
                "delete": "destroy"
            }
        )
             ),
    path('company', CompanyListingView.as_view(
        {
            "get": "get",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('financial_details', FinancialDataAPI.as_view(
            {
                "get": "get",
                "post": "create",
                "patch": "update",
                "delete": "destroy"
            }
        )
             ),
    path('currency', CurrencyListingView.as_view(
            {
                "get": "get",
            }
        )
             ),
    path('grade', GradeListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('designation', DesignationListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('employee', EmployeeListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('user', UserListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('usergroup', UserGroupView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('feature', FeatureListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),

    path('role', RoleListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),

    path('permission', PermissionListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),

    path('module', ModuleListingView.as_view(
        {
            "get": "get",
            "post": "create",
            "patch": "update",
            "delete": "destroy"
        }
    )
         ),
    path('locked-user', LockedUsersAPI.as_view(
        {
            "get": "get",
            "patch": "update"
        }
    )
         ),

    path('dashboard', FeatureCountDashboard.as_view(
        {
            "get": "get",
        }
    )
         ),
    path('weekday', WeekdayView.as_view(
            {
                "get": "get",
            }
        )
             ),

]
