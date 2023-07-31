from channel_management.models import *
from inventory_management.models import *
from notifications_management.models import *
from user_management.models import *
from market_intelligence.models import *
from channel_management.serializers import *
from area_management.serializers import *
import pandas as pd
from django.db.models import ManyToManyField
import io
import xlwt
from django.http import FileResponse
from inventory_management.serializers import *
from notifications_management.serializers import *
from user_management.serializers import *
from market_intelligence.serializers import *
from datetime import datetime

model_names = {
    "area/country": Country,
    "area/region": Region,
    "area/city": City,
    "area/zone": Zone,
    "area/sub_zone": SubZone,
    "channel/": Channel,
    "channel/outlet": Outlet,
    "channel/distributor": Outlet,
    "inventory/product": Product,
    "inventory/product_type": ProductType,
    "inventory/warehouse": Warehouse,
    "inventory/plant": Plant,
    "inventory/launch-product": Product,
    "market_intelligence/brand": Brand,
    "market_intelligence/brand_type": BrandType,
    "notifications/email": EmailTemplate,
    "role": Role,
    "user": User,
    "department": Department,
    "sub-department": SubDepartment,
    "designation": Designation,
    "grade": Grade,
    "employee": Employee,
    "usergroup": UserGroup,
    "module": Module
}

model_serializers = {
    "area/region": RegionSerializer,
    "area/city": CitySerializer,
    "area/zone": ZoneSerializer,
    "area/sub_zone": SubZoneSerializer,
    "channel/": ChannelSerializer,
    "channel/outlet": OutletSerializer,
    "channel/distributor": OutletSerializer,
    "inventory/product": ProductSerializer,
    "inventory/product_type": ProductTypeSerializer,
    "inventory/warehouse": WarehouseSerializer,
    "inventory/plant": PlantSerializer,
    "inventory/launch-product": ProductSerializer,
    "market_intelligence/brand": BrandSerializer,
    "market_intelligence/brand_type": BrandTypeSerializer,
    "notifications/email": EmailTemplateSerializer,
    "role": RoleSerializer,
    "user": UserListingSerializer,
    "department": DepartmentSerializer,
    "sub-department": SubDepartmentSerializer,
    "designation": DesignationSerializer,
    "grade": GradeSerializer,
    "employee": EmployeeSerializer,
    "usergroup": UserGroupSerializer,
    "module": ModuleSerializer
}


def get_region_parent_records(data):
    data["country"] = Country.objects.filter(name__iexact=data.get("country"), is_deleted=False).first()
    return data


def get_city_parent_records(data):
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    return data


def get_zone_parent_records(data):
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    return data


def get_sub_zone_parent_records(data):
    data["zone"] = Zone.objects.filter(name__iexact=data.get("zone"), is_deleted=False).first()
    return data


def get_outlet_parent_records(data):
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    data["zone"] = Zone.objects.filter(name__iexact=data.get("zone"), is_deleted=False).first()
    data["sub_zone"] = SubZone.objects.filter(name__iexact=data.get("sub_zone"), is_deleted=False).first()
    data["channel"] = Channel.objects.filter(name__iexact=data.get("channel"), is_deleted=False).first()
    return data


def get_warehouse_parent_records(data):
    first_name, last_name = data["person_in_control"].split() if data["person_in_control"] else (None, None)
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    data["zone"] = Zone.objects.filter(name__iexact=data.get("zone"), is_deleted=False).first()
    data["person_in_control"] = Employee.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name,
                                                        is_deleted=False).first()
    data["product"] = Product.objects.filter(name__iexact=data.get("product"), is_deleted=False).first()
    return data


def get_plant_parent_records(data):
    first_name, last_name = data["person_in_control"].split() if data["person_in_control"] else (None, None)
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    data["person_in_control"] = Employee.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name,
                                                        is_deleted=False).first()
    data["product"] = Product.objects.filter(name__iexact=data.get("product"), is_deleted=False).first()
    return data


def get_product_parent_records(data):
    data["country"] = Country.objects.filter(name__iexact=data.get("country"), is_deleted=False).first()
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    data["zone"] = Zone.objects.filter(name__iexact=data.get("zone"), is_deleted=False).first()
    data["subzone"] = SubZone.objects.filter(name__iexact=data.get("subzone"), is_deleted=False).first()
    data["channel"] = Channel.objects.filter(name__iexact=data.get("channel"), is_deleted=False).first()
    data["manufacturer"] = Brand.objects.filter(name__iexact=data.get("manufacturer"), is_deleted=False).first()
    data["product_type"] = ProductType.objects.filter(name__iexact=data.get("product_type"), is_deleted=False).first()
    return data


def get_brand_parent_records(data):
    data["brand_type"] = BrandType.objects.filter(name__iexact=data.get("brand_type"), is_deleted=False).first()
    return data


def get_email_parent_records(json_data):
    # recipient_list = User.objects.all()
    # recipient_roles = Role.objects.all()
    # recipient_group = UserGroup.objects.all()
    # request_data = []
    # for data in data:
    #     data["recipient_list"] = recipient_list.get(name__iexact=data["recipient_list"]) if data["recipient_list"]
    #     data["recipient_roles"] = recipient_roles.get(name__iexact=data["recipient_roles"])
    #     data["recipient_group"] = recipient_group.get(name__iexact=data["recipient_group"])
    #     request_data.append(data)

    return json_data


def get_user_parent_records(data):
    data["employee"] = Employee.objects.filter(name__iexact=data.get("employee"), is_deleted=False).first()
    data["outlet"] = Outlet.objects.filter(name__iexact=data.get("outlet"), is_deleted=False).first()
    data["role"] = Role.objects.filter(name__iexact=data.get("role"), is_deleted=False).first()
    return data


def get_department_parent_records(data):
    first_name, last_name = data["department_head"].split() if data["department_head"] else (None, None)
    data["department_head"] = Employee.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name,
                                                     is_deleted=False).first()
    return data


def get_designation_parent_records(data):
    if "department" in data.keys():
        data["department"] = Department.objects.filter(name__iexact=data.get("department"), is_deleted=False).first()
    return data


def get_employee_parent_records(data):
    prefix, number = data["grade"].split("-") if data["grade"] else (None, None)
    first_name, last_name = data["reports_to"].split() if data["reports_to"] else (None, None)
    data["department"] = Department.objects.filter(name__iexact=data.get("department"), is_deleted=False).first()
    data["sub_department"] = SubDepartment.objects.filter(name__iexact=data.get("sub_department"),
                                                   is_deleted=False).first()
    data["designation"] = Designation.objects.filter(name__iexact=data.get("designation"), is_deleted=False).first()
    data["region"] = Region.objects.filter(name__iexact=data.get("region"), is_deleted=False).first()
    data["city"] = City.objects.filter(name__iexact=data.get("city"), is_deleted=False).first()
    data["zone"] = Zone.objects.filter(name__iexact=data.get("zone"), is_deleted=False).first()
    data["subzone"] = SubZone.objects.filter(name__iexact=data.get("subzone"), is_deleted=False).first()
    data["reports_to"] = Employee.objects.filter(first_name__iexact=first_name, last_name__iexact=last_name,
                                           is_deleted=False).first()
    data["grade"] = Grade.objects.filter(prefix__iexact=prefix, number__iexact=number, is_deleted=False).first()
    return data


def get_user_group_parent_records(data):
    data["users"] = User.objects.filter(name__iexact=data.get("users"), is_deleted=False).first()
    return data


# Country, grade, module, product, productList, role, brandType, Channel have no functions
model_names_with_get_parent_functions = {
    "area/region": get_region_parent_records,
    "area/city": get_city_parent_records,
    "area/zone": get_zone_parent_records,
    "area/sub_zone": get_sub_zone_parent_records,
    "channel/outlet": get_outlet_parent_records,
    "inventory/warehouse": get_warehouse_parent_records,
    "inventory/plant": get_plant_parent_records,
    "inventory/product": get_product_parent_records,
    "market_intelligence/brand": get_brand_parent_records,
    "notifications/email": get_email_parent_records,
    "user": get_user_parent_records,
    "department": get_department_parent_records,
    "designation": get_designation_parent_records,
    "employee": get_employee_parent_records,
    "usergroup": get_user_group_parent_records,
}


def check_for_date_fields(data):
    date_fields = ["date_of_birth", "date_of_joining"]
    for field in date_fields:
        if field in data.keys():
            data[field] = data[field].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime) else x)

    return data


def parse_instance_ids(data):
    for key, value in data.items():
        if isinstance(value, models.Model):
            data[key] = value.id
        elif isinstance(value, list):
            data[key] = [v.id for v in value if isinstance(v, models.Model)]
    return data


def generate_execl_file(columns, records, filename):
    try:
        buffer = io.BytesIO()
        wb = xlwt.Workbook(encoding="utf-8")
        filename = filename.split("/")[-1]
        ws = wb.add_sheet(filename + "_rejected_records")
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        row_num = 0
        for col_num in columns:
            ws.write(0, row_num, col_num, font_style)
            row_num += 1
        count = 0
        for y, row in enumerate(records, start=1):
            for column_num, column in enumerate(columns):
                ws.write(count + y, column_num, str(row[column]))
            y += 1
        count += 1
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(e)


def convert_many_to_many_fields_to_list(object, fields):
    for field in fields:
        if isinstance(field, ManyToManyField):
            object[field.name] = [object[field.name]]
    return object


def bulk_create_objects(model, data_list):
    many_to_many_fields = [
        field.name for field in model._meta.get_fields() if isinstance(field, ManyToManyField)
    ]

    objects_to_create = []
    related_objects = {}
    for data in data_list:
        related_data = {}
        for field_name in many_to_many_fields:
            if field_name in data:
                related_data[field_name] = data.pop(field_name)
        objects_to_create.append(model(**data))
        related_objects[model] = related_data

    # Bulk create the objects
    created_objects = model.objects.bulk_create(objects_to_create)

    # Process many-to-many relationships
    for obj in created_objects:
        related_data = related_objects.get(type(obj))
        if related_data:
            for field_name, values in related_data.items():
                field = getattr(obj, field_name)
                values = [] if values is None else values
                field.set(values)

    return created_objects
