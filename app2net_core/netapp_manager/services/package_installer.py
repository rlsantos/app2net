from netapp_manager.services.netapp_configurator import config


def install_netapp(compatible_nodes, package):
    for node in compatible_nodes:
        install_action = package.actions.get(name='install')
        connection = node.connect()
        output = connection.run_management_action(
            package.network_service.identifier,
            install_action.command,
            install_action.native_procedure
        )
    config(package, compatible_nodes)
