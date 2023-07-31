from channel_management.models import *
from area_management.serializers import *
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from user_management.models import User


class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["guid", "first_name", "last_name", "role"]
        extra_kwargs = {'password': {'write_only': True}, "otp": {'write_only': True},
                        "otp_generated_at": {'write_only': True},
                        "failed_login_attempts": {'write_only': True}, "last_failed_time": {'write_only': True}}
        depth = 1


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"

    def validate(self, instance):
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if "name" in instance:
            if Channel.objects.filter(~Q(id__in=id), name__iexact=instance.get("name"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Channel with same name already exists"))
        if "code" in instance:
            if Channel.objects.filter(~Q(id__in=id), code__iexact=instance.get("code"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Channel with same code already exists"))
        return instance


class DistributorLisitngSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = ["id", "name", "regional_manager", "zonal_manager", "dsr", "user"]

    def to_representation(self, instance):
        data = super(DistributorLisitngSerializer, self).to_representation(instance)
        data["regional_manager"] = UserSerializer(instance.regional_manager, many=True).data
        data["zonal_manager"] = UserSerializer(instance.zonal_manager, many=True).data
        data["dsr"] = UserSerializer(instance.dsr, many=True).data
        data["user"] = UserSerializer(instance.user).data
        return data


class OutletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = "__all__"

    def to_representation(self, instance):
        data = super(OutletSerializer, self).to_representation(instance)
        data["channel"] = ChannelSerializer(instance.channel).data
        data["region"] = RegionSerializer(instance.region).data
        data["city"] = CitySerializer(instance.city).data
        data["zone"] = ZoneSerializer(instance.zone).data
        data["sub_zone"] = SubZoneSerializer(instance.sub_zone).data
        data["regional_manager"] = UserSerializer(instance.regional_manager, many=True).data
        data["zonal_manager"] = UserSerializer(instance.zonal_manager, many=True).data
        data["dsr"] = UserSerializer(instance.dsr, many=True).data
        data["distributor"] = DistributorSerializer(instance.distributor.all(), many=True).data
        data["user"] = UserSerializer(instance.user).data
        return data

    def validate(self, instance):
        sap_code = instance.get("sap_code", None)
        role = instance.get("role")
        allow_login = instance.get("allow_login")
        email = instance.get("email")
        longitude = instance.get("longitude")
        latitude = instance.get("latitude")

        if self.instance:
            id = [self.instance.id]
            if not sap_code:
                sap_code = self.instance.sap_code
        else:
            id = []
        if sap_code:
            if Outlet.objects.filter(~Q(id__in=id), sap_code__iexact=sap_code,
                                     is_deleted=False).exists():
                raise serializers.ValidationError(_("Outlet with same sap_code already exists"))

        if latitude:
            if not (23.5 <= float(latitude) <= 37):
                raise serializers.ValidationError("Latitude must be within the geographic boundaries of Pakistan.")

        if longitude:
            if not (60.5 <= float(longitude) <= 77):
                raise serializers.ValidationError("Longitude must be within the geographic boundaries of Pakistan.")

        return instance


class GisOutletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outlet
        fields = ["id", "name", "latitude", "longitude"]
