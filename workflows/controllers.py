from copy import deepcopy

from utils.helper import *
from workflows.serializers import WrokflowSerializer, HierarchySerializer
from django.utils import timezone
from django.db import transaction


class WorkflowController:
    feature_name = "Workflow"
    serializer_class = WrokflowSerializer

    def get_workflow(self, request):
        kwargs = {}
        id = get_query_param(request, "id", None)
        order = get_query_param(request, 'order', 'desc')
        order_by = get_query_param(request, 'order_by', "created_at")
        is_active = get_query_param(request, "is_active", None)
        feature = get_query_param(request, "feature", None)
        user = get_query_param(request, "user", None)

        if feature:
            kwargs["feature__id"] = feature
        if user:
            kwargs["user__guid"] = user
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

    def create_workflow(self, request):
        try:
            hierarchies = request.data.pop("hierarchy")
            serialized_data = self.serializer_class(data=request.data)
            if serialized_data.is_valid():
                with transaction.atomic():
                    response_data = serialized_data.save()
                    for hierarchy in hierarchies:
                        hierarchy["workflow"] = response_data.id
                        serialized_hierarchy = HierarchySerializer(data=hierarchy)
                        if serialized_hierarchy.is_valid():
                            serialized_hierarchy.save()
                        else:
                            return create_response({},
                                                   get_first_error_message_from_serializer_errors(
                                                       serialized_data.errors,
                                                       UNSUCCESSFUL),
                                                   status_code=500)
                    after_response = model_to_dict(response_data)
                    after_response["user"] = str(after_response["user"])
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

    def update_workflow(self, request):
        try:
            if "id" not in request.data:
                return create_response({}, ID_NOT_PROVIDED, 404)
            else:
                instance = self.serializer_class.Meta.model.objects.filter(id=request.data.get("id"),
                                                                           is_deleted=False)
                instance = instance.first()
                if not instance:
                    return create_response({}, NOT_FOUND, 400)
                serialized_data = self.serializer_class(instance, data=request.data, partial=True)
                hierarchies = request.data.pop("hierarchy") if "hierarchy" in request.data else None
                if serialized_data.is_valid():
                    if hierarchies:
                        with transaction.atomic():
                            response_data = serialized_data.save()
                            related_hierarchies = response_data.hierarchy.all()
                            related_hierarchies.update(is_deleted=True, deleted_at=timezone.now())
                            for hierarchy in hierarchies:
                                hierarchy["workflow"] = response_data.id
                                serialized_hierarchy = HierarchySerializer(data=hierarchy)
                                if serialized_hierarchy.is_valid():
                                    serialized_hierarchy.save()
                                else:
                                    return create_response({},
                                                           get_first_error_message_from_serializer_errors(
                                                               serialized_data.errors,
                                                               UNSUCCESSFUL),
                                                           status_code=500)
                    response_data = serialized_data.save()
                    logs_controller.create_logs(feature=self.feature_name, object=response_data.id,
                                                operation=OperationType.UPDATED,
                                                user=request.user)
                    return create_response(self.serializer_class(response_data).data, SUCCESSFUL, 200)
                return create_response({}, get_first_error_message_from_serializer_errors(serialized_data.errors,
                                                                                          UNSUCCESSFUL),
                                       status_code=500)
        except Exception as e:
            if "duplicate" in str(e).lower():
                return create_response({}, self.feature_name + " " + ALREADY_EXISTS, 500)
            return create_response({}, UNSUCCESSFUL, status_code=500)

    def delete_workflow(self, request):
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
