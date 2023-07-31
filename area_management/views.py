from rest_framework import viewsets

from area_management.area_controller import *
from area_management.serializers import *
from utils.base_authentication import JWTAuthentication
from utils.base_permission import *

region_controller = RegionController()
city_controller = CityController()
zone_controller = ZoneController()
sub_zone_controller = SubZoneController()
country_controller = CountryController()
temporary_country_controller = TemporaryCountryController()


class TemporaryCountryView(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        return temporary_country_controller.get_all_countries(request)


class CountryView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = CountrySerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return country_controller.get_country(request)

    def create(self, request):
        return country_controller.create_country(request)

    def update(self, request):
        return country_controller.update_country(request)

    def destroy(self, request):
        return country_controller.delete_country(request)


class RegionView(viewsets.ModelViewSet):
    """
    Endpoints for Region CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = RegionSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return region_controller.get_region(request)

    def create(self, request):
        return region_controller.create_region(request)

    def update(self, request):
        return region_controller.update_region(request)

    def destroy(self, request):
        return region_controller.delete_region(request)


class CityView(viewsets.ModelViewSet):
    """
    Endpoints for City CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = CitySerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return city_controller.get_city(request)

    def create(self, request):
        return city_controller.create_city(request)

    def update(self, request):
        return city_controller.update_city(request)

    def destroy(self, request):
        return city_controller.delete_city(request)


class ZoneView(viewsets.ModelViewSet):
    """
    Endpoints for Zone CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = ZoneSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return zone_controller.get_zone(request)

    def create(self, request):
        return zone_controller.create_zone(request)

    def update(self, request):
        return zone_controller.update_zone(request)

    def destroy(self, request):
        return zone_controller.delete_zone(request)


class SubZoneView(viewsets.ModelViewSet):
    """
    Endpoints for Subzone CRUDs.
    """
    authentication_classes = (JWTAuthentication,)
    serializer_class = SubZoneSerializer
    permission_classes = (FeatureBasedPermission,)

    def get(self, request):
        return sub_zone_controller.get_sub_zone(request)

    def create(self, request):
        return sub_zone_controller.create_sub_zone(request)

    def update(self, request):
        return sub_zone_controller.update_sub_zone(request)

    def destroy(self, request):
        return sub_zone_controller.delete_sub_zone(request)
