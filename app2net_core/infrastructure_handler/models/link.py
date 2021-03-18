from django.db import models
from constants import LINK_STATUS, UNITS
from .interface import Interface


class Link(models.Model):
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=LINK_STATUS, default='active')
    max_speed = models.FloatField(help_text='Insert the max speed of the link')
    unit = models.CharField(max_length=10, choices=UNITS, help_text = 'Choose the measurement unit for the resource')
    interface = models.OneToOneField(Interface, on_delete=models.CASCADE)


class Internal(Link):
    destination = models.OneToOneField(Interface, on_delete=models.CASCADE)


class External(Link):
    internet_access = models.BooleanField(default=False)
    observations = models.TextField(null=True)
