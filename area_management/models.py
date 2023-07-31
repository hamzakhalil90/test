from django.core.validators import RegexValidator
from django.db import models

from utils.base_models import LogsMixin


# Create your models here

class Country(LogsMixin):
    name = models.CharField(max_length=100, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    code = models.CharField(max_length=20)

    class Meta:
        ordering = ['name']


class Region(LogsMixin):
    name = models.CharField(max_length=100, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    code = models.CharField(max_length=20)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="region")


class City(LogsMixin):
    name = models.CharField(max_length=100, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    code = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="city")


class Zone(LogsMixin):
    name = models.CharField(max_length=100, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    code = models.CharField(max_length=20)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="zone")


class SubZone(LogsMixin):
    name = models.CharField(max_length=100, validators=[
        RegexValidator(r'^[a-zA-Z0-9 ]+$', message="Name field should not contain special characters")])
    code = models.CharField(max_length=20)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="subzone")
