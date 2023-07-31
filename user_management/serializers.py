from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from user_management.models import *
from channel_management.serializers import *
from django.contrib.auth.hashers import check_password
from utils.custom_exceptions import *
from django.db.models import Q
from rest_framework import serializers
from user_management.models import FinancialDetails


class EmployeeHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "first_name", "last_name")


class LoginSerializer(serializers.Serializer):
    """User login serializer
    """
    email = serializers.EmailField(
        label=_("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, instance):
        if len(instance["password"]) < 8:
            raise serializers.ValidationError(_("Password must be at least 8 characters long."))
        if User.objects.filter(email=instance["email"], is_active="INACTIVE", is_locked=True).exists():
            raise serializers.ValidationError(_("Your account has been deactivated."))

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        label=_("old_password"),
        style={"input_type": "old_password"},
        trim_whitespace=False,
        write_only=True
    )

    new_password = serializers.CharField(
        label=_("new_password"),
        style={"input_type": "new_password"},
        trim_whitespace=False,
        write_only=True
    )

    confirm_password = serializers.CharField(
        label=_("confirm_password"),
        style={"input_type": "confirm_password"},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, instance):
        user = self.context.get("user")
        if len(instance["new_password"]) < 8:
            raise PasswordMustBeEightChar()
        if instance["new_password"] == instance["old_password"]:
            raise SameOldPassword()
        passwords = UserPasswordHistory.objects.filter(user=user.guid).order_by(
            "-created_at")
        if passwords:
            passwords = passwords[:6] if len(passwords) >= 6 else passwords
            for p in passwords:
                if check_password(instance["new_password"], p.password):
                    raise PasswordAlreadyUsed()
        return instance


class VerifyOtpSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    otp = serializers.CharField(
        label=_("otp"),
        style={"input_type": "otp"},
        trim_whitespace=False,
        write_only=True
    )

    new_password = serializers.CharField(
        label=_("new_password"),
        style={"input_type": "new_password"},
        trim_whitespace=False,
        write_only=True
    )

    confirm_password = serializers.CharField(
        label=_("confirm_password"),
        style={"input_type": "confirm_password"},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, instance):
        user = self.context.get("user")
        if len(instance["new_password"]) < 8:
            raise PasswordMustBeEightChar()
        passwords = UserPasswordHistory.objects.filter(user=user.guid).order_by(
            "-created_at")
        if passwords:
            passwords = passwords[:6] if len(passwords) >= 6 else passwords
            for p in passwords:
                if check_password(instance["new_password"], p.password):
                    raise serializers.ValidationError(_("This password has already been used in the last 6 passwords."))
        return instance


class ForgetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    email = serializers.EmailField(
        label=_("email"),
        write_only=True
    )


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

    def to_representation(self, instance):
        data = super(DepartmentSerializer, self).to_representation(instance)
        data["department_head"] = EmployeeHeadSerializer(
            instance.department_head).data if instance.department_head else {}
        return data

    def validate(self, instance):
        name = instance.get("name")
        category = instance.get("category")
        if self.instance:
            id = [self.instance.id]
            if not category:
                category = self.instance.category
        else:
            id = []
        if name:
            if Department.objects.filter(~Q(id__in=id), name__iexact=name,
                                         is_deleted=False, category=category).exists():
                raise serializers.ValidationError(_("Department with same name already exists"))
        return instance


class SubDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDepartment
        fields = "__all__"

    def to_representation(self, instance):
        data = super(SubDepartmentSerializer, self).to_representation(instance)
        data["head"] = EmployeeHeadSerializer(
            instance.head).data if instance.head else {}
        data["department"] = DepartmentSerializer(instance.department).data if instance.department else []
        return data

    def validate(self, instance):
        name = instance.get("name")
        category = instance.get("category")
        if self.instance:
            id = [self.instance.id]
            if not category:
                category = self.instance.category
        else:
            id = []
        if name:
            if SubDepartment.objects.filter(~Q(id__in=id), name__iexact=name,
                                            is_deleted=False, category=category).exists():
                raise serializers.ValidationError(_("Sub-Department with same name already exists"))
        return instance


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = "__all__"

    def to_representation(self, instance):
        data = super(DesignationSerializer, self).to_representation(instance)
        data["department"] = DepartmentSerializer(instance.department).data
        return data

    def validate(self, instance):
        name = instance.get("name")
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Designation.objects.filter(~Q(id__in=id), name__iexact=name, is_deleted=False).exists():
                raise serializers.ValidationError(_("Designation with same name already exists"))
        return instance


class ReportsToSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        # depth = 1


class EmployeeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "sap_id"]


class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, instance):
        try:
            data = RoleSerializer(instance.user.role).data if instance.user else []
        except Exception as e:
            print(e)
            data = []

        return data

    class Meta:
        model = Employee
        fields = "__all__"

    def to_representation(self, instance):
        data = super(EmployeeSerializer, self).to_representation(instance)
        data["department"] = DepartmentSerializer(instance.department).data
        data["sub_department"] = SubDepartmentSerializer(instance.sub_department).data
        data["designation"] = DesignationSerializer(instance.designation).data
        data["region"] = RegionSerializer(instance.region).data
        data["city"] = CitySerializer(instance.city).data
        data["zone"] = ZoneSerializer(instance.zone).data
        data["subzone"] = SubZoneSerializer(instance.subzone).data
        data["grade"] = GradeSerializer(instance.grade).data
        data["reports_to"] = ReportsToSerializer(instance.reports_to).data if instance.reports_to else None
        data["days_of_week"] = WeekdaySerializer(instance.days_of_week.all(),
                                                 many=True).data if instance.days_of_week.all() else []
        return data

    def validate(self, instance):
        email = instance.get("email", None)
        contact_number = instance.get("contact_number", None)
        sap_id = instance.get("sap_id", None)
        role = self.initial_data.get("role", None)
        allow_login = instance.get("allow_login", None)
        if self.instance:
            id = [self.instance.id]
            email = self.instance.email

        else:
            id = []
        if sap_id:
            if Employee.objects.filter(~Q(id__in=id), sap_id__iexact=instance.get("sap_id"), is_deleted=False).exists():
                raise serializers.ValidationError(_("Employee with same sap_id already exists"))
        if contact_number:
            if Employee.objects.filter(~Q(id__in=id), contact_number__iexact=contact_number,
                                       is_deleted=False).exists():
                raise serializers.ValidationError(_("Employee with same Contact number already exists"))
        if allow_login:
            if not email:
                raise serializers.ValidationError(_("Email not provided"))
            # if not role:
            #     raise serializers.ValidationError(_("Role not provided"))
            if User.objects.filter(~Q(employee__in=id), email=email, is_deleted=False).exists():
                raise serializers.ValidationError(_("User with same email already exists"))
        return instance


class UserListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}, "otp": {'write_only': True},
                        "otp_generated_at": {'write_only': True},
                        "failed_login_attempts": {'write_only': True}, "last_failed_time": {'write_only': True}}

    def to_representation(self, instance):
        data = super(UserListingSerializer, self).to_representation(instance)
        if instance.is_superuser:
            data["role"] = "is_superuser"
        else:
            data["role"] = RoleSerializer(instance.role).data if instance.role else []
        data["employee"] = EmployeeBasicSerializer(instance.employee).data if instance.employee else []
        return data


class GroupUserListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("guid", "first_name", "last_name", "email")


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = "__all__"

    def to_representation(self, instance):
        data = super(UserGroupSerializer, self).to_representation(instance)
        data["users"] = GroupUserListingSerializer(instance.users.all(), many=True).data
        return data

    def validate(self, instance):
        name = instance.get("name")
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if UserGroup.objects.filter(~Q(id__in=id), name__iexact=name, is_deleted=False).exists():
                raise serializers.ValidationError(_("A user group with same name already exists"))
        return instance


class FeatureListingSreializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = ["id", "name", "path"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = ["id", "name"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"

    def validate(self, instance):
        name = instance.get("name")
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Module.objects.filter(~Q(id__in=id), name__iexact=name, is_deleted=False).exists():
                raise serializers.ValidationError(_("Module with same name already exists"))
        return instance


class PermissionRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleFeatureAssociation
        fields = ["id", "role", "feature", "permissions"]

    def to_representation(self, instance):
        data = super(PermissionRoleSerializer, self).to_representation(instance)
        data["feature"] = FeatureListingSreializer(instance.feature).data
        return data


class RoleFeatureAssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleFeatureAssociation
        fields = ["id", "feature", "permissions", "role"]

    def to_representation(self, instance):
        data = super(RoleFeatureAssociationSerializer, self).to_representation(instance)
        data["feature"] = FeatureListingSreializer(instance.feature).data
        data["permissions"] = PermissionSerializer(instance.permissions.all(), many=True).data
        return data


class RoleSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()

    def get_features_list(self, instance):
        try:
            features = RoleFeatureAssociationSerializer(instance.feature_association.filter(is_deleted=False),
                                                        many=True).data
            return features
        except Exception as e:
            print(e)

    class Meta:
        model = Role
        fields = ["id", "name", "features_list", "is_active"]

    def validate(self, instance):
        name = instance.get("name", None)
        if self.instance:
            id = [self.instance.id]
        else:
            id = []
        if name:
            if Role.objects.filter(~Q(id__in=id), name__iexact=name, is_deleted=False).exists():
                print(Role.objects.filter(~Q(id__in=id), name__iexact=name, is_deleted=False))
                raise serializers.ValidationError(_("Role with same name already exists"))
        return instance


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"

    def validate(self, data):
        # Check if a grade with the same prefix and number already exists
        if data.get('prefix') and Grade.objects.filter(prefix__iexact=data['prefix'],
                                                       number__iexact=data['number'], is_deleted=False).exists():
            raise serializers.ValidationError("A grade with the same prefix and number already exists.")

        # Check if a grade with the same number exists and prefix is None
        if not data.get('prefix') and Grade.objects.filter(number=data['number'], is_deleted=False).exists():
            raise serializers.ValidationError("A grade with the same number already exists.")

        return data


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class WeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekday
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    # addresses = serializers.SerializerMethodField()
    #
    # def get_addresses(self, instance):
    #     data = AddressSerializer(instance.addresses.all(), many=True).data if instance.addresses.all() else []
    #     return data

    class Meta:
        model = Company
        fields = "__all__"

    def to_representation(self, instance):
        data = super(CompanySerializer, self).to_representation(instance)
        data["reporting_currency"] = CurrencySerializer(instance.reporting_currency).data
        data["operating_currency"] = CurrencySerializer(instance.operating_currency).data
        data["days_of_week"] = WeekdaySerializer(instance.days_of_week.all(),
                                                 many=True).data if instance.days_of_week.all() else []
        data["addresses"] = AddressSerializer(instance.addresses.all(),
                                              many=True).data if instance.addresses.all() else []
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.reporting_currency = validated_data.get('reporting_currency', instance.reporting_currency)
        instance.operating_currency = validated_data.get('operating_currency', instance.operating_currency)
        instance.days_of_week.set(validated_data.get('days_of_week', instance.days_of_week.all()))
        instance.logo = validated_data.get('logo', instance.logo)
        instance.favicon = validated_data.get('favicon', instance.favicon)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.save()
        if "addresses" in self.context.get("request").data.keys():
            instance.addresses.all().delete()
            addresses = []
            address_list = self.context.get("request").data.pop("addresses")
            for address in address_list:
                addresses.append(Address(company=instance, company_address=address.get("company_address"),
                                         location_name=address.get("location_name"),
                                         is_default=address.get("is_default", False)))
            Address.objects.bulk_create(addresses)
            return instance


class FinancialDataSerializer(serializers.ModelSerializer):
    fiscal_periods = serializers.SerializerMethodField()

    def get_fiscal_periods(self, instance):
        try:
            data = FiscalPeriodSerializer(instance.fiscal_period.all(),
                                          many=True).data if instance.fiscal_period.all() else []
        except Exception as e:
            print(e)
            data = []
        return data

    class Meta:
        model = FinancialDetails
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.company = validated_data.get('company', instance.company)
        instance.name = validated_data.get('name', instance.name)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.is_locked = validated_data.get('is_locked', instance.is_locked)
        instance.period = validated_data.get('period', instance.period)
        instance.save()
        order = 1
        if "fiscal_period" in self.context.get("request").data.keys():
            instance.fiscal_period.all().delete()
            periods = []
            fiscal_period = self.context.get("request").data.pop("fiscal_period")
            for fp in fiscal_period:
                periods.append(FiscalPeriod(fiscal_year=instance, start_date=fp.get("start_date"),
                                            end_date=fp.get("end_date"), order=order,
                                            is_locked=fp.get("is_locked", False)))
                order += 1
            FiscalPeriod.objects.bulk_create(periods)
            return instance


class FiscalPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalPeriod
        fields = "__all__"
