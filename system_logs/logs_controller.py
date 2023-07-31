from rest_framework.pagination import LimitOffsetPagination

from system_logs.models import AuditLogs
from system_logs.serializers import AuditLogSerializer
from utils.response_messages import *
from utils.reusable_methods import *


class AuditLogsController:
    serializer_class = AuditLogSerializer

    def delete_logs(self, request):
        kwargs = {}
        if "id" not in request.query_params:
            return create_response({}, ID_NOT_PROVIDED, 404)
        kwargs = get_params("id", request.query_params.get("id"), kwargs)
        data = self.serializer_class.Meta.model.objects.filter(**kwargs)
        if not data:
            return create_response({}, NOT_FOUND, status_code=400)
        data.delete()
        return create_response({}, SUCCESSFUL, status_code=200)

    def get_logs(self, request):
        kwargs = {}
        user = get_query_param(request, "user", None)
        feature = get_query_param(request, "feature", None)
        operation = get_query_param(request, "operation", None)
        date_from = get_query_param(request, "date_from", None)
        date_to = get_query_param(request, "date_to", None)
        limit = get_query_param(request, 'limit', None)
        offset = get_query_param(request, 'offset', None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        search = get_query_param(request, 'search', None)
        export = get_query_param(request, 'export', None)

        if order and order_by:
            if order_by == "department_head":
                order_by = "department_head__first_name"
            if order == "desc":
                order_by = f"-{order_by}"

        if user:
            kwargs["user"] = user
        if feature:
            kwargs["feature"] = feature
        if operation:
            kwargs["operation"] = operation
        if date_from and date_to:
            kwargs["created_at__gte"] = date_from
            kwargs["created_at__lte"] = date_to
        data = self.serializer_class.Meta.model.objects.select_related('user').filter(**kwargs).order_by(order_by)

        count = data.count()
        if limit and offset:
            pagination = LimitOffsetPagination()
            data = pagination.paginate_queryset(data, request)
        serialized_data = self.serializer_class(data, many=True).data
        response_data = {
            "count": count,
            "data": serialized_data
        }
        return create_response(response_data, SUCCESSFUL, status_code=200)

    def create_logs(self, feature=None, object=None, operation=None, user=None, changes=None):
        try:
            data = AuditLogs.objects.create(feature=feature, object=object, operation=operation, user=user,
                                            changes=changes)
            return data
        except Exception as e:
            print(e)

    @staticmethod
    def get_updated_fields(new_data, previous_instance):
        try:
            updated_fields = [
                {
                    "field": key,
                    "value": value,
                    "previous_value": previous_instance.get(key)
                }
                for key, value in new_data.items()
                if previous_instance.get(key) != value
            ]
        except Exception as e:
            print(e)
            return create_response({}, UNSUCCESSFUL, 400)
        return updated_fields
