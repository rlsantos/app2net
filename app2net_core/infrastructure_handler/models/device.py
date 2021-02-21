from django.db import models
from constants import DEVICE_STATUS
from .pvn import Pvn
from .driver import Driver
from .resource import Resource
from .credential import Credential
from .programmable_technology import ProgrammableTechnology


class Device(models.Model):
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=DEVICE_STATUS, default='active')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    pvn = models.ForeignKey(Pvn, on_delete=models.CASCADE, related_name="devices")
    drivers = models.ManyToManyField(Driver, through='infrastructure_handler.InstalledDriver', 
                                     verbose_name='List of Drivers', related_name="devices")
    resources = models.ManyToManyField(Resource, verbose_name='List of Available Resources', 
                                       related_name="devices")
    credentials = models.ManyToManyField(Credential, verbose_name='Available Credentials', 
                                         related_name="devices")
    programmable_technologies = models.ManyToManyField(
        ProgrammableTechnology, verbose_name='Available Programmable Technologies')
    
    def __str__(self):
        return f"{self.pvn} - {self.name}"
