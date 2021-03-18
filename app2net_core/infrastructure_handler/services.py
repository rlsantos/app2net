from django.db import transaction
from infrastructure_handler.models.interface import Interface
from infrastructure_handler.models.link import Internal
from system_notifier.notification_exchanger import get_nodes_info
from collections import namedtuple

from constants import CONVERSION_FACTORS, Units

from .models import Device, Pvn, Link, Resource, ResourceType
from .parsers import VxdlXmlParser


@transaction.atomic
def configure_nodes(vxdl, owner):
    pvn = _create_pvn(vxdl, owner)
    print(pvn)
    # pvn.install_drivers()
    #nodes_info = get_nodes_info()
    # save_data(nodes_info)


def _create_pvn(vxdl, owner) -> Pvn:
    data = VxdlXmlParser.parse(vxdl)
    nodes = data["nodes"]

    pvn = Pvn.objects.create(name=data["id"])
    pvn.owner.add(owner)

    devices = []
    resources = []
    interfaces = []

    for node in nodes:
        device_resources = [
            Resource.objects.get_or_create(
                name="CPU Cores",
                value=node["cpu"]["cores"],
                resource_type=ResourceType.objects.get_or_create(
                    name="cpu_cores",
                    unit=Units.QUANTITY
                )[0]
            )[0],
            Resource.objects.get_or_create(
                name="CPU Frequency",
                value=_get_resource_value(node["cpu"]["frequency"]),
                resource_type=ResourceType.objects.get_or_create(
                    name="cpu_frequency",
                    unit=Units.GHZ
                )[0]
            )[0],
            Resource.objects.get_or_create(
                name="Memory",
                value=_get_resource_value(node["memory"]),
                resource_type=ResourceType.objects.get_or_create(
                    name="memory",
                    unit=Units.KB
                )[0]
            )[0],
            Resource.objects.get_or_create(
                name="Storage",
                value=_get_resource_value(node["storage"]),
                resource_type=ResourceType.objects.get_or_create(
                    name="storage",
                    unit=Units.KB
                )[0]
            )[0],
        ]

        for software in node["software_list"]:
            print(software)

            device_resources.append(
                Resource.objects.get_or_create(
                    name=software["name"],
                    value=software["version"],
                    resource_type=ResourceType.objects.get_or_create(
                        name="installed_software",
                        unit=Units.VERSION
                    )[0]
                )[0]
            )

        resources.append(device_resources)

        device_interfaces = []

        for interface in node["interfaces"]:
            device_interfaces.append(Interface(
                name=interface["alias"]
            ))

        interfaces.append(device_interfaces)

        devices.append(
            Device(
                name=node["id"],
                pvn=pvn,
            )
        )

    devices_objects = Device.objects.bulk_create(devices)
    resource_objects = []
    interface_objects = []

    for idx, device in enumerate(devices_objects):
        for resource in resources[idx]:
            relation = Device.resources.through(device=device, resource=resource)
            resource_objects.append(relation)

        for interface in interfaces[idx]:
            interface.device = device
            interface_objects.append(interface)

    Device.resources.through.objects.bulk_create(resource_objects)
    Interface.objects.bulk_create(interface_objects)

    links = data["links"]

    link_objects = []

    for link in links:
        source_device = pvn.devices.get(name=link["source"]["node"])
        source_interface = source_device.interfaces.get(name=link["source"]["interface"])
        destination_device = pvn.devices.get(name=link["destination"]["node"])
        destination_interface = destination_device.interfaces.get(
            name=link["destination"]["interface"])

        link_objects.append(
            Internal(
                name=link["id"],
                max_speed=float(_get_resource_value(link["bandwidth"]["forward"])),
                unit=Units.KBPS,
                interface=source_interface,
                destination=destination_interface,
            )
        )

    Link.objects.bulk_create(link_objects)

    return pvn


def _get_resource_value(resource_data):
    verification_sequence = ["value", "max", "min"]
    for possibility in verification_sequence:
        if resource_data.get(possibility) is not None:
            return _normalize_unit(resource_data[possibility], resource_data["unit"])
    raise ValueError("Resource does not have a value")


def _normalize_unit(value, original_unit):
    if original_unit in CONVERSION_FACTORS:
        factor = CONVERSION_FACTORS[original_unit]
        return str(int(float(value) * factor))
    else:
        return value


def _get_compatible_driver(node):
    pass


def get_pvn_info(pvn):
    pass
