from rest_framework import viewsets
from utils.base_authentication import JWTAuthentication
from channel_management.channel_controller import *
from channel_management.serializers import *
from utils.base_permission import *


channel_type_controller = ChannelTypeController()
outlet_controller = OutletController()
gis_controller = GisController()
assignment_controller = BulkAssignemntController()
distributor_listing = DistributorListingController()


# Create your views here.
class ChannelView(viewsets.ModelViewSet):
    """
    Endpoints for Channel CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = ChannelSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return channel_type_controller.get_channel(request)

    def create(self, request):
        return channel_type_controller.create_channel(request)

    def update(self, request):
        return channel_type_controller.update_channel(request)

    def destroy(self, request):
        return channel_type_controller.delete_channel(request)


class DistributorListingView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = DistributorLisitngSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return distributor_listing.get(request)


class GisOutletView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = GisOutletSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return gis_controller.get_gis_data(request)


class OutletView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = OutletSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return outlet_controller.get_outlet(request)

    def create(self, request):
        return outlet_controller.create_outlet(request)

    def update(self, request):
        return outlet_controller.update_outlet(request)

    def destroy(self, request):
        return outlet_controller.delete_outlet(request)


class BulkAssignmentView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (FeatureBasedPermission,)

    def update(self, request):
        return assignment_controller.update(request)
