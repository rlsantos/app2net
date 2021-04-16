from django.db import models
from .resource import Resource


class ProgrammableTechnology(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Programmable Technologies"

    def __str__(self):
        return f"{self.name} {self.version}"
