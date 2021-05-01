from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from xml.etree import ElementTree

import os

from infrastructure_handler.models import ProgrammableTechnology, ExecutionEnvironment

from .repository import Repository
from .category import Category


def get_nad_upload_path(instance, filename):
    return f"nad/{instance.developer}/{instance.identifier}.nad"


class NetAppManager(models.Manager):
    @transaction.atomic
    def create_from_nad(self, nad_file, developer):
        try:
            parsed_data = ElementTree.parse(nad_file)
        except ElementTree.ParseError:
            raise ValueError("Invalid NAD File")

        root = parsed_data.getroot()

        identifier = root.find("identifier").text
        categories = root.findall("categories/category")
        packages = root.findall("packages/technology")

        try:
            network_service = self.create(
                identifier=identifier, 
                nad_file=nad_file, 
                developer=developer
            )
        except IntegrityError:
            raise ValueError((
                f"You already have a service with the identifier '{identifier}'."
            ))

        categories_objs = [Category.objects.get_or_create(name=category.text)[0] for category in categories]

        network_service.categories.set(categories_objs)

        for package in packages:
            pkg_technology = ProgrammableTechnology.objects.get(
                name=package.find('identifier').text
            )
            pkg_version = package.find('version').text

            ee_query = {
                "programmable_technology": pkg_technology,
                "name": package.find('ee').text
            }

            if pkg_version != "all":
                ee_query["version"] = pkg_version

            pkg_ee = ExecutionEnvironment.objects.get(**ee_query)

            pkg_type = package.find('type').text
            pkg_uri = package.find('location/uri').text
            pkg_hash = package.find('hash').text
            pkg_location_flag = NetAppPackage.LocationFlagChoices(package.find('location_flag').text)

            pkg_repository, sep, pkg_path = pkg_uri.partition("/")

            if not sep:
                raise ValueError(f"Invalid NAD File: Invalid URI {pkg_uri}")

            try:
                nacr = Repository.objects.get(address=pkg_repository)

            except Repository.DoesNotExist:
                raise ValueError(f"Repository '{pkg_repository}' not registered")

            package_obj = network_service.packages.create(
                execution_environment=pkg_ee,
                type=pkg_type,
                nacr=nacr,
                file_path=pkg_path,
                location_flag=pkg_location_flag,
                hash=pkg_hash,
            )

            pkg_actions = package.find('manage_actions')
            for action in pkg_actions.getchildren():
                name = action.tag
                command = action.findtext('command')
                native_procedure = action.findtext('native_procedure') == "true"

                package_obj.actions.create(
                    name=name,
                    command=command,
                    native_procedure=native_procedure
                )

        return network_service


class NetApp(models.Model):
    identifier = models.SlugField(max_length=100, blank=True)
    version = models.CharField(max_length=30, blank=True)

    developer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True
    )
    categories = models.ManyToManyField(Category, related_name="network_services")
    downloads = models.PositiveIntegerField(default=0, editable=False)
    nad_file = models.FileField(upload_to=get_nad_upload_path, null=True, blank=True)
    conflicts = models.ManyToManyField('self', blank=True)
    objects = NetAppManager()

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
        package = self.packages.get(execution_environment=technology)

        requirements = (
            package.execution_environment.requirements.all()
        )
        return (requirements.most_restrictive(), 
                package.nacr, package.location_flag)


class NetAppPackage(models.Model):
    class LocationFlagChoices(models.TextChoices):
        INGRESS = ("ingress", _("Ingress"))
        EGRESS = ("egress", _("Egress"))
        BORDER = ("border", _("Border"))
        CUSTOM = ("custom", _("Custom"))
        ALL = ("all", _("All"))

    class NetAppType(models.TextChoices):
        NETAPP = ("NetApp", _("NetApp"))
        VNA = ("VNA", _("VNA"))

    network_service = models.ForeignKey(
        NetApp,
        on_delete=models.CASCADE,
        related_name="packages",
        verbose_name=_("Network Service"),
    )
    type = models.CharField(max_length=6, choices=NetAppType.choices,
                            default=NetAppType.NETAPP)
    execution_environment = models.ForeignKey(
        ExecutionEnvironment, on_delete=models.SET_NULL, null=True
    )
    nacr = models.ForeignKey(Repository, on_delete=models.CASCADE,
                             related_name="network_services")
    location_flag = models.CharField(max_length=7, choices=LocationFlagChoices.choices)
    file_path = models.CharField(max_length=500)
    hash = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('network_service', 'execution_environment'),
                name='single_package_per_execution_environment'
            ),
        ]

    def __str__(self):
        return f"{self.network_service}: {self.execution_environment}"

    @property
    def uri(self):
        return os.path.join(self.nacr.address, self.file_path)

    def install(self, nodes):
        for node in nodes:
            connection = node.connect()
            connection.download()


class Action(models.Model):
    name = models.CharField(max_length=50)
    package = models.ForeignKey(NetAppPackage,
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
