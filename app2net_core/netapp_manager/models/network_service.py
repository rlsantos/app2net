from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from xml.etree import ElementTree
import os

from infrastructure_handler.models import Resource, ProgrammableTechnology, ExecutionEnvironment

from .repository import Repository
from .category import Category


def get_nad_upload_path(instance, filename):
    return f"nad/{instance.developer}/{instance.identifier}.nad"


class NetworkServiceManager(models.Manager):
    @transaction.atomic
    def create_from_nad(self, nad_file, developer):
        parsed_data = ElementTree.parse(nad_file)

        root = parsed_data.getroot()

        identifier = root.find("identifier").text
        categories = root.findall("categories/category")
        packages = root.findall("packages/technology")

        network_service = self.create(
            identifier=identifier, 
            nad_file=nad_file, 
            developer=developer
        )

        categories_objs = [Category.objects.get_or_create(name=category.text)[0] for category in categories]

        network_service.categories.set(categories_objs)

        for package in packages:
            pkg_technology = ProgrammableTechnology.objects.get(
                name=package.find('identifier').text
            )
            pkg_ee = ExecutionEnvironment.objects.get(
                programmable_technology=pkg_technology, 
                name=package.find('ee').text
            )
            pkg_version = package.find('version').text
            pkg_type = package.find('type').text
            pkg_uri = package.find('location/uri').text
            pkg_hash = package.find('hash')
            pkg_location_flag = package.find('location_flag')

            package_obj = NetworkServicePackage.objects.create(
                network_service=network_service,
                technology=pkg_technology,
                execution_environment=pkg_ee,
                type=pkg_type, #How to make this?
            )
            pkg_actions = package.find('manage_actions')

        
        print(identifier, categories, packages)


class NetworkService(models.Model):
    identifier = models.SlugField(max_length=100, blank=True)
    version = models.CharField(max_length=30, blank=True)

    developer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="+",
        blank=True
    )
    categories = models.ManyToManyField(
        Category, related_name="network_services")

    downloads = models.PositiveIntegerField(default=0, editable=False)
    nad_file = models.FileField(upload_to=get_nad_upload_path, null=True, blank=True)
    conflicts = models.ManyToManyField('self')
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
    type = models.CharField(max_length=6, choices=NetAppType.choices,
                            default=NetAppType.NETAPP)
    execution_environment = models.ForeignKey(
        ExecutionEnvironment, on_delete=models.SET_NULL, null=True
    )
    nacr = models.ForeignKey(Repository, on_delete=models.CASCADE,
                             related_name="network_services")
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
