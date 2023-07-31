from rest_framework import viewsets
from user_management.user_controller import *
from utils.base_authentication import JWTAuthentication
from user_management.serializers import LoginSerializer, GradeSerializer
from utils.base_permission import *
from rest_framework.permissions import IsAdminUser

login_controller = LoginController()
forget_password_controller = ForgetPasswordController()
change_password_controller = ChangePasswordController()
verify_otp = VerifyOtpController()
user_controller = UserListingController()
feature_controller = FeatureController()
dep_controller = DepartmentController()
sub_dep_controller = SubDepartmentController()
desg_controller = DesignationController()
emp_controller = EmployeeController()
role_controller = RoleController()
module_controller = ModuleController()
permission_controller = PermissionController()
locked_controller = LockedUsersController()
grade_controller = GradeController()
user_group_controller = UserGroupController()
feature_count_controller = FeatureCountController()
company_controller = CompanyController()
currency_controller = CurrencyController()
weekday_controller = WeekdayController()
financial_controller = FinancialDataController()


class LoginAPIView(viewsets.ModelViewSet):
    """
        An endpoint for user login.
        """
    serializer_class = LoginSerializer

    def post(self, request):
        return login_controller.login(request)


class ChangePasswordAPI(viewsets.ModelViewSet):
    """
    An endpoint for changing password.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = ChangePasswordSerializer

    def patch(self, request):
        return change_password_controller.update(request)


class ForgetPasswordAPI(viewsets.ModelViewSet):
    """
    An endpoint for forget password.
    """
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        return forget_password_controller.forget_password(request)


class VerifyOtpAPI(viewsets.ModelViewSet):
    """
    An endpoint for token verification.
    """
    serializer_class = VerifyOtpSerializer

    def post(self, request):
        return verify_otp.verify(request)


class DepartmentListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = DepartmentSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return dep_controller.get_department(request)

    def create(self, request):
        return dep_controller.create_department(request)

    def update(self, request):
        return dep_controller.update_department(request)

    def destroy(self, request):
        return dep_controller.delete_department(request)


class SubDepartmentListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = SubDepartmentSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return sub_dep_controller.get_sub_department(request)

    def create(self, request):
        return sub_dep_controller.create_sub_department(request)

    def update(self, request):
        return sub_dep_controller.update_sub_department(request)

    def destroy(self, request):
        return sub_dep_controller.delete_sub_department(request)


class DesignationListingView(viewsets.ModelViewSet):
    """
    Endpoints for designation CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = DesignationSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return desg_controller.get_designation(request)

    def create(self, request):
        return desg_controller.create_designation(request)

    def update(self, request):
        return desg_controller.update_designation(request)

    def destroy(self, request):
        return desg_controller.delete_designation(request)


class EmployeeListingView(viewsets.ModelViewSet):
    """
    Endpoints for Employee CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = EmployeeSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return emp_controller.get_employee(request)

    def create(self, request):
        return emp_controller.create_employee(request)

    def update(self, request):
        return emp_controller.update_employee(request)

    def destroy(self, request):
        return emp_controller.delete_employee(request)


class UserListingView(viewsets.ModelViewSet):
    """
    Endpoints for users CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = UserListingSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return user_controller.get_user(request)

    def create(self, request):
        return user_controller.create_user(request)

    def update(self, request):
        return user_controller.update_user(request)

    def destroy(self, request):
        return user_controller.delete_user(request)


class UserGroupView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = UserGroupSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return user_group_controller.get_user_group(request)

    def create(self, request):
        return user_group_controller.create_user_group(request)

    def update(self, request):
        return user_group_controller.update_user_group(request)

    def destroy(self, request):
        return user_group_controller.delete_user_group(request)


class FeatureListingView(viewsets.ModelViewSet):
    """
    Endpoints for Feature CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = FeatureListingSreializer

    def get(self, request):
        return feature_controller.get_feature(request)

    def create(self, request):
        return feature_controller.create_feature(request)

    def update(self, request):
        return feature_controller.update_feature(request)

    def destroy(self, request):
        return feature_controller.delete_feature(request)


class RoleListingView(viewsets.ModelViewSet):
    """
    Endpoints for role CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)
    serializer_class = RoleSerializer

    def get(self, request):
        return role_controller.get_role(request)

    def create(self, request):
        return role_controller.create_role(request)

    def update(self, request):
        return role_controller.update_role(request)

    def destroy(self, request):
        return role_controller.delete_role(request)


class PermissionListingView(viewsets.ModelViewSet):
    """
    Endpoints for permission CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = PermissionSerializer

    def get(self, request):
        return permission_controller.get_permission(request)

    def create(self, request):
        return permission_controller.create_permission(request)

    def update(self, request):
        return permission_controller.update_permission(request)

    def destroy(self, request):
        return permission_controller.delete_permission(request)


class ModuleListingView(viewsets.ModelViewSet):
    """
    Endpoints for Module CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)
    serializer_class = ModuleSerializer

    def get(self, request):
        return module_controller.get_module(request)

    def create(self, request):
        return module_controller.create_module(request)

    def update(self, request):
        return module_controller.update_module(request)

    def destroy(self, request):
        return module_controller.delete_module(request)


class GradeListingView(viewsets.ModelViewSet):
    """
    Endpoints for Module CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)
    serializer_class = GradeSerializer

    def get(self, request):
        return grade_controller.get_grade(request)

    def create(self, request):
        return grade_controller.create_grade(request)

    def update(self, request):
        return grade_controller.update_grade(request)

    def destroy(self, request):
        return grade_controller.delete_grade(request)


class LockedUsersAPI(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = UserListingSerializer

    def get(self, request):
        return locked_controller.get_locked_users(request)

    def update(self, request):
        return locked_controller.update_locked_users(request)


class FeatureCountDashboard(viewsets.ModelViewSet):
    # authentication_classes = (JWTAuthentication,)

    def get(self, request):
        return feature_count_controller.get_count(request)


class WeekdayView(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        return weekday_controller.get_days(request)


class CurrencyListingView(viewsets.ModelViewSet):
    """
    Endpoints for permission CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = CurrencySerializer

    def get(self, request):
        return currency_controller.get_currency(request)


class CompanyListingView(viewsets.ModelViewSet):
    """
    Endpoints for permission CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = CompanySerializer

    def get(self, request):
        return company_controller.get_company(request)

    def create(self, request):
        return company_controller.create_company(request)

    def update(self, request):
        return company_controller.update_company(request)

    def destroy(self, request):
        return company_controller.delete_company(request)


class FinancialDataAPI(viewsets.ModelViewSet):
    """
    Endpoints for permission CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = FinancialDataSerializer

    def get(self, request):
        return financial_controller.get_fiscal(request)

    def create(self, request):
        return financial_controller.create_fiscal(request)

    def update(self, request):
        return financial_controller.update_fiscal(request)

    def destroy(self, request):
        return financial_controller.delete_fiscal(request)
