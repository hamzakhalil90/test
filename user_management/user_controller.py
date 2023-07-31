import json
import threading
from bulk_update_management.bulk_update_helper import *
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from utils.export_columns import *
from utils.send_email import *
from utils.export_utils import ExportUtility
from utils.helper import *
from copy import deepcopy

logs_controller = AuditLogsController()


# Create your views here.
class LoginController:
    feature_name = "Auth"
    """
    An endpoint for Login
    """
    serializer_class = LoginSerializer
    logs_controller = AuditLogsController()

    def login(self, request):
        # make the request data mutable
        request.POST._mutable = True
        # strip whitespace from the email and password
        request.data["email"] = request.data.get("email", "").strip()
        request.data["password"] = request.data.get("password", "").strip()
        # make the request data mutable
        request.POST._mutable = False
        # Get email and password from request data
        email = request.data.get("email")
        password = request.data.get("password")
        # create the serializer instance
        serialized_data = self.serializer_class(data=request.data)
        # check if the data is valid
        if not serialized_data.is_valid():
            # if not valid return an error message
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=401)
        # authenticate user
        user = authenticate(username=email, password=password)
        if not user or user.is_deleted:
            # if not valid user return an error message
            return create_response({}, message=INCORRECT_EMAIL_OR_PASSWORD, status_code=401)
        # prepare response data
        response_data = {
            "token": user.get_access_token(),
            "name": user.get_full_name(),
            "role": "is_superuser" if user.is_superuser else RoleSerializer(user.role).data,
            "guid": user.guid
        }
        # update or create token
        Token.objects.update_or_create(defaults={"token": response_data.get("token")}, user_id=user.guid)
        user.failed_login_attempts = 0
        user.last_failed_time = None
        user.last_login = timezone.now()
        user.save()
        logs_controller.create_logs(feature=self.feature_name, operation=OperationType.LOGIN, user=user)
        # return success message
        return create_response(response_data, SUCCESSFUL, status_code=200)


class ChangePasswordController:
    feature_name = "Change Password"
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer

    def update(self, request):
        # make the request data mutable
        request.POST._mutable = True
        # strip whitespace from the passwords
        request.data["old_password"] = request.data.get("old_password").strip()
        request.data["new_password"] = request.data.get("new_password").strip()
        request.data["confirm_password"] = request.data.get("confirm_password").strip()
        # make the request data mutable
        request.POST._mutable = True
        # create the serializer instance
        serializer = self.serializer_class(data=request.data, context={"user": request.user})
        # check if the data is valid
        if not serializer.is_valid():
            # If the data is not valid, return a response with the errors
            return create_response({}, get_first_error_message_from_serializer_errors(serializer.errors, UNSUCCESSFUL),
                                   status_code=400)
        # check if the new password and confirm password match
        if request.data.get('new_password') != request.data.get('confirm_password'):
            # if not match return error message
            return create_response({}, message=PASSWORD_DOES_NOT_MATCH, status_code=403)

        # Check old password
        if not request.user.check_password(request.data.get("old_password")):
            # if the old password is incorrect return error message
            return create_response({}, message=INCORRECT_OLD_PASSWORD, status_code=400)

        # set_password also hashes the password that the users will get
        request.user.set_password(request.data.get("new_password"))
        request.user.save()
        logs_controller.create_logs(feature=self.feature_name, operation=OperationType.UPDATED, user=request.user)
        # return success message
        return create_response({}, SUCCESSFUL, status_code=200)


class ForgetPasswordController:
    feature_name = "Forget Password"
    serializer_class = ForgetPasswordSerializer

    def forget_password(self, request):
        # Deserialize the request data using the defined serializer
        serialized_data = self.serializer_class(data=request.data)
        # check if the request data is valid
        if not serialized_data.is_valid():
            # if invalid return an error message
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   401)
        try:
            # Try to filter the user with the provided email
            user = User.objects.filter(email=request.data.get("email")).first()
            if not user:
                # if user not found return an error message
                return create_response({}, USER_NOT_FOUND, status_code=404)
            # generate OTP
            otp = generate_six_length_random_number()
            user.otp = otp
            user.otp_generated_at = timezone.now()
            user.save()
            # Prepare the email subject and message
            try:
                template = EmailTemplate.objects.get(notification_feature__name=self.feature_name)
                variables = {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "otp": user.otp
                }
                message = pass_variables_into_string(template.body, variables)
                subject = template.subject

            except:
                subject = "Password Recovery Request"
                message = f"""
                    OTP: {otp}
                    """

            recipient_list = [request.data.get("email")]
            # Send the email
            t = threading.Thread(target=send_mail, args=(subject, message, EMAIL_HOST_USER, recipient_list))
            t.start()
            logs_controller.create_logs(feature=self.feature_name, operation=OperationType.UPDATED, user=user)
            # return success message
            return create_response({}, EMAIL_SUCCESSFULLY_SENT, status_code=200)
        except Exception as e:
            # print the error message
            print(e)
            # return error message
            return create_response({}, e, status_code=500)


class VerifyOtpController:
    feature_name = "OTP verification"
    serializer_class = VerifyOtpSerializer

    def verify(self, request):
        # make the request data mutable
        request.POST._mutable = True
        # strip whitespace from the passwords
        request.data["new_password"] = request.data.get("new_password").strip()
        request.data["confirm_password"] = request.data.get("confirm_password").strip()
        # make the request data mutable
        request.POST._mutable = True
        try:
            # check OTP time delay
            time_delay = timezone.now() - timezone.timedelta(seconds=300)
            user = User.objects.filter(otp=request.data.get("otp"), otp_generated_at__gt=time_delay).first()
            if not user:
                # if not valid OTP return an error message
                return create_response({}, INVALID_OTP, status_code=404)
            # create the serializer instance
            serialized_data = self.serializer_class(data=request.data, context={"user": user})
            # check if the data is valid
            if not serialized_data.is_valid():
                # if not valid return an error message
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL), 401)
            # check if the new password and confirm password match
            if request.data.get('new_password') != request.data.get('confirm_password'):
                # if not match return error message
                return create_response({}, message=PASSWORD_DOES_NOT_MATCH, status_code=403)
            # set new password
            user.set_password(request.data.get("new_password"))
            # clear OTP
            user.otp = None
            user.save()
            logs_controller.create_logs(feature=self.feature_name, operation=OperationType.UPDATED, user=user)
            # return success message
            return create_response({}, SUCCESSFUL, status_code=200)
        except Exception as e:
            print(e)
            return create_response({}, e, status_code=500)


class DepartmentController:
    feature_name = "Department"
    serializer_class = DepartmentSerializer
    export_util = ExportUtility()

    def get_department(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        category = get_query_param(request, 'category', None)
        export = get_query_param(request, 'export', None)
        is_active = get_query_param(request, "is_active", None)
        if id:
            kwargs["id"] = id
        if category:
            kwargs["category"] = category
        if order and order_by:
            if order_by == "department_head":
                order_by = "department_head__first_name"
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["name__icontains"] = search
            search_kwargs = seacrh_text_parser(search, search_kwargs, prefix="department_head__")
        if is_active:
            kwargs["is_active"] = is_active
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_department_data(serialized_asset=serialized_data,
                                                           columns=DEPARTMENT_EXPORT_COLUMNS,
                                                           export_name="Department Listing")
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_department(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_department(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)

                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())

                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_department(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.designation.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class SubDepartmentController:
    feature_name = "Sub Department"
    serializer_class = SubDepartmentSerializer
    export_util = ExportUtility()

    def get_sub_department(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        category = get_query_param(request, 'category', None)
        export = get_query_param(request, 'export', None)
        is_active = get_query_param(request, "is_active", None)
        department = get_query_param(request, "department", None)
        if id:
            kwargs["id"] = id
        if category:
            kwargs["category"] = category
        if order and order_by:
            if order_by == "head":
                order_by = "head__first_name"
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["name__icontains"] = search
            search_kwargs = seacrh_text_parser(search, search_kwargs, prefix="head__")
        if department:
            kwargs["department"] = department
        if is_active:
            kwargs["is_active"] = is_active
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_department_data(serialized_asset=serialized_data,
                                                           columns=SUB_DEPARTMENT_EXPORT_COLUMNS,
                                                           export_name="Sub Department Listing")
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_sub_department(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_sub_department(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values
                                                )
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_sub_department(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class DesignationController:
    feature_name = "Designation"
    serializer_class = DesignationSerializer
    export_util = ExportUtility()

    def get_designation(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        category = get_query_param(request, "category", None)
        grade_from = get_query_param(request, "grade_from", None)
        grade_to = get_query_param(request, "grade_to", None)
        department = get_query_param(request, "department", None)
        is_active = get_query_param(request, "is_active", None)

        if grade_from and grade_to:
            kwargs["grade__gte"] = grade_from
            kwargs["grade__lte"] = grade_to
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order_by == "category":
                order_by = "department__category"
            if order_by == "department":
                order_by = "department__name"
            if order == "desc":
                order_by = f"-{order_by}"
        if category:
            kwargs["department__category"] = category
        if search:
            kwargs["name__icontains"] = search
        if department:
            kwargs = get_params("department", department, kwargs)
        kwargs["is_deleted"] = False
        if is_active:
            kwargs["is_active"] = is_active
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_designation_data(serialized_asset=serialized_data,
                                                            columns=DESIGNATION_EXPORT_COLUMNS,
                                                            export_name="Designation Listing")
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_designation(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_designation(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_designation(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 400)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 400)
        for instance in instances:
            if instance.employee_designation.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class EmployeeController:
    feature_name = "Employee"
    serializer_class = EmployeeSerializer
    export_util = ExportUtility()

    def get_employee(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        search_by = get_query_param(request, 'search_by', None)
        export = get_query_param(request, 'export', None)
        category = get_query_param(request, 'category', None)
        login = get_query_param(request, 'allow_login', None)
        zone = get_query_param(request, 'zone', None)
        date_from = get_query_param(request, 'date_from', None)
        date_to = get_query_param(request, 'date_to', None)
        department = get_query_param(request, "department", None)
        sub_department = get_query_param(request, "sub_department", None)

        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if department:
            if type(department) == list:
                kwargs["department__in"] = department
            else:
                kwargs["department"] = department
        if sub_department:
            if type(sub_department) == list:
                kwargs["sub_department__in"] = sub_department
            else:
                kwargs["sub_department"] = sub_department
        if order and order_by:
            if order_by == "category":
                order_by = "department__category"
            if order_by == "department":
                order_by = "department__name"
            if order_by == "designation":
                order_by = "designation__name"

            if order == "desc":
                order_by = f"-{order_by}"
        if date_from and date_to:
            kwargs["date_of_joining__gte"] = date_from
            kwargs["date_of_joining__lte"] = date_to

        if category:
            kwargs["department__category"] = category
        if login or login == "False":
            kwargs["allow_login"] = login_params[login.lower()]
        if zone:
            kwargs["zone"] = zone
        if search:
            search_kwargs = seacrh_text_parser(search, search_kwargs)
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_employee_data(serialized_asset=serialized_data,
                                                         columns=EMPLOYEE_EXPORT_COLUMNS,
                                                         export_name="Employee Listing")
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_employee(self, request):
        try:
            allow_login = request.data.get("allow_login")
            role = request.data.get("role")
            if allow_login:
                if not role:
                    return create_response({}, ROLE_NOT_PROVIDED, 400)
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                with transaction.atomic():
                    response_data = serialized_data.save()
                    if response_data.allow_login:
                        user_data, password = user_json_helper(request.data, response_data)
                        serialized_user = UserListingSerializer(data=user_data)
                        if serialized_user.is_valid():
                            user = serialized_user.save()
                            # Prepare the email subject and message
                            try:
                                template = EmailTemplate.objects.get(notification_feature__name=self.feature_name)
                                user = User.objects.filter(email=request.data.get("email")).first()
                                variables = {
                                    "first_name": user.first_name,
                                    "last_name": user.last_name,
                                    "password": password
                                }
                                message = pass_variables_into_string(template.body, variables)
                                subject = template.subject

                            except:
                                subject = "Account Created Successfully"
                                message = f"""
                                    Password: {password}
                                    """

                            recipient_list = [request.data.get("email")]
                            # Send the email
                            t = threading.Thread(target=send_mail,
                                                 args=(subject, message, EMAIL_HOST_USER, recipient_list))
                            t.start()
                        else:
                            return create_response(
                                {},
                                get_first_error_message_from_serializer_errors(
                                    serialized_user.errors, UNSUCCESSFUL
                                ),
                                status_code=500,
                            )
                after_response = model_to_dict(response_data)
                after_response.pop("date_of_joining")
                after_response.pop("date_of_birth")
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)

                return create_response(
                    self.serializer_class(response_data).data,
                    SUCCESSFUL,
                    status_code=200,
                )
            else:
                return create_response({},
                                       get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                      UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({"data": str(e)}, UNSUCCESSFUL, 500)

    def update_employee(self, request):
        try:
            allow_login = request.data.get("allow_login")
            role = request.data.get("role")
            if allow_login:
                if not role:
                    return create_response({}, ROLE_NOT_PROVIDED, 400)
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    try:
                        if "first_name" in request.data or "last_name" in request.data or "email" in request.data:
                            instance = User.objects.filter(employee=request.data.get("id"), is_deleted=False,
                                                           is_active="ACTIVE")
                            if instance.first():
                                instance = instance.first()
                                serialized_data = UserListingSerializer(instance, request.data, partial=True)
                                if serialized_data.is_valid():
                                    serialized_data.save()
                                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                                operation=OperationType.UPDATED,
                                                                user=request.user, changes=updated_fields_with_values)
                    except Exception as e:
                        print(e)
                        pass
                    if "allow_login" in request.data:
                        if not response_data.allow_login:
                            try:
                                User.objects.filter(employee=request.data.get("id")).update(is_deleted=True,
                                                                                            is_active="INACTIVE",
                                                                                            deleted_at=timezone.now())
                            except:
                                pass
                        if response_data.allow_login:
                            user = User.objects.filter(employee=response_data.id, email=response_data.email)
                            if user.exists():
                                new_role = Role.objects.get(id=role)
                                user, password = update_exisiting_user(user, new_role)

                            else:
                                user_data, password = user_json_helper(request.data, response_data)
                                serialized_user = UserListingSerializer(data=user_data)
                                if serialized_user.is_valid():
                                    user = serialized_user.save()
                                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                                operation=OperationType.UPDATED,
                                                                user=request.user, changes=updated_fields_with_values)
                                else:
                                    return create_response(
                                        {},
                                        get_first_error_message_from_serializer_errors(
                                            serialized_user.errors, UNSUCCESSFUL
                                        ),
                                        status_code=500,
                                    )
                            # Prepare the email subject and message
                            try:
                                template = EmailTemplate.objects.get(notification_feature__name=self.feature_name)
                                user = User.objects.filter(email=request.data.get("email")).first()
                                variables = {
                                    "first_name": user.first_name,
                                    "last_name": user.last_name,
                                    "password": password
                                }
                                message = pass_variables_into_string(template.body, variables)
                                subject = template.subject

                            except:
                                subject = "Account Created Successfully"
                                message = f"""
                                    Password: {password}
                                    """

                            recipient_list = [request.data.get("email")]
                            # Send the email
                            t = threading.Thread(target=send_mail,
                                                 args=(subject, message, EMAIL_HOST_USER, recipient_list))
                            t.start()

                    return create_response(
                        self.serializer_class(response_data).data,
                        SUCCESSFUL,
                        status_code=200,
                    )
                else:
                    return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                              UNSUCCESSFUL),
                                           status_code=500)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_employee(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        User.objects.filter(employee__in=ids).update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class UserListingController:
    feature_name = "User"
    serializer_class = UserListingSerializer
    export_util = ExportUtility()

    def get_user(self, request):
        kwargs = {}
        search_kwargs = {}
        guid = get_query_param(request, "guid", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        profile = get_query_param(request, "self", None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if guid:
            kwargs["guid"] = guid
        if profile:
            kwargs["guid"] = request.user.guid
        if search:
            search_kwargs = seacrh_text_parser(search, search_kwargs)

        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        kwargs["is_locked"] = False
        data = self.serializer_class.Meta.model.objects.select_related("role").prefetch_related(
            "role__feature_association__permissions").filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)

            return self.export_util.export_user_data(serialized_asset=serialized_data,
                                                     columns=USER_EXPORT_COLUMNS,
                                                     export_name="User Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_user(self, request):
        try:
            dummy_password = generate_dummy_password()
            request.POST._mutable = True
            request.data["password"] = make_password(dummy_password)
            request.POST._mutable = True
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
            else:
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
            send_password(first_name=response_data.first_name, last_name=response_data.last_name,
                          email=request.data.get("email"),
                          password=dummy_password)
            return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
        except Exception as e:
            print(e)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_user(self, request):
        try:
            if "guid" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(guid=request.data.get("guid"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, USER_NOT_FOUND, 400)
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    # logs_controller.create_logs(feature=self.feature_name, object=response_data.guid,
                    #                             operation=OperationType.UPDATED,
                    #                             user=request.user, before=instance, after=response_data)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_user(self, request):
        if "guid" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("guid"))
        instances = self.serializer_class.Meta.model.objects.filter(guid__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, USER_NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class UserGroupController:
    feature_name = "UserGroup"
    serializer_class = UserGroupSerializer
    export_util = ExportUtility()

    def get_user_group(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if search:
            kwargs["name__icontains"] = search
        if order and order_by:
            if order_by == "department_head":
                order_by = "department_head__first_name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_user_group_data(serialized_asset=serialized_data,
                                                           columns=USER_GROUP_EXPORT_COLUMNS,
                                                           export_name="User Group Listing")
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_user_group(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                after_response["users"] = UserListingSerializer(after_response["users"], many=True).data
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_user_group(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)

                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_user_group(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class FeatureController:
    feature_name = "Feature"
    serializer_class = FeatureListingSreializer

    def get_feature(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)

        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_feature(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_feature(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_feature(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class RoleController:
    feature_name = "Role"
    serializer_class = RoleSerializer
    export_util = ExportUtility()

    def update_features(self, request):
        features_list = request.data.pop("features_list")
        instances = RoleFeatureAssociation.objects.filter(role=request.data.get("id"))
        if not instances:
            return create_response({}, NOT_FOUND, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        for features in features_list:
            features["role"] = request.data.get("id")
            serialized_data = RoleFeatureAssociationSerializer(data=features)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
        return create_response(self.serializer_class(
            self.serializer_class.Meta.model.objects.filter(id=request.data.get("id")).first()).data, SUCCESSFUL, 200)

    def get_role(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)
        export = get_query_param(request, "export", None)

        if is_active:
            kwargs["is_active"] = is_active

        if id:
            kwargs["id"] = id
        if search:
            kwargs["name__icontains"] = search
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_role_data(
                serialized_asset=serialized_data,
                columns=ROLE_EXPORT_COLUMNS,
                export_name="Role Listing",
            )

        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_role(self, request):
        try:
            role_name = request.data.get("name")
            features_list = request.data.get("features_list")
            with transaction.atomic():
                serialized_data = self.serializer_class(data=request.data)
                if serialized_data.is_valid():
                    role = serialized_data.save()
                else:
                    return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                              UNSUCCESSFUL), 500)
                for features in features_list:
                    features["role"] = role.id
                    serialized_data = RoleFeatureAssociationSerializer(data=features)
                    if serialized_data.is_valid():
                        serialized_data.save()
                    else:
                        return create_response({},
                                               get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                              UNSUCCESSFUL),
                                               status_code=500)

                return create_response(self.serializer_class(role).data, message=SUCCESSFUL, status_code=200)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({"data": e}, UNSUCCESSFUL, 500)

    def update_role(self, request):
        try:
            with transaction.atomic():
                if "id" not in request.data:
                    return create_response({}, ID_NOT_PROVIDED, 404)
                else:
                    if "name" in request.data:
                        instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                                   is_deleted=False)
                        before_instance = model_to_dict(instance)
                        if not instance:
                            return create_response({}, NOT_FOUND, 400)
                        instance = instance.first()
                        serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                        if serialized_data.is_valid():
                            role = serialized_data.save()
                            check_for_children(instance, data=role, request=request)
                            self.update_features(request)
                            return create_response(self.serializer_class(role).data, SUCCESSFUL, status_code=200)
                        return create_response({},
                                               get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                              UNSUCCESSFUL),
                                               status_code=500)
                    elif "features_list" in request.data:
                        self.update_features(request)
                        return create_response(self.serializer_class(
                            self.serializer_class.Meta.model.objects.filter(id=request.data.get("id")).first()).data,
                                               SUCCESSFUL, 200)

                return create_response({}, UNSUCCESSFUL, status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)

            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_role(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        with transaction.atomic():
            instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                        is_deleted=False)
            if not instances:
                return create_response({}, NOT_FOUND, 404)
            for instance in instances:
                if instance.user_role.filter(is_deleted=False).count() > 0:
                    return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
            instances.update(is_deleted=True, deleted_at=timezone.now())
            features = RoleFeatureAssociation.objects.filter(role__in=ids)
            features.update(is_deleted=True, deleted_at=timezone.now())
            logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                        operation=OperationType.DELETED,
                                        user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class PermissionController:
    feature_name = "Permission"
    serializer_class = PermissionSerializer

    def get_permission(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id

        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_permission(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_permission(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)

                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_permission(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in instances.id]),
                                    operation=OperationType.DELETED,
                                    user=request.user)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class ModuleController:
    feature_name = "Module"
    serializer_class = ModuleSerializer

    def get_module(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if search:
            kwargs["name__icontains"] = search
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        kwargs["status"] = 1
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_module(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            return create_response({},
                                   get_first_error_message_from_serializer_errors(serialized_data.errors, UNSUCCESSFUL),
                                   status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_module(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_module(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class LockedUsersController:
    feature_name = "Locked Users"
    serializer_class = UserListingSerializer

    def get_locked_users(self, request):
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "updated_at")

        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"

        data = self.serializer_class.Meta.model.objects.filter(is_deleted=False, is_locked=True,
                                                               is_active="INACTIVE").order_by(order_by)
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def update_locked_users(self, request):
        guid = request.data.get("guid", None)
        if not guid:
            return create_response({}, ID_NOT_PROVIDED, 400)
        else:
            try:
                instance = self.serializer_class.Meta.model.objects.get(guid=guid)
                before_instance = model_to_dict(instance)
                instance.is_active = "ACTIVE"
                instance.is_locked = False
                instance.failed_login_attempts = 0
                instance.last_failed_time = None
                response = instance.save()
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values())
                logs_controller.create_logs(feature=self.feature_name, object=instance.id,
                                            operation=OperationType.UPDATED,
                                            user=request.user, changes=updated_fields_with_values)
                return create_response(self.serializer_class(instance).data, SUCCESSFUL, 200)
            except Exception as e:
                print(e)
                return create_response({}, UNSUCCESSFUL, 200)


class GradeController:
    feature_name = "Grade"
    serializer_class = GradeSerializer
    export_util = ExportUtility()

    def get_grade(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)

        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["prefix__icontains"] = search
            search_kwargs["number__icontains"] = search
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            return self.export_util.export_grade_data(
                serialized_asset=serialized_data,
                columns=GRADE_EXPORT_COLUMNS,
                export_name="GRADE Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_grade(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)

                return create_response(
                    self.serializer_class(response_data).data,
                    SUCCESSFUL,
                    status_code=200,
                )
            return create_response(
                {},
                get_first_error_message_from_serializer_errors(
                    serialized_data.errors, UNSUCCESSFUL
                ),
                status_code=500,
            )
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def update_grade(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(
                    id=request.data.get("id"), is_deleted=False
                )

                if not instance:
                    return create_response({}, NOT_FOUND, 400)

                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(
                    instance, data=request.data, partial=True
                )
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)

                    return create_response(
                        self.serializer_class(response_data).data, SUCCESSFUL, 200
                    )
                return create_response(
                    {},
                    get_first_error_message_from_serializer_errors(
                        serialized_data.errors, UNSUCCESSFUL
                    ),
                    status_code=500,
                )
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_grade(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(
            id__in=ids, is_deleted=False
        )
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.grade.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class FeatureCountController:
    def get_count(self, request):
        try:
            mock_response = {value: key for key, value in model_names.items()}
            response_data = {key.__name__: key.objects.filter(is_deleted=False).count() for key, value in
                             mock_response.items()}
            return create_response(response_data, SUCCESSFUL, status_code=200)
        except Exception as e:
            print(e)


class WeekdayController:
    feature_name = "Weekday"
    serializer_class = WeekdaySerializer

    def get_days(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")

        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        count = data.count()
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)


class CurrencyController:
    feature_name = "Currency"
    serializer_class = CurrencySerializer

    def get_currency(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["name__icontains"] = search
        if is_active:
            kwargs["is_active"] = is_active
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by)
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)


class CompanyController:
    feature_name = "Company"
    serializer_class = CompanySerializer
    export_util = ExportUtility()

    def get_company(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["name__icontains"] = search
        if is_active:
            kwargs["is_active"] = is_active
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by)
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def update_company(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())

                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True,
                                                        context={'request': request})
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values
                                                )
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_company(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        # for instance in instances:
        #     if instance.designation.filter(is_deleted=False).count() > 0:
        #         return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class FinancialDataController:
    feature_name = "Fiscal year details"
    serializer_class = FinancialDataSerializer
    export_util = ExportUtility()

    def get_fiscal(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        is_active = get_query_param(request, "is_active", None)
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        if is_active:
            kwargs["is_active"] = is_active
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by)
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_fiscal(self, request):
        try:
            periods = request.data.pop("fiscal_period")
            request.POST._mutable = True
            request.data["company"] = 1
            request.POST._mutable = False
            serialized_data = self.serializer_class(data=request.data)

            if serialized_data.is_valid():
                with transaction.atomic():
                    response_data = serialized_data.save()
                    for order, period in enumerate(periods, start=1):
                        period["fiscal_year"] = response_data.id
                        period["order"] = order
                        serialized_period = FiscalPeriodSerializer(data=period)
                        if serialized_period.is_valid():
                            serialized_period.save()
                after_response = model_to_dict(response_data)
                logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                            operation=OperationType.CREATED,
                                            user=request.user)
                return create_response(self.serializer_class(response_data).data, SUCCESSFUL, status_code=200)
            else:
                return create_response({},
                                       get_first_error_message_from_serializer_errors(
                                           serialized_data.errors, UNSUCCESSFUL),
                                       status_code=500)

        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            print(e)
            return create_response({}, UNSUCCESSFUL, 500)

    def update_fiscal(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())

                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True,
                                                        context={'request': request})
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                    check_for_children(instance, data=response_data, request=request)
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values
                                                )
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_fiscal(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        # for instance in instances:
        #     if instance.designation.filter(is_deleted=False).count() > 0:
        #         return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)
