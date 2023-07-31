from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from area_management.serializers import RegionSerializer
from market_intelligence.models import *


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

    def to_representation(self, instance):
        data = super(BrandSerializer, self).to_representation(instance)
        data["brand_type"] = BrandTypeSerializer(instance.brand_type).data
        return data

    def validate(self, instance):
        name = instance.get("name")
        code = instance.get("code")

        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Brand.objects.filter(
                    ~Q(id__in=id),
                    name__iexact=name,
                    is_deleted=False,
            ).exists():
                raise serializers.ValidationError(
                    _("Brand with same name already exists")
                )
        if code:
            if Brand.objects.filter(
                    ~Q(id__in=id), code__iexact=code, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Brand with same code already exists")
                )
        return instance


class BrandTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandType
        fields = "__all__"

    def to_representation(self, instance):
        data = super(BrandTypeSerializer, self).to_representation(instance)
        data["region"] = RegionSerializer(instance.region.all(), many=True).data if instance.region.all() else []
        return data

    def validate(self, instance):
        name = instance.get("name")

        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if BrandType.objects.filter(~Q(id__in=id),
                                        name__iexact=name,
                                        is_deleted=False,
                                        ).exists():
                raise serializers.ValidationError(
                    _("Brand Type with same name already exists")
                )
        return instance
