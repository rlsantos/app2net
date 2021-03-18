from app2net_core.netapp_manager.services.netapp_configurator import config


def install_netapp(compatible_nodes, network_service):
    for node in compatible_nodes:
        for technology in node.programmable_technologies.all():
            package = network_service.packages.get(
                technology=technology
            )
            install_action = package.actions.get(name='install')
            connection = node.connect()
            connection.run_management_action(
                network_service.identifier,
                install_action.command,
                install_action.native_procedure
            )
    config(network_service, compatible_nodes)
