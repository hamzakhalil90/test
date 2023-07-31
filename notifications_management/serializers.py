from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from notifications_management.models import *

class NotificationFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationFeatures
        fields = "__all__"

    def validate(self, instance):
        name = instance.get("name")

        if self.instance:
            id = [self.instance.id]
            if not name:
                name = self.instance.name
        else:
            id = []
        if name:
            if EmailTemplate.objects.filter(
                    ~Q(id__in=id), name__iexact=name, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Notification Feature with same name already exists")
                )

        return instance

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = "__all__"

    def validate(self, instance):
        name = instance.get("name")

        if self.instance:
            id = [self.instance.id]
            if not name:
                name = self.instance.name
        else:
            id = []
        if name:
            if EmailTemplate.objects.filter(
                    ~Q(id__in=id), name__iexact=name, is_deleted=False
            ).exists():
                raise serializers.ValidationError(
                    _("Email Templete with same name already exists")
                )

        return instance
