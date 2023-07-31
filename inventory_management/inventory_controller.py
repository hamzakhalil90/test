from copy import deepcopy
from django.utils import timezone
from rest_framework.pagination import LimitOffsetPagination

from inventory_management.serializers import *
from utils.export_columns import *
from utils.export_utils import ExportUtility
from utils.helper import *
from django.forms.models import model_to_dict
from system_logs.logs_controller import AuditLogsController
from utils.enums import *

logs_controller = AuditLogsController()


class ProductController:
    feature_name = "Product"
    serializer_class = ProductSerializer
    export_util = ExportUtility()

    def get_product(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)
        manufacturer = get_query_param(request, "manufacturer", None)
        category = get_query_param(request, "category", None)
        is_active = get_query_param(request, "is_active", None)
        if not request.user.is_superuser:
            search_kwargs["country"] = request.user.employee.region.country
            search_kwargs["region"] = request.user.employee.region
            search_kwargs["city"] = request.user.employee.city
            search_kwargs["zone"] = request.user.employee.zone
            search_kwargs["subzone"] = request.user.employee.subzone

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        if manufacturer:
            kwargs = get_params("manufacturer", manufacturer, kwargs)
        if category:
            kwargs["category"] = category
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_product_data(
                serialized_asset=serialized_data,
                columns=PRODUCT_EXPORT_COLUMNS,
                export_name="Product Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_product(self, request):
        try:

            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_instance = deepcopy(response_data)
                after_instance = model_to_dict(after_instance)
                after_instance.pop("image")
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
            print(e)
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def update_product(self, request):
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
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_product(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instances.first().warehouse_products.filter(
                    is_deleted=False).count() > 0 or \
                    instances.first().plant_products.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class ProductTypeController:
    feature_name = "Product_Type"
    serializer_class = ProductTypeSerializer
    export_util = ExportUtility()

    def get_product_type(self, request):
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
            return self.export_util.export_product_type_data(
                serialized_asset=serialized_data,
                columns=PRODUCT_TYPE_EXPORT_COLUMNS,
                export_name="Product Type Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_product_type(self, request):
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
            print(e)
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def update_product_type(self, request):
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
            print(e)
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def delete_product_type(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        kwargs = {}
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.product.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 500)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class WarehouseController:
    feature_name = "Warehouse"
    serializer_class = WarehouseSerializer
    export_util = ExportUtility()

    def get_warehouse(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)
        region = get_query_param(request, "region", None)
        city = get_query_param(request, "city", None)
        zone = get_query_param(request, "zone", None)
        product = get_query_param(request, "product", None)
        category = get_query_param(request, "category", None)
        manufacturer = get_query_param(request, "manufacturer", None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            search_kwargs["name__icontains"] = search
            search_kwargs["code__icontains"] = search

        if region:
            kwargs = get_params("region", region, kwargs)

        if city:
            kwargs = get_params("city", city, kwargs)
        if zone:
            kwargs = get_params("zone", zone, kwargs)
        if product:
            kwargs = get_params("product", product, kwargs)
        if category:
            kwargs = get_params("category", category, kwargs)
        if manufacturer:
            kwargs = get_params("manufacturer", manufacturer, kwargs)

        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)

            return self.export_util.export_warehouse_data(
                serialized_asset=serialized_data,
                columns=WAREHOUSE_EXPORT_COLUMNS,
                export_name="Warehouse Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_warehouse(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                after_response["product"] = str(after_response["product"])
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
            print("error", e)
            if "duplicate" in str(e).lower():
                return create_response(
                    {}, self.feature_name + " " + ALREADY_EXISTS, 500
                )
            return create_response({}, UNSUCCESSFUL, 500)

    def update_warehouse(self, request):
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

    def delete_warehouse(self, request):
        kwargs = {}
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class PlantController:
    feature_name = "Plant"
    serializer_class = PlantSerializer
    export_util = ExportUtility()

    def get_plant(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)
        region = get_query_param(request, "region", None)
        city = get_query_param(request, "city", None)
        product = get_query_param(request, "product", None)
        type = get_query_param(request, "type", None)
        code = get_query_param(request, "code", None)
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

        if region:
            kwargs = get_params("region", region, kwargs)
        if code:
            kwargs = get_params("code", code, kwargs)
        if city:
            kwargs = get_params("city", city, kwargs)
        if product:
            kwargs = get_params("product", product, kwargs)
        if type:
            kwargs = get_params("type", type, kwargs)

        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_plant_data(
                serialized_asset=serialized_data,
                columns=PLANT_EXPORT_COLUMNS,
                export_name="Plant Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_plant(self, request):
        try:
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                response_data = serialized_data.save()
                after_response = model_to_dict(response_data)
                after_response["product"] = str(after_response["product"])
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

    def update_plant(self, request):
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

    def delete_plant(self, request):
        kwargs = {}
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class LaunchProductController:
    feature_name = "Product"
    serializer_class = LaunchProductSerializer
    export_util = ExportUtility()

    def get_launched_products(self, request):
        kwargs = {}
        search_kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, "order", "desc")
        order_by = get_query_param(request, "order_by", "created_at")
        search = get_query_param(request, "search", None)
        export = get_query_param(request, "export", None)
        manufacturer = get_query_param(request, "manufacturer", None)
        category = get_query_param(request, "category", None)
        is_active = get_query_param(request, "is_active", None)
        if not request.user.is_superuser:
            search_kwargs["country"] = request.user.employee.region.country
            search_kwargs["region"] = request.user.employee.region
            search_kwargs["city"] = request.user.employee.city
            search_kwargs["zone"] = request.user.employee.zone
            search_kwargs["subzone"] = request.user.employee.subzone

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if order and order_by:
            if order == "desc":
                order_by = f"-{order_by}"
        if search:
            kwargs["name__icontains"] = search
        if manufacturer:
            kwargs = get_params("manufacturer", manufacturer, kwargs)
        if category:
            kwargs["category"] = category
        kwargs["is_deleted"] = False
        kwargs["is_launched"] = True
        data = self.serializer_class.Meta.model.objects.filter(Q(**search_kwargs, _connector=Q.OR), **kwargs).order_by(
            order_by
        )
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_launched_product_data(
                serialized_asset=serialized_data,
                columns=LAUNCHED_PRODUCT_EXPORT_COLUMNS,
                export_name="Launched Product Listing",
            )
        count = data.count()
        data = paginate_data(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {"count": count, "data": serialized_data}
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def launch(self, request):
        try:
            if not "id" in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            ids = request.data.pop("id")
            instances = Product.objects.filter(id__in=ids, is_deleted=False)
            if not instances:
                return create_response({}, NOT_FOUND, 404)
            instances.update(**request.data
                             )
            return create_response({}, SUCCESSFUL, status_code=200)
        except Exception as e:
            print(e)
            return create_response({}, SOMETHING_WENT_WRONG, status_code=500)
