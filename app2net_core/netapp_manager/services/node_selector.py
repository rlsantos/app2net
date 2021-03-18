from netapp_manager.models.network_service import NetworkService, NetworkServicePackage
from netapp_manager.services.package_transfer import trigger_transfer


class PvnInfo:
    def __init__(self, pvn):
        self.pvn = pvn
        self.devices = pvn.devices.all()


def define_compatible_nodes(pvn_info, network_service, technology=None):
    service = NetworkService.objects.get(identifier=network_service)

    if technology:
        packages = service.packages.filter(technology=technology)
        if not packages.exist():
            raise ValueError(
                f"Network service {network_service} does not support technology {technology}")
    else:
        packages = service.packages.all()

    for package in packages:
        requirements, nacr, location_flag = service.get_info(package.technology)
        compatible_nodes = pvn_info.devices.filter(
            programmable_technologies=package.technology
        ).filter_compatible(requirements)
        trigger_transfer(nacr, location_flag, compatible_nodes,
                         requirements, package)
