import infrastructure_handler.models.pvn
from netapp_manager.services import node_selector
from infrastructure_handler.models import Pvn, ProgrammableTechnology


def deploy_network_service(pvn, network_service, technology=None):
    pvn_info = infrastructure_handler.models.pvn.PvnInfo(pvn, technology)
    node_selector.define_compatible_nodes(pvn_info, network_service)


def remove_network_service(pvn, network_service):
    pvn_info = infrastructure_handler.models.pvn.PvnInfo(pvn)


pvn_name = input("Pvn Name: ")
pvn = Pvn.objects.get(name=pvn_name)

while True:
    operation = input("Operation:\n1. Deploy\n2. Remove")
    if operation == "1":
        netapp_id = input("NetApp Identifier: ")
        technology = input("Technology (Optional): ")
        if technology != "":
            technology = ProgrammableTechnology.objects.get(name=technology)
        else:
            technology = None
        deploy_network_service(pvn, netapp_id, technology)
    elif operation == "2":
        netapp_id = input("NetApp Identifier: ")
        remove_network_service(pvn, netapp_id)
