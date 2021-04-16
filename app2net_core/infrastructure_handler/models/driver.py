from django.db import models
from constants import DRIVER_STATUS
from infrastructure_handler.models.execution_environment import ExecutionEnvironment
from infrastructure_handler.models.programmable_technology import ProgrammableTechnology


class Driver(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=DRIVER_STATUS, default='active')
    package = models.FileField(null=True)
    technology = models.ForeignKey(ProgrammableTechnology, on_delete=models.CASCADE, null=True)
    execution_environments = models.ManyToManyField(ExecutionEnvironment, related_name='drivers')

    def __str__(self):
        return f"{self.name} {self.version} ({self.status})"
