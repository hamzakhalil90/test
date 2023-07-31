from django.db import models
from django.core.validators import RegexValidator

from area_management.models import Region
from utils.base_models import LogsMixin
from django.db.models import Q, UniqueConstraint


class BrandType(LogsMixin):
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    code = models.CharField(max_length=50, unique=True, editable=False)
    description = models.CharField(max_length=250, null=True, blank=True)
    region = models.ManyToManyField(Region, related_name='brand_type', null=True, blank=True)

    def generate_code(self):
        """Generate a unique code for the BrandType model"""
        prefix = "BRAND"
        last_obj = BrandType.objects.order_by("-id").first()
        if last_obj is None:
            # If there are no objects yet, start with code BRAND0001
            return f"{prefix}0001"
        else:
            # Increment the code by 1
            last_code = last_obj.code
            last_num = int(last_code.replace(prefix, ""))
            next_num = last_num + 1
            return f"{prefix}{next_num:04}"

    def save(self, *args, **kwargs):
        """Override the save method to set the code field with the generated code"""
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)


class Brand(LogsMixin):
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 .]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    code = models.CharField(max_length=50)
    brand_type = models.ForeignKey(BrandType, on_delete=models.CASCADE, related_name="brand")
