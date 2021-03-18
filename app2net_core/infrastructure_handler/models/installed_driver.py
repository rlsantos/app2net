from django.db import models
from .driver import Driver
from .device import Device

# ToDo: Add the running port to model


class InstalledDriver(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE,
                               related_name="installed_drivers")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE,
                               related_name="installations")
    port = models.PositiveIntegerField(default=5555)
    install_driver_date = models.DateTimeField(auto_now_add=True)
    update_driver_date = models.DateTimeField(auto_now=True)
