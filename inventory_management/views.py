from rest_framework import viewsets
from inventory_management.inventory_controller import *
from utils.base_authentication import JWTAuthentication
from inventory_management.serializers import *
from utils.base_permission import *

prod_controller = ProductController()
prod_type_controller = ProductTypeController()
warehouse_controller = WarehouseController()
plant_controller = PlantController()
launch_controller = LaunchProductController()


class ProductListingView(viewsets.ModelViewSet):
    """
    Endpoints for Product CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = ProductSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return prod_controller.get_product(request)

    def create(self, request):
        return prod_controller.create_product(request)

    def update(self, request):
        return prod_controller.update_product(request)

    def destroy(self, request):
        return prod_controller.delete_product(request)


class LaunchProductView(viewsets.ModelViewSet):
    """
    Endpoints for Product CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = ProductSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return launch_controller.get_launched_products(request)

    def update(self, request):
        return launch_controller.launch(request)


class ProductTypeListingView(viewsets.ModelViewSet):
    """
    Endpoints for Product Type CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = ProductTypeSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return prod_type_controller.get_product_type(request)

    def create(self, request):
        return prod_type_controller.create_product_type(request)

    def update(self, request):
        return prod_type_controller.update_product_type(request)

    def destroy(self, request):
        return prod_type_controller.delete_product_type(request)


class WarehouseListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = WarehouseSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return warehouse_controller.get_warehouse(request)

    def create(self, request):
        return warehouse_controller.create_warehouse(request)

    def update(self, request):
        return warehouse_controller.update_warehouse(request)

    def destroy(self, request):
        return warehouse_controller.delete_warehouse(request)


class PlantListingView(viewsets.ModelViewSet):
    """
    Endpoints for department CRUDs.
    """

    authentication_classes = (JWTAuthentication,)
    serializer_class = PlantSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return plant_controller.get_plant(request)

    def create(self, request):
        return plant_controller.create_plant(request)

    def update(self, request):
        return plant_controller.update_plant(request)

    def destroy(self, request):
        return plant_controller.delete_plant(request)
