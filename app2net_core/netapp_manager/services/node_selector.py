from netapp_manager.models.network_service import NetworkService, NetworkServicePackage
from netapp_manager.services.package_transfer import trigger_transfer


class PvnInfo:
    def __init__(self, pvn, technology=None, network_service=None):
        self.pvn = pvn

        self.technologies = pvn.devices.values('programmable_technologies').distinct()

        if technology is not None and technology in self.technologies:
            self.technologies = self.technologies.get(id=technology.id)

        self.devices = pvn.devices.filter(programmable_technologies__in=self.technologies)


def define_compatible_nodes(pvn_info, network_service):
    service = NetworkService.objects.get(identifier=network_service)
    packages = service.packages.filter(technology__in=pvn_info.technologies)

    if not packages.exists():
        raise ValueError(
            f"Network service {network_service} does not "
            f"support technologies {pvn_info.technologies}"
        )

    for package in packages:
        requirements, nacr, location_flag = service.get_info(package.technology)
        compatible_nodes = pvn_info.devices.filter(
            programmable_technologies=package.technology
        ).filter_compatible(requirements)
        trigger_transfer(nacr, location_flag, compatible_nodes, requirements, package)
