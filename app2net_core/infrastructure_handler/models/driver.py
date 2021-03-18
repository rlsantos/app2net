from django.db import models
from constants import DRIVER_STATUS


class Driver(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=DRIVER_STATUS, default='active')
    package = models.FileField(null=True)

    def __str__(self):
        return f"{self.name} {self.version} ({self.status})"
