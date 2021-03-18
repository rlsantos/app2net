from system_notifier.notification_exchanger import transfer_netapp

from .package_installer import install_netapp
import secrets


def trigger_transfer(nacr, location_flag, compatible_nodes, requirements, package):
    hash_crypt = secrets.token_bytes(16)
    calculated_hashcrypt = nacr.check_authenticity(hash_crypt)

    if not validate_repository(hash_crypt, calculated_hashcrypt):
        raise ConnectionError("NACR couldn't prove its identity")

    transfer_guidelines = nacr.define_transfer_guidelines("", compatible_nodes)
    transfer_guidelines.package = package
    transfer_netapp(compatible_nodes, nacr, transfer_guidelines)
    install_netapp(compatible_nodes, package)


def validate_repository(hash_crypt, calculated_hash):
    return True


def define_transfers_guidelines(strategy, compatible_nodes, nacr):
    return {
        "strategy": strategy,
    }
