from django.db import models
from django.db.models import Subquery, OuterRef
from django.db.models.functions import Cast
from constants import DEVICE_STATUS, Units

from infrastructure_handler.models import ExecutionEnvironment

from system_notifier.notification_exchanger import NodeNotifier

from .pvn import Pvn
from .driver import Driver
from .resource import Resource
from .credential import Credential
from .programmable_technology import ProgrammableTechnology


class DeviceQuerySet(models.QuerySet):
    def filter_compatible(self, requirements):
        qs = self
        for requirement in requirements:
            qs = qs.filter(resources__name=requirement.name)
            resource_value = Subquery(
                Resource.objects.filter(
                    devices=OuterRef('pk'),
                    name=requirement.name
                ).values('value')
            )
            if requirement.resource_type.unit == Units.VERSION:
                qs = qs.annotate(
                    resource_value=resource_value
                ).filter(resource_value__gte=requirement.value)
            else:
                qs = qs.annotate(
                    resource_value=Cast(resource_value, models.IntegerField())
                ).filter(resource_value__gte=requirement.value)

        return qs


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
    execution_environments = models.ManyToManyField(
        ExecutionEnvironment, verbose_name="Available execution environments"
    )

    objects = DeviceQuerySet.as_manager()

    def __str__(self):
        return f"{self.pvn} - {self.name}"

    def install_driver(self, driver, port):
        """Validate the requirements and install requested the driver

        Arguments:
            driver (Driver): Driver to be installed on device
            port (int): Port that the driver daemon will listen
        
        ToDo:
            Real Implementation
        """
        # Dummy code
        connection = self.credentials.filter(uploadable=True).first().connect()
        connection.run(driver.install_command)
        connection.run(driver.up_command.format(port))

        self.drivers.through.create(
            driver=driver,
            port=port
        )

    def connect(self):
        """Open a connection to the device

        ToDo:
            Make port dynamic
        """
        return NodeNotifier(
            self.interfaces.first().addresses.first().value,
            5555
        )
