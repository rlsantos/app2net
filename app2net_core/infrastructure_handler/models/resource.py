from django.db import models
from django.db.models import F, Q, Max, Min, Window
from django.db.models.functions import Cast
from constants import LOGICAL_RESOURCE_STATUS, Units



class ResourceType(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=10, choices=Units.choices,
                            help_text='Choose the measurement unit for the resource')

    def __str__(self):
        return f"{self.name} ({self.unit})"


class ResourceQuerySet(models.QuerySet):
    def most_restrictive(self):
        max_int_resources = self.exclude(resource_type__unit=Units.VERSION).annotate(
            max_value=Window(
                expression=Max(Cast('value', models.IntegerField())),  
                partition_by=[F('name')],
            ),
        ).values('name', 'max_value')
        
        max_str_resources = self.filter(resource_type__unit=Units.VERSION).annotate(
            max_value=Window(
                expression=Max('value'),  
                partition_by=[F('name')],
            ),
        ).values('name', 'max_value')
        
        max_values_filter = Q()
        for resource_type in [max_int_resources, max_str_resources]:
            for resource in resource_type:
                max_values_filter |= Q(
                    name=resource["name"],
                    value=str(resource["max_value"])
                )
        
        return self.filter(max_values_filter).distinct() 

    def least_restrictive(self):
        min_int_resources = self.exclude(resource_type__unit=Units.VERSION).annotate(
            min_value=Window(
                expression=Min(Cast('value', models.IntegerField())),  
                partition_by=[F('name')],
            ),
        ).values('name', 'min_value')
        
        min_str_resources = self.filter(resource_type__unit=Units.VERSION).annotate(
            min_value=Window(
                expression=Min('value'),  
                partition_by=[F('name')],
            ),
        ).values('name', 'min_value')
        
        min_values_filter = Q()
        for resource_type in [min_int_resources, min_str_resources]:
            for resource in resource_type:
                min_values_filter |= Q(
                    name=resource["name"],
                    value=str(resource["min_value"])
                )

        return self.filter(min_values_filter).distinct() 


class Resource(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(
        max_length=30, help_text='Specify the frequency, speed, clock, quantity, capacity or version of the resource')
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)

    objects = ResourceQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "value"],
                name="unique_name_value_combination"
            ),
        ]

    def __str__(self):
        return f"{self.name}: {self.value} {self.resource_type.unit}"


class Physical(Resource):
    manufacturer = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)


class Logical(Resource):
    status = models.CharField(
        max_length=20, choices=LOGICAL_RESOURCE_STATUS, default='active')
