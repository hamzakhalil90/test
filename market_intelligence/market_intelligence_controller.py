from copy import deepcopy
from django.utils import timezone
from utils.response_messages import *
from utils.helper import *
from utils.base_authentication import *
from market_intelligence.serializers import *
from django.contrib.auth import authenticate
from rest_framework.pagination import LimitOffsetPagination
from utils.export_utils import ExportUtility
from utils.export_columns import *
import ast
import threading
from utils.helper import create_user
from django.forms.models import model_to_dict
from system_logs.logs_controller import AuditLogsController
from utils.enums import *

logs_controller = AuditLogsController()


class BrandController:
    feature_name = "Brand"
    serializer_class = BrandSerializer
    export_util = ExportUtility()

    def get_brand(self, request):
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
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                            operation=OperationType.EXPORT,
                                            user=request.user)

            return self.export_util.export_brand_data(
                serialized_asset=serialized_data,
                columns=BRAND_EXPORT_COLUMNS,
                export_name="Brand Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_brand(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
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

    def update_brand(self, request):
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

    def delete_brand(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.product_manufacturer.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class BrandTypeController:
    feature_name = "Brand Type"
    serializer_class = BrandTypeSerializer
    export_util = ExportUtility()

    def get_brand_type(self, request):
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
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_brand_type_data(
                serialized_asset=serialized_data,
                columns=BRAND_TYPE_EXPORT_COLUMNS,
                export_name="Brand Type Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_brand_type(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                after_response["region"] = RegionSerializer(after_response.get("region"), many=True).data
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

    def update_brand_type(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(
                    id=request.data.get("id"), is_deleted=False
                )
                before_instance = deepcopy(instance)
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
                                                user=request.user, changes=updated_fields_with_values
)
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

    def delete_brand_type(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.brand.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)
