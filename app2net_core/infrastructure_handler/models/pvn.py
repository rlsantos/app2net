from django.db import models
from django.contrib.auth import get_user_model

from uuid import uuid4

from .driver import Driver


class Pvn(models.Model):
    id = models.UUIDField(editable=False, default=uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    owners = models.ManyToManyField(get_user_model(), verbose_name="PVN Owner", related_name="pvns")

    def __str__(self):
        return f"{self.name}"

    def install_drivers(self):
        for device in self.devices:
            current_port = 5555
            drivers = Driver.objects.filter(
                programmable_technology__in=device.programmable_technologies
            )
            for driver in drivers:
                device.install_driver(driver, current_port)
                current_port += 1

    def install(self, network_service):
        pass

    def get_info(self):
        return PvnInfo(self)


class PvnInfo:
    def __init__(self, pvn, technology=None, network_service=None):
        self.pvn = pvn

        self.technologies = pvn.devices.values('execution_environments').distinct()
        print(self.technologies)
        if technology is not None and technology in self.technologies:
            self.technologies = self.technologies.get(id=technology.id)

        self.devices = pvn.devices.filter(execution_environments__in=self.technologies)