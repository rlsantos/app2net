from django.db import models
from .device import Device


class Interface(models.Model):
    name = models.CharField(max_length=50)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="interfaces")

    def __str__(self):
        return f"{self.device} - {self.name}"
