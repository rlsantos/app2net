from rest_framework.exceptions import APIException


class NetworkServiceStoreError(APIException):
    status_code = 400

class TransferError(Exception):
    pass