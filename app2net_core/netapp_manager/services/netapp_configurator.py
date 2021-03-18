def config(network_service, compatible_nodes):
    """
    tuned_config = customize_config(network_service.initial_config)
    for node in compatible_nodes:
        connection = node.connect()
        connection.run_management_action(network_service.identifier, tuned_config)
    """
    pass


def customize_config(config):
    return config
