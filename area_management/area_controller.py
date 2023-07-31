from copy import deepcopy
from utils.reusable_methods import *
from utils.response_messages import *
from rest_framework.pagination import LimitOffsetPagination
from area_management.serializers import *
from django.utils import timezone
import ast
import json
from utils.export_utils import ExportUtility
from utils.export_columns import *
from utils.helper import *
from django.forms.models import model_to_dict
from system_logs.logs_controller import AuditLogsController
from utils.enums import *

logs_controller = AuditLogsController()


# Create your views here.
class CountryController:
    """
    An endpoint for region management.
    """
    feature_name = "Country"
    serializer_class = CountrySerializer
    export_util = ExportUtility()

    def get_country(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'asc')
        order_by = get_query_param(request, 'order_by', "name")
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
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_country_data(serialized_asset=serialized_data,
                                                        columns=COUNTRY_EXPORT_COLUMNS,
                                                        export_name="Country Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_country(self, request):
        try:
            for data in request.data["data"]:
                serialized_data = self.serializer_class(data=data)
                if serialized_data.is_valid():
                    response_data = serialized_data.save()
                else:
                    return create_response({},
                                           get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                           status_code=400)

            return create_response({}, SUCCESSFUL, status_code=200)

        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, 400)

    def update_country(self, request):
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
                    check_for_children(instance, data=response_data, request=request)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, 400)

    def delete_country(self, request):
        kwargs = {}
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)

        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.region.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class RegionController:
    """
    An endpoint for region management.
    """
    feature_name = "Region"
    serializer_class = RegionSerializer
    export_util = ExportUtility()

    def get_region(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        country = get_query_param(request, 'country', None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if country:
            kwargs = get_params("country", country, kwargs)
        if search:
            kwargs["name__icontains"] = search
        if order and order_by:
            if order_by == "country":
                order_by = "country__name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.select_related("country").filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_region_data(serialized_asset=serialized_data,
                                                       columns=REGION_EXPORT_COLUMNS,
                                                       export_name="Region Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_region(self, request):
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
                                   status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, 400)

    def update_region(self, request):
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
                                       status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, 400)

    def delete_region(self, request):
        kwargs = {}
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)

        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        kwargs["is_deleted"] = False
        instances = self.serializer_class.Meta.model.objects.filter(**kwargs)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.city.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=request.query_params.get("id"),
                                    operation=OperationType.DELETED,
                                    user=request.user)

        return create_response({}, SUCCESSFUL, 200)


class CityController:
    """
    An endpoint for city management.
    """
    feature_name = "City"
    export_util = ExportUtility()
    serializer_class = CitySerializer

    def get_city(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        region = get_query_param(request, "region", None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if region:
            kwargs = get_params("region", region, kwargs)

        if search:
            kwargs["name__icontains"] = search
        if order and order_by:
            if order_by == "country":
                order_by = "region__country__name"
            if order_by == "region":
                order_by = "region__name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.select_related("region").filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_city_data(serialized_asset=serialized_data,
                                                     columns=CITY_EXPORT_COLUMNS,
                                                     export_name="City Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_city(self, request):
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
                                   status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def update_city(self, request):
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
                                       status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def delete_city(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.zone.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class ZoneController:
    """
    An endpoint for zone management.
    """
    feature_name = "Zone"
    export_util = ExportUtility()
    serializer_class = ZoneSerializer

    def get_zone(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        city = get_query_param(request, "city", None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if search:
            kwargs["name__icontains"] = search
        if city:
            kwargs = get_params("city", city, kwargs)
            # if type(city) == list:
            #     city = ast.literal_eval(city)
            #     kwargs["city__in"] = city
            # else:
            #     kwargs["city"] = city
        if order and order_by:
            if order_by == "country":
                order_by = "city__region__country__name"
            if order_by == "region":
                order_by = "city__region__name"
            if order_by == "city":
                order_by = "city__name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.select_related("city").filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_zone_data(serialized_asset=serialized_data,
                                                     columns=ZONE_EXPORT_COLUMNS,
                                                     export_name="Zone Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_zone(self, request):
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
                                   status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def update_zone(self, request):
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
                    check_for_children(instance, data=response_data, request=request)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def delete_zone(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.subzone.filter(is_deleted=False).count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class SubZoneController:
    """
    An endpoint for subzone management.
    """
    feature_name = "Sub Zone"
    export_util = ExportUtility()
    serializer_class = SubZoneSerializer

    def get_sub_zone(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)
        region = get_query_param(request, 'region', None)
        city = get_query_param(request, 'city', None)
        zone = get_query_param(request, 'zone', None)
        is_active = get_query_param(request, "is_active", None)

        if is_active:
            kwargs["is_active"] = is_active
        if id:
            kwargs["id"] = id
        if search:
            kwargs["name__icontains"] = search
        if zone:
            kwargs = get_params("zone", zone, kwargs)
        if region:
            kwargs = get_params("zone__city__region", region, kwargs)
        if city:
            kwargs = get_params("zone__city", city, kwargs)
        if order and order_by:
            if order_by == "country":
                order_by = "zone__city__region__country__name"
            if order_by == "region":
                order_by = "zone__city__region__name"
            if order_by == "city":
                order_by = "zone__city__name"
            if order_by == "zone":
                order_by = "zone__name"
            if order == "desc":
                order_by = f"-{order_by}"
        kwargs["is_deleted"] = False
        data = self.serializer_class.Meta.model.objects.select_related("zone").filter(**kwargs).order_by(order_by)
        if export:
            serialized_data = self.serializer_class(data, many=True)
            logs_controller.create_logs(feature=self.feature_name,
                                        operation=OperationType.EXPORT,
                                        user=request.user)
            return self.export_util.export_subzone_data(serialized_asset=serialized_data,
                                                        columns=SUBZONE_EXPORT_COLUMNS,
                                                        export_name="Subzone Listing")
        count = data.count()
        data = paginate_data(data, request)

        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_sub_zone(self, request):
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
                                   status_code=400)
        except Exception as e:
            print(e)
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def update_sub_zone(self, request):
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
                                       status_code=400)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 400)
            return create_response({}, UNSUCCESSFUL, status_code=400)

    def delete_sub_zone(self, request):
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        ids = ast.literal_eval(request.query_params.get("id"))
        instances = self.serializer_class.Meta.model.objects.filter(id__in=ids,
                                                                    is_deleted=False)
        if not instances:
            return create_response({}, NOT_FOUND, 404)
        for instance in instances:
            if instance.employee.count() > 0:
                return create_response({}, OBJECTS_ASSOCIATED_CANNOT_BE_DELETED, 400)
        instances.update(is_deleted=True, deleted_at=timezone.now())
        logs_controller.create_logs(feature=self.feature_name, object=str([id for id in ids]),
                                    operation=OperationType.DELETED,
                                    user=request.user)
        return create_response({}, SUCCESSFUL, 200)


class TemporaryCountryController:
    def get_all_countries(self, requerst):
        try:
            with open('area_management/migrations/countries.json', 'r') as f:
                countries_data = json.load(f)
                return create_response({"data": countries_data}, SUCCESSFUL, 200)
        except Exception as e:
            print(e)
            return create_response({}, UNSUCCESSFUL, 400)
