from market_intelligence.models import Brand
from user_management.models import *
from area_management.models import *
from channel_management.models import *
import uuid


class ProductType(LogsMixin):
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

    def generate_code(self):
        """Generate a unique code for the ProductType model"""
        prefix = "PROD"
        last_obj = ProductType.objects.order_by("-id").first()
        if last_obj is None:
            # If there are no objects yet, start with code PROD0001
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


class Product(LogsMixin):
    weight_measurement_choices = (
        ("KG", "KG"),
        ("MT", "MT")
    )
    category = (("IL", "Internal"), ("EL", "External"))
    name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9 ]+$",
                message="Name field should not contain special characters",
            )
        ],
    )
    code = models.CharField(max_length=50)
    description = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(upload_to="Images/", blank=True, null=True)
    manufacturer = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="product_manufacturer"
    )

    weight = models.CharField(max_length=50)
    unit_of_measurement = models.CharField(max_length=30, choices=weight_measurement_choices)
    dimensions = models.CharField(max_length=50, null=True, blank=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="product")
    is_launched = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)
    subzone = models.ForeignKey(SubZone, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.DO_NOTHING, related_name="products", null=True, blank=True)

    def weight_in_grams(self):
        return self.weight * 1000

    @property
    def weight_in_pounds(self):
        return self.weight * 2.20462

    @property
    def weight_in_bags(self):
        return self.weight / 50

    @property
    def weight_in_tons(self):
        return self.weight / 1000


class Warehouse(LogsMixin):
    category = (("IL", "Internal"), ("EL", "External"))

    name = models.CharField(max_length=30, validators=[
        RegexValidator(
            r"^[a-zA-Z0-9 ]+$",
            message="Name field should not contain special characters",
        )
    ])
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="warehouse_region")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="warehouse_city")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="warehouse_zone")
    address = models.CharField(max_length=50)
    person_in_control = models.ForeignKey(Employee, null=True, blank=True, related_name="warehouse",
                                          on_delete=models.DO_NOTHING)
    items_capacity = models.CharField(max_length=50, null=True, blank=True)
    warehouse_square_footage = models.CharField(max_length=50, null=True, blank=True)
    product = models.ManyToManyField("Product", related_name="warehouse_products")
    storage_types = models.CharField(max_length=50, null=True, blank=True)
    loading_unloading_info = models.CharField(max_length=50, null=True, blank=True)
    operating_hours = models.CharField(max_length=50, null=True, blank=True)
    sap_id = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    additional_information = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50)
    category = models.CharField(max_length=10, choices=category)


class Plant(LogsMixin):
    name = models.CharField(max_length=50, validators=[
        RegexValidator(r"^[a-zA-Z0-9 ]+$", message="Name field should not contain special characters")])
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="plant"
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="plant_city")
    address = models.CharField(max_length=50)
    person_in_control = models.ForeignKey(Employee, null=True, blank=True, related_name="plant",
                                          on_delete=models.DO_NOTHING)
    manufacturing_capacity = models.CharField(max_length=50, null=True, blank=True)
    storage_capacity = models.CharField(max_length=50, null=True, blank=True)
    product = models.ManyToManyField("Product", related_name="plant_products")
    storage_types = models.CharField(max_length=50, null=True, blank=True)
    loading_unloading_info = models.CharField(max_length=50, null=True, blank=True)
    security_control_mechanism = models.CharField(max_length=50, null=True, blank=True)
    operating_hours = models.CharField(max_length=50, null=True, blank=True)
    sap_id = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    additional_information = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50)
