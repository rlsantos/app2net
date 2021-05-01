from django.db import models

from infrastructure_handler.models.programmable_technology import ProgrammableTechnology

from .resource import Resource


class ExecutionEnvironment(models.Model):
    name = models.CharField(max_length=50)
    programmable_technology = models.ForeignKey(
        ProgrammableTechnology, 
        on_delete=models.CASCADE, 
        related_name="execution_environments"
    )
    version = models.CharField(max_length=30)
    requirements = models.ManyToManyField(
        Resource, 
        blank=True
    )

    def __str__(self):
        return self.name
