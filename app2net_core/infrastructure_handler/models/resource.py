from django.db import models
from constants import LOGICAL_RESOURCE_STATUS, Units


class ResourceType(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=Units.choices,
                            help_text='Choose the measurement unit for the resource')

    def __str__(self):
        return f"{self.name} ({self.unit})"


class Resource(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(
        max_length=30, help_text='Specify the frequency, speed, clock, quantity, capacity or version of the resource')
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}: {self.value} {self.resource_type.unit}"


class Physical(Resource):
    manufacturer = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)


class Logical(Resource):
    status = models.CharField(
        max_length=20, choices=LOGICAL_RESOURCE_STATUS, default='active')
