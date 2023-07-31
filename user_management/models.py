import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from dateutil.relativedelta import relativedelta
import datetime
from django.db.models import Q, UniqueConstraint
from LCLPD_backend.settings import *
from area_management.models import *
from utils.base_models import LogsMixin
from utils.reusable_methods import generate_access_token


# Create your models here.
class Features(LogsMixin):
    """Model for storing features"""

    name = models.TextField(max_length=50, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    path = models.CharField(max_length=50)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "is_deleted"],
                name="unique_feature",
                condition=Q(is_deleted="f"),
            )
        ]


class Permissions(LogsMixin):
    name = models.TextField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    code = models.CharField(max_length=10)


class Role(LogsMixin):
    name = models.TextField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )


class RoleFeatureAssociation(LogsMixin):
    role = models.ForeignKey(
        "Role", on_delete=models.CASCADE, related_name="feature_association"
    )
    permissions = models.ManyToManyField("Permissions", related_name="role_permissions")
    feature = models.ForeignKey(Features, on_delete=models.CASCADE)


class User(LogsMixin, AbstractUser):
    """Fully featured User model, email and password are required.
    Other fields are optional.
    """
    status_choices = (
        ("INACTIVE", "INACTIVE"),
        ("ACTIVE", "ACTIVE"),
    )

    user_types = (("SA", "Super Admin"), ("A", "Admin"))
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.CharField(max_length=8, default="ACTIVE", choices=status_choices)
    contact_number = models.CharField(max_length=25, unique=True, blank=True, null=True)
    otp = models.IntegerField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    REQUIRED_FIELDS = ["email", "password"]
    user_type = models.CharField(max_length=50, choices=user_types)
    employee = models.OneToOneField(
        "Employee",
        on_delete=models.DO_NOTHING,
        related_name="user",
        null=True,
        blank=True,
    )
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_time = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    image = models.ImageField(upload_to="Images/", blank=True, null=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.DO_NOTHING,
        related_name="user_role",
        null=True,
        blank=True,
    )

    def get_access_token(self):
        return generate_access_token(self)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, raw_password):
        # Store the new password in the password history
        UserPasswordHistory.objects.create(
            user=self, password=make_password(raw_password)
        )
        super().set_password(raw_password)


class Token(LogsMixin):
    """Token model for authentication"""

    user = models.ForeignKey(
        AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE, related_name="token"
    )
    token = models.TextField(max_length=500, unique=True, null=False, blank=False)


class Department(LogsMixin):
    category = (
        ("IL", "Internal"),
        ("EL", "External"),
    )
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    details = models.TextField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=10, choices=category)
    department_head = models.ForeignKey(
        "Employee",
        on_delete=models.DO_NOTHING,
        related_name="heads_department",
        null=True,
        blank=True,
    )


class SubDepartment(LogsMixin):
    category = (
        ("IL", "Internal"),
        ("EL", "External"),
    )
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    details = models.TextField(max_length=1000, null=True, blank=True)
    category = models.CharField(max_length=10, choices=category)
    head = models.ForeignKey(
        "Employee",
        on_delete=models.DO_NOTHING,
        related_name="heads_sub_department",
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.DO_NOTHING,
        related_name="sub_department",
        null=True,
        blank=True,
    )


class Designation(LogsMixin):
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    details = models.TextField(max_length=1000, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.DO_NOTHING, related_name="designation"
    )
    # grade = models.IntegerField()


class Grade(LogsMixin):
    prefix = models.CharField(max_length=4, null=True, blank=True,
                              validators=[
                                  RegexValidator(
                                      r"^[a-zA-Z0-9 ]+$",
                                      message="Grade-Prefix field should not contain special characters",
                                  )
                              ],
                              )
    number = models.CharField(max_length=2,
                              validators=[
                                  RegexValidator(
                                      r"^[0-9]+$",
                                      message="Grade-Postfix can only contain digits.",
                                  )
                              ],
                              )


class Employee(LogsMixin):
    first_name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    date_of_birth = models.DateField()

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    email = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                r"^[0-9]+$", message="Contact number field should only contain digits"
            )
        ],
    )
    emergency_contact_number = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r"^[0-9]+$", message="Contact number field should only contain digits"
            )
        ],
    )

    emergency_contact_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )

    address = models.TextField(max_length=500)
    date_of_joining = models.DateField()
    department = models.ForeignKey(
        Department, on_delete=models.DO_NOTHING, related_name="employee_department"
    )
    sub_department = models.ForeignKey(
        SubDepartment, on_delete=models.DO_NOTHING, related_name="employee_sub_department", null=True, blank=True
    )
    designation = models.ForeignKey(
        Designation, on_delete=models.DO_NOTHING, related_name="employee_designation"
    )
    sap_id = models.CharField(max_length=25, blank=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.DO_NOTHING,
        related_name="employee",
        null=True,
        blank=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="employee",
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="employee",
    )
    subzone = models.ForeignKey(
        SubZone,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="employee",
    )
    allow_login = models.BooleanField(default=False)
    reports_to = models.ForeignKey(
        "Employee",
        on_delete=models.DO_NOTHING,
        related_name="managing",
        null=True,
        blank=True,
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.DO_NOTHING,
        related_name="grade",
        null=True,
        blank=True,
    )
    days_of_week = models.ManyToManyField("Weekday", related_name="employee_working_days")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)


class UserPasswordHistory(LogsMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)


class Module(LogsMixin):
    name = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    description = models.TextField(max_length=250, null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)
    status = models.IntegerField(default=1)


class UserGroup(LogsMixin):
    name = models.CharField(
        max_length=60,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    users = models.ManyToManyField("User", related_name="group_users")


class Company(LogsMixin):
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )

    reporting_currency = models.ForeignKey("Currency", on_delete=models.DO_NOTHING, null=True,
                                           related_name="reporting_company", blank=True)
    operating_currency = models.ForeignKey("Currency", on_delete=models.DO_NOTHING, related_name="operating_company",
                                           null=True, blank=True)

    days_of_week = models.ManyToManyField("Weekday", related_name="working_days")

    logo = models.ImageField(upload_to="Images/", blank=True, null=True)
    favicon = models.ImageField(upload_to="Images/", blank=True, null=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)


class Currency(LogsMixin):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10, null=True, blank=True)


class Weekday(LogsMixin):
    name = models.CharField(max_length=10, null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)


class Address(LogsMixin):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="addresses")
    location_name = models.CharField(max_length=50, null=True, blank=True)
    company_address = models.CharField(max_length=200, null=True, blank=True)
    is_default = models.BooleanField(default=False)


class FinancialDetails(LogsMixin):
    status_choices = (
        ("OPEN", "OPEN"),
        ("CLOSED", "CLOSED"),
        ("PENDING", "PENDING"),
    )

    period_types = (
        ("ANNUAL", "ANNUAL"),
        ("BI-ANNUAL", "BI-ANNUAL"),
        ("QUARTERLY", "QUARTERLY"),
        ("MONTHLY", "MONTHLY"),
    )
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name="financials")
    name = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=status_choices)
    is_locked = models.BooleanField(default=False)
    period = models.CharField(max_length=10, choices=period_types)


class FiscalPeriod(LogsMixin):
    fiscal_year = models.ForeignKey(FinancialDetails, on_delete=models.DO_NOTHING, related_name="fiscal_period")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    order = models.IntegerField()
    is_locked = models.BooleanField(default=False)
