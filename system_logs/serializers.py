from rest_framework import serializers
from system_logs.models import *
from utils.reusable_methods import parse_datetime


class AuditLogSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        try:
            data = instance.user.get_full_name()
        except:
            data = None
        return data

    class Meta:
        model = AuditLogs
        fields = "__all__"

    def to_representation(self, instance):
        data = super(AuditLogSerializer, self).to_representation(instance)
        date, time = parse_datetime(instance.created_at)
        data["changes"] = data["changes"] if data["changes"] else []
        data["time"] = str(time).split(".")[0]
        data["date"] = date
        return data
