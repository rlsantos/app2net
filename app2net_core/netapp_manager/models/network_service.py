from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import os
from infrastructure_handler.models import (
    Resource, ProgrammableTechnology, ExecutionEnvironment)

from . import Repository


def get_nad_upload_path(instance, filename):
    return f"nad/{instance.developer}/{instance.identifier}.nad"


class NetworkServiceManager(models.Manager):
    def create_from_nad(self, nad_file):
        pass


class NetworkService(models.Model):
    identifier = models.SlugField(max_length=100, blank=True)
    version = models.CharField(max_length=30, blank=True)

    developer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True
    )

    downloads = models.PositiveIntegerField(default=0, editable=False)
    nad_file = models.FileField(upload_to=get_nad_upload_path, null=True, blank=True)

    objects = NetworkServiceManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["developer", "identifier"],
                name="unique_app_identifier_per_developer"
            )
        ]

    def __str__(self):
        return f"{self.developer}.{self.identifier}"

    @property
    def complete_identifier(self):
        return str(self)

    def get_info(self, technology):
        package = self.packages.get(technology=technology)
        # Merging querysets
        requirements = (
            package.requirements.all() |
            package.execution_environment.requirements.all()
        )
        return (requirements.most_restrictive(), 
                package.nacr, package.location_flag)


class NetworkServicePackage(models.Model):
    class LocationFlagChoices(models.TextChoices):
        INGRESS = ("I", _("Ingress"))
        EGRESS = ("E", _("Egress"))
        BORDER = ("B", _("Border"))
        CUSTOM = ("C", _("Custom"))
        ALL = ("A", _("All"))

    class NetAppType(models.TextChoices):
        NETAPP = ("NetApp", _("NetApp"))
        VNA = ("VNA", _("VNA"))

    network_service = models.ForeignKey(
        NetworkService,
        on_delete=models.CASCADE,
        related_name="packages",
        verbose_name=_("Network Service"),
    )
    technology = models.ForeignKey(
        ProgrammableTechnology, on_delete=models.SET_NULL, null=True
    )
    type = models.CharField(max_length=6, choices=NetAppType.choices,
                            default=NetAppType.NETAPP)
    execution_environment = models.ForeignKey(
        ExecutionEnvironment, on_delete=models.SET_NULL, null=True
    )
    nacr = models.ForeignKey(Repository, on_delete=models.CASCADE,
                             related_name="network_services")
    requirements = models.ManyToManyField(Resource, blank=True)
    location_flag = models.CharField(max_length=1, choices=LocationFlagChoices.choices)
    file_path = models.CharField(max_length=500)
    hash = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('network_service', 'technology'),
                name='single_package_per_technology'
            ),
        ]

    def __str__(self):
        return f"{self.network_service}: {self.technology}"

    @property
    def uri(self):
        return os.path.join(self.nacr.address, self.file_path)

    def install(self, nodes):
        for node in nodes:
            connection = node.connect()
            connection.download()


class Action(models.Model):
    name = models.CharField(max_length=50)
    package = models.ForeignKey(NetworkServicePackage,
                                on_delete=models.CASCADE, related_name="actions")
    command = models.TextField()
    native_procedure = models.BooleanField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "package"],
                name="unique_action_name_per_package"
            )
        ]
