from copy import deepcopy
import threading
from channel_management.models import Outlet
from channel_management.serializers import ChannelSerializer, OutletSerializer
from django.db import transaction
from django.utils import timezone
from rest_framework.pagination import LimitOffsetPagination
from utils.enums import *
from utils.export_columns import *
from utils.export_utils import ExportUtility
from utils.helper import *
from utils.reusable_methods import *
from django.forms.models import model_to_dict
from system_logs.logs_controller import AuditLogsController
from utils.enums import *
from bulk_update_management.bulk_update_helper import *
from utils.send_email import pass_variables_into_string


logs_controller = AuditLogsController()


class ChannelTypeController:
    """
    An endpoint for channel-type management.
    """

    feature_name = "Channel"
    serializer_class = ChannelSerializer
    export_util = ExportUtility()

    def get_channel(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)
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
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_channel_data(
                serialized_asset=serialized_data,
                columns=CHANNEL_EXPORT_COLUMNS,
                export_name="Channel Listing",
            )
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_channel(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                after_response.pop("marker")
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

    def update_channel(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, NOT_FOUND, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(
                    id=request.data.get("id"), is_deleted=False
                )
                updated_fields_with_values = logs_controller.get_updated_fields(request.data, instance.values().first())
                instance = instance.first()
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
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
            print(e)
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_channel(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.outlet.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class OutletController:
    """
    An endpoint for Outlet management.
    """

    serializer_class = OutletSerializer
    feature_name = "Outlet"
    export_util = ExportUtility()

    def get_outlet(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        category = get_query_param(request, "category", None)
        channel = get_query_param(request, "channel", None)
        region = get_query_param(request, "region", None)
        city = get_query_param(request, "city", None)
        zone = get_query_param(request, "zone", None)
        subzone = get_query_param(request, "subzone", None)
        export = get_query_param(request, "export", None)
        login = get_query_param(request, "login", None)
        is_active = get_query_param(request, "is_active", None)
        is_distributor = get_query_param(request, "is_distributor", None)
        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if region:
            kwargs["region"] = region
        if city:
            kwargs["city"] = city
        if zone:
            kwargs["zone"] = zone
        if subzone:
            kwargs["subzone"] = subzone
        if is_distributor or request.path == "/channel/distributor":
            kwargs["is_distributor"] = True
        else:
            kwargs["is_distributor"] = False
        if login:
            kwargs["allow_login"] = login_params[login.lower()]
        if order and order_by:
            if order_by == "region":
                order_by = "region__name"
            if order_by == "city":
                order_by = "city__name"
            if order_by == "zone":
                order_by = "zone__name"
            if order_by == "subzone":
                order_by = "subzone__name"
            if order_by == "channel":
                order_by = "channel__name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        if category:
            kwargs["category"] = category
        if channel:
            kwargs["channel"] = channel

        if search:
            search_kwargs["name__icontains"] = search
            search_kwargs["email__icontains"] = search
            search_kwargs["ntn__icontains"] = search

        data = self.serializer_class.Meta.model.objects.filter(
            Q(**search_kwargs, _connector=Q.OR), **kwargs
        ).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_outlet_data(
                serialized_asset=serialized_data,
                columns=OUTLET_EXPORT_COLUMNS,
                export_name="Outlets Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_outlet(self, request):
        try:
            if request.path == "/channel/distributor":
                request.POST._mutable = True
                try:
                    request.data["channel"] = Channel.objects.get(name__iexact="distributor").id
                except Exception as e:
                    print(e)
                request.data["is_distributor"] = True
                request.POST._mutable = False
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
                            response_data.user = user
                            response_data.save()
                            # Prepare the email subject and message
                            try:
                                template = EmailTemplate.objects.get(notification_feature__name = self.feature_name)
                                user = User.objects.filter(email=request.data.get("email")).first()
                                variables = {
                                    "first_name" : user.first_name,
                                    "last_name" : user.last_name,
                                    "password" : password
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
                            t = threading.Thread(target=send_mail, args=(subject, message, EMAIL_HOST_USER, recipient_list))
                            t.start()
                        else:
                            return create_response(
                                {},
                                get_first_error_message_from_serializer_errors(
                                    serialized_user.errors, UNSUCCESSFUL
                                ),
                                status_code=500,
                            )

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

    def update_outlet(self, request):
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

                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user, changes=updated_fields_with_values)
                    try:
                        if "first_name" in request.data or "last_name" in request.data or "email" in request.data:
                            user_instance = instance.user
                            if user_instance:
                                serialized_data = UserListingSerializer(user_instance, request.data, partial=True)
                                if serialized_data.is_valid():
                                    serialized_data.save()
                                else:
                                    return create_response({}, get_first_error_message_from_serializer_errors(
                                        serialized_data.errors, UNSUCCESSFUL), status_code=400)

                    except Exception as e:
                        print(e)
                        pass
                    if not response_data.allow_login and "allow_login" in request.data:
                        try:
                            user = instance.user
                            user.is_deleted = True
                            user.is_active = "INACTIVE"
                            user.deleted_at = timezone.now()
                            user.save()
                        except Exception as e:
                            pass
                    if response_data.allow_login and "allow_login" in request.data:
                        user = instance.user
                        if user:
                            new_role = Role.objects.get(id=role)
                            user, password = update_exisiting_user(user, new_role)

                        else:
                            if not "email" in request.data and response_data.email is None:
                                return create_response({}, "Email not Provided", status_code=400)
                            if not "role" in request.data and response_data.role is None:
                                return create_response({}, "Role not Provided", status_code=400)
                            user_data, password = user_json_helper(request.data, response_data)
                            serialized_user = UserListingSerializer(data=user_data)
                            if serialized_user.is_valid():
                                user = serialized_user.save()
                                instance.user = user
                                instance.save()
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
                                template = EmailTemplate.objects.get(notification_feature__name = self.feature_name)
                                user = User.objects.filter(email=request.data.get("email")).first()
                                variables = {
                                    "first_name" : user.first_name,
                                    "last_name" : user.last_name,
                                    "password" : password
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
                            t = threading.Thread(target=send_mail, args=(subject, message, EMAIL_HOST_USER, recipient_list))
                            t.start()
                    return create_response(
                        self.serializer_class(response_data).data,
                        SUCCESSFUL,
                        status_code=200,
                    )
                else:
                    return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                              UNSUCCESSFUL),
                                           status_code=400)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_outlet(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        User.objects.filter(employee__in=ast.literal_eval(request.query_params.get("id"))).update(
            is_deleted=True, deleted_at=timezone.now()
        )
        return create_response({}, SUCCESSFUL, 200)


class BulkAssignemntController:
    def update(self, request):
        try:
            if not "id" in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            ids = request.data.pop("id")
            instances = Outlet.objects.filter(id__in=ids, is_deleted=False)
            if not instances:
                return create_response({}, NOT_FOUND, 404)
            for instance in instances:
                instance.regional_manager.set(request.data.get("regional_manager"))
                instance.zonal_manager.set(request.data.get("zonal_manager"))
                instance.dsr.set(request.data.get("dsr"))
                instance.distributor.set(request.data.get("distributor"))
            return create_response({}, SUCCESSFUL, status_code=200)
        except Exception as e:
            print(e)
            return create_response({}, SOMETHING_WENT_WRONG, status_code=400)


class DistributorListingController:
    serializer_class = DistributorLisitngSerializer

    def get(self, request):
        data = self.serializer_class.Meta.model.objects.filter(is_distributor=True, is_deleted=False,
                                                               is_active="ACTIVE").order_by("-created_at")
        count = data.count()
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)


class GisController:
    serializer_class = GisOutletSerializer

    def get_gis_data(self, request):
        data = self.serializer_class.Meta.model.objects.filter(is_deleted=False, is_active="ACTIVE")
        count = data.count()
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, 200)
