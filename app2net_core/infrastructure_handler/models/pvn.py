from django.db import models, transaction
from django.contrib.auth import get_user_model
from .driver import Driver


class Pvn(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(get_user_model(), verbose_name="PVN Owner", related_name="pvns")

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
        pass
