from rest_framework import viewsets
from market_intelligence.market_intelligence_controller import *
from utils.base_authentication import JWTAuthentication
from market_intelligence.serializers import *
from utils.base_permission import *

brand_controller = BrandController()
brand_type_controller = BrandTypeController()


class BrandListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = BrandSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return brand_controller.get_brand(request)

    def create(self, request):
        return brand_controller.create_brand(request)

    def update(self, request):
        return brand_controller.update_brand(request)

    def destroy(self, request):
        return brand_controller.delete_brand(request)


class BrandTypeListingView(viewsets.ModelViewSet):
    """
    Endpoints for Brand Type CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = BrandTypeSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return brand_type_controller.get_brand_type(request)

    def create(self, request):
        return brand_type_controller.create_brand_type(request)

    def update(self, request):
        return brand_type_controller.update_brand_type(request)

    def destroy(self, request):
        return brand_type_controller.delete_brand_type(request)

