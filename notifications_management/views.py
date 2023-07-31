from rest_framework import viewsets
from notifications_management.notification_controller import *
from utils.base_authentication import JWTAuthentication
from notifications_management.serializers import *
from utils.base_permission import *


email_templete_controller = EmailTemplateController()
notification_feature_controller = NotificationFeaturesController()


class EmailTempleteListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = EmailTemplateSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return email_templete_controller.get_email_templete(request)

    def create(self, request):
        return email_templete_controller.create_email_templete(request)

    def update(self, request):
        return email_templete_controller.update_email_templete(request)

    def destroy(self, request):
        return email_templete_controller.delete_email_templete(request)
    
class NotificationFeaturesListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = NotificationFeaturesSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return notification_feature_controller.get_notification_features(request)

    def create(self, request):
        return notification_feature_controller.create_notification_features(request)

    def destroy(self, request):
        return notification_feature_controller.delete_notification_features(request)
