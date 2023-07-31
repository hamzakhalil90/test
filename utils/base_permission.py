from rest_framework import permissions

from LCLPD_backend.settings import ENVIRONMENT
from user_management.serializers import PermissionRoleSerializer
from utils.custom_exceptions import *


class FeatureBasedPermission(permissions.BasePermission):
    methods = {
        "GET": 1,
        "POST": 2,
        "PATCH": 3,
        "DELETE": 4,
        "EXPORT": 5
    }

    def has_permission(self, request, view):

        if request.user.is_superuser or ENVIRONMENT == "DEV":
            return True
        # feature = request.query_params.get("feature")
        # if not feature:
        #     raise FeatureIdRequired()
        request_method = "EXPORT" if request.method == "GET" and request.query_params.get("export",
                                                                                          None) else request.method
        features = request.user.role.feature_association.filter(is_deleted=False)
        if not features:
            raise NotAuthorized()
        features_data = PermissionRoleSerializer(features,
                                                 many=True).data
        user_assigned_feature = list(filter(lambda x: x["feature"]["path"] == request.path, features_data))
        if len(user_assigned_feature) > 0:
            user_assigned_feature = user_assigned_feature[0]
            if self.methods[request_method] in user_assigned_feature["permissions"]:
                return True
        raise NotAuthorized()
