from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from area_management.models import *


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code", "is_active"]

    def validate(self, instance):
        name = instance.get("name", None)
        code = instance.get("code", None)
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Country.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                print(Country.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False))
                raise serializers.ValidationError(_("Country with same name already exists"))
        if code:
            if Country.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Country with same code already exists"))
        return instance


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name", "code", "is_active", "country"]

    def to_representation(self, instance):
        data = super(RegionSerializer, self).to_representation(instance)
        data["country"] = CountrySerializer(instance.country).data
        return data

    def validate(self, instance):
        name = instance.get("name", None)
        code = instance.get("code", None)
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Region.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                print(Region.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False))
                raise serializers.ValidationError(_("Region with same name already exists"))
        if code:
            if Region.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Region with same code already exists"))
        return instance


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "code", "is_active", "region"]

    def to_representation(self, instance):
        data = super(CitySerializer, self).to_representation(instance)
        data["region"] = RegionSerializer(instance.region).data
        return data

    def validate(self, instance):
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if "name" in instance:
            if City.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                print(City.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False))
                raise serializers.ValidationError(_("City with same name already exists"))
        if "code" in instance:
            if City.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("City with same code already exists"))
        return instance


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ["id", "name", "code", "is_active", "city"]

    def to_representation(self, instance):
        data = super(ZoneSerializer, self).to_representation(instance)
        data["region"] = RegionSerializer(instance.city.region).data
        data["city"] = CitySerializer(instance.city).data
        return data

    def validate(self, instance):
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if "name" in instance:
            if Zone.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                print(Zone.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False))
                raise serializers.ValidationError(_("Zone with same name already exists"))
        if "code" in instance:
            if Zone.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Zone with same code already exists"))
        return instance


class SubZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubZone
        fields = ["id", "name", "code", "is_active", "zone"]

    def to_representation(self, instance):
        data = super(SubZoneSerializer, self).to_representation(instance)
        data["region"] = RegionSerializer(instance.zone.city.region).data
        data["city"] = CitySerializer(instance.zone.city).data
        data["zone"] = ZoneSerializer(instance.zone).data
        return data

    def validate(self, instance):
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if "name" in instance:
            if SubZone.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                print(SubZone.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False))
                raise serializers.ValidationError(_("Subzone with same name already exists"))
        if "code" in instance:
            if SubZone.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Subzone with same code already exists"))
        return instance
