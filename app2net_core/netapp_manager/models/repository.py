from django.db import models
from django.utils.translation import gettext_lazy as _
from dataclasses import dataclass
import uuid

from netapp_manager.exceptions import TransferError


def get_upload_url(filename, instance):
    return f"nacr_keys/{instance.address}/"


@dataclass
class TransferGuidelines:
    """Class to store the transfer guidelines

    Attributes:
        strategy (str): Strategy to be used to transfer files
        network_service (NetworkServicePackage): Network service to be transfered
    """
    strategy: str
    package: 'NetworkServicePackage' = None


class Repository(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    address = models.CharField(max_length=300)
    public_key = models.FileField(upload_to='nacr_keys/', null=True, blank=True)

    class Meta:
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")

    def __str__(self):
        return f"Repository: {self.address}"

    def define_transfer_guidelines(self, strategy, compatible_nodes):
        """Define the optimal transference guidelines

        Arguments:
            strategy (str): Strategy to be used on transfers
            compatible_nodes(QuerySet[Device]): Devices to receive the files

        ToDo:
            Actual implementation
        """
        return TransferGuidelines(strategy)

    def check_authenticity(self, hash_crypt):
        """Check identity of remote repository

        Arguments:
            hash_crypt (str): Hash to ask for calculation

        ToDo: Actual Implementation
        """
        pass

    def run_transfers(self, compatible_nodes, transfer_guidelines):
        """Transfer files to nodes according transfer guidelines

        Arguments:
            compatible_nodes (Queryset[Device]): Set of nodes to run transference
            transfer_guidelines (TransferGuidelines): Guidelines to follow while transfering files

        Notes:
            transfer_guidelines will only be required while 
            notify_nodes_and_repository is not fully implemented
        """
        for node in compatible_nodes:
            connection = node.connect()
            response = connection.download(
                transfer_guidelines.package.uri,
                transfer_guidelines.package.network_service.identifier,
                transfer_guidelines.package.hash,
                transfer_guidelines.strategy
            )
            if not response['success']:
                raise TransferError(response["error"]['message'])
