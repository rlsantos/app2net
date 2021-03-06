from django.db import models
from .interface import Interface


class AddressType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Address(models.Model):
    value = models.CharField(max_length=128)
    mask = models.PositiveSmallIntegerField(null=True, help_text='Insert the mask in the CIDR notation')
    address_type = models.ForeignKey(AddressType, on_delete=models.CASCADE, related_name="addresses")
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='addresses')

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.value} ({self.interface})"
