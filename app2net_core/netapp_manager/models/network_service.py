from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import os

from infrastructure_handler.models import Resource, ProgrammableTechnology

from . import Repository


class NetworkService(models.Model):
    identifier = models.CharField(max_length=100)
    developer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["developer", "identifier"],
                name="unique_app_identifier_per_developer"
            )
        ]

    def __str__(self):
        return f"{self.developer}.{self.identifier}"

    def get_info(self, technology):
        package = self.packages.get(technology=technology)
        return package.requirements.all(), package.nacr, package.location_flag


class NetworkServicePackage(models.Model):
    class LocationFlagChoices(models.TextChoices):
        ingress = ("I", _("Ingress"))
        egress = ("E", _("Egress"))
        border = ("B", _("Border"))
        custom = ("C", _("Custom"))
        all = ("A", _("All"))

    network_service = models.ForeignKey(
        NetworkService,
        on_delete=models.CASCADE,
        related_name="packages",
        verbose_name=_("Network Service"),
    )
    technology = models.ForeignKey(
        ProgrammableTechnology, on_delete=models.SET_NULL, null=True)
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
