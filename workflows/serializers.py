from rest_framework import serializers
from workflows.models import Workflow, Hierarchy


class WrokflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = "__all__"

    def to_representation(self, instance):
        data = super(WrokflowSerializer, self).to_representation(instance)
        data["hierarchy"] = HierarchySerializer(instance.hierarchy.filter(is_deleted=False), many=True).data
        return data


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = "__all__"
