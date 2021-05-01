from netapp_manager.services.package_transfer import trigger_transfer


def define_compatible_nodes(pvn_info, network_service):
    packages = network_service.packages.filter(execution_environment__in=pvn_info.technologies)

    if not packages.exists():
        raise ValueError(
            f"Network service {network_service} does not "
            f"support technologies {pvn_info.technologies}"
        )

    for package in packages:
        requirements, nacr, location_flag = network_service.get_info(package.execution_environment)
        compatible_nodes = pvn_info.devices.filter(
            execution_environments=package.execution_environment
        ).filter_compatible(requirements)
        print(compatible_nodes)
        trigger_transfer(nacr, location_flag, compatible_nodes, requirements, package)
