from utils.base_models import LogsMixin
from area_management.models import *
from user_management.models import User
from django.db import models
from django.core.validators import RegexValidator


# Create your models here.
class Channel(LogsMixin):
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    code = models.CharField(max_length=100)
    marker = models.ImageField(upload_to="Images/", blank=True, null=True)


class Outlet(LogsMixin):
    category = (
        ("IL", "Internal"),
        ("EL", "External"),
    )
    sap_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="SapCode field should not contain special characters",
            )
        ],
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    ntn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    strn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    address = models.CharField(max_length=100, null=True, blank=True)
    owner_name = models.CharField(max_length=100)
    owner_cnic = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(max_length=35, null=True, blank=True)
    owner_contact = models.CharField(max_length=15, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, choices=category)
    region = models.ForeignKey(
        Region, on_delete=models.DO_NOTHING, related_name="outlet_region"
    )
    city = models.ForeignKey(
        City, on_delete=models.DO_NOTHING, related_name="outlet_city"
    )
    zone = models.ForeignKey(
        Zone, on_delete=models.DO_NOTHING, related_name="outlet_zone"
    )
    sub_zone = models.ForeignKey(
        SubZone, on_delete=models.CASCADE, related_name="outlet_sub_zone"
    )
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="outlet"
    )
    allow_login = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="corresponding_outlet", null=True,
                             blank=True)
    image = models.ImageField(upload_to="Images/", blank=True, null=True)
    name_on_board = models.CharField(max_length=100, validators=[
        RegexValidator(r"^[a-zA-Z0-9 ]+$", message="Name field should not contain special characters", )], null=True,
                                     blank=True, )
    regional_manager = models.ManyToManyField(User, related_name="outlets_under_rm", null=True,
                                              blank=True, )
    zonal_manager = models.ManyToManyField(User, related_name="outlets_under_zm", null=True,
                                           blank=True, )
    dsr = models.ManyToManyField(User, related_name="outlets_under_dsr", null=True,
                                 blank=True, )
    is_distributor = models.BooleanField(default=False)
    distributor = models.ManyToManyField("Outlet",
                                         related_name="managing_outlets",
                                         null=True,
                                         blank=True)
