from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from inventory_management.models import *
from market_intelligence.serializers import *
from django.db.models import Q
from area_management.serializers import *
from user_management.serializers import EmployeeSerializer
from channel_management.serializers import ChannelSerializer


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = "__all__"

    def validate(self, instance):
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if "name" in instance:
            if ProductType.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Product Type with same name already exists"))
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        data = super(ProductSerializer, self).to_representation(instance)
        data["manufacturer"] = BrandSerializer(instance.manufacturer).data
        data["product_type"] = ProductTypeSerializer(instance.product_type).data
        data["country"] = CountrySerializer(instance.country).data
        data["region"] = RegionSerializer(instance.region).data
        data["zone"] = ZoneSerializer(instance.zone).data
        data["city"] = CitySerializer(instance.city).data
        data["subzone"] = SubZoneSerializer(instance.subzone).data
        data["channel"] = ChannelSerializer(instance.channel).data
        return data

    def validate(self, instance):
        name = instance.get("name", None)
        brand = instance.get("manufacturer", None)
        code = instance.get("code", None)
        category = instance.get("category", None)

        if self.instance:
            id = [self.instance.id]
            brand = self.instance.manufacturer
            category = self.instance.category
        else:
            id = []

        if code:
            if Product.objects.filter(
                    ~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Product with same code already exists")
                )

        if name:
            if Product.objects.filter(~Q(id__in=id), manufacturer=brand, name__iexact=instance.get("name"),
                                      is_deleted=False).exists():
                raise serializers.ValidationError(
                    _("Same Product already exists in this Brand")
                )

        return instance


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"

    def to_representation(self, instance):
        data = super(WarehouseSerializer, self).to_representation(instance)
        data["product"] = ProductSerializer(instance.product.all(), many=True).data
        data["region"] = RegionSerializer(instance.region).data
        data["city"] = CitySerializer(instance.city).data
        data["zone"] = ZoneSerializer(instance.zone).data
        data["person_in_control"] = EmployeeSerializer(instance.person_in_control).data
        return data

    def validate(self, instance):
        category = instance.get("category")
        name = instance.get("name")
        code = instance.get("code")
        longitude = instance.get("longitude")
        latitude = instance.get("latitude")

        if self.instance:
            id = [self.instance.id]
            if not category:
                category = self.instance.category
            if not code:
                code = self.instance.code
            if not name:
                name = self.instance.name
        else:
            id = []
        if name:
            if Warehouse.objects.filter(
                    ~Q(id__in=id),
                    category=category,
                    name__iexact=name,
                    is_deleted=False,
            ).exists():
                raise serializers.ValidationError(
                    _("Same Warehouse already exists in this Category")
                )
        if code:
            if Warehouse.objects.filter(
                    ~Q(id__in=id), code__iexact=code, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Warehouse with same code already exists")
                )
        if latitude:
            if not (23.5 <= float(latitude) <= 37):
                raise serializers.ValidationError("Latitude must be within the geographic boundaries of Pakistan.")

        if longitude:
            if not (60.5 <= float(longitude) <= 77):
                raise serializers.ValidationError("Longitude must be within the geographic boundaries of Pakistan.")
        return instance


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = "__all__"

    def to_representation(self, instance):
        data = super(PlantSerializer, self).to_representation(instance)
        data["product"] = ProductSerializer(instance.product.all(), many=True).data
        data["region"] = RegionSerializer(instance.region).data
        data["city"] = CitySerializer(instance.city).data
        data["person_in_control"] = EmployeeSerializer(instance.person_in_control).data
        return data

    def validate(self, instance):
        category = instance.get("category")
        name = instance.get("name")
        code = instance.get("code")
        sap_id = instance.get("sap_id")
        longitude = instance.get("longitude")
        latitude = instance.get("latitude")

        if self.instance:
            id = [self.instance.id]
            if not code:
                code = self.instance.code
            if not name:
                name = self.instance.name
        else:
            id = []
        if sap_id:
            if Plant.objects.filter(
                    ~Q(id__in=id), sap_id__iexact=sap_id, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Plant with same sap_id already exists")
                )
        if name:
            if Plant.objects.filter(
                    ~Q(id__in=id),
                    name__iexact=name,
                    is_deleted=False,
            ).exists():
                raise serializers.ValidationError(
                    _("Same Plant already exists in this Category")
                )
        if code:
            if Plant.objects.filter(
                    ~Q(id__in=id), code__iexact=code, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Plant with same code already exists")
                )
        if latitude:
            if not (23.5 <= float(latitude) <= 37):
                raise serializers.ValidationError("Latitude must be within the geographic boundaries of Pakistan.")

        if longitude:
            if not (60.5 <= float(longitude) <= 77):
                raise serializers.ValidationError("Longitude must be within the geographic boundaries of Pakistan.")

        return instance


class LaunchProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        data = super(LaunchProductSerializer, self).to_representation(instance)
        data["manufacturer"] = BrandSerializer(instance.manufacturer).data
        data["product_type"] = ProductTypeSerializer(instance.product_type).data
        data["country"] = CountrySerializer(instance.country).data if instance.country else []
        data["region"] = RegionSerializer(instance.region).data if instance.region else []
        data["zone"] = ZoneSerializer(instance.zone).data if instance.zone else []
        data["city"] = CitySerializer(instance.city).data if instance.city else []
        data["subzone"] = SubZoneSerializer(instance.subzone).data if instance.subzone else []
        data["channel"] = ChannelSerializer(instance.channel).data if instance.channel else []
        return data