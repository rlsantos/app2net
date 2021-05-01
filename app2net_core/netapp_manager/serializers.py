from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import APIException

from netapp_manager.exceptions import NetworkServiceStoreError
from . import models


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["id", "address", "public_key"]


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Action
        fields = ["name", "command", "native_procedure"]


class NetworkServicePackageSerializer(serializers.ModelSerializer):
    location_flag = serializers.CharField(source='get_location_flag_display')
    technology = serializers.StringRelatedField()
    actions = ActionSerializer(many=True)

    class Meta:
        model = models.NetAppPackage
        fields = ["technology", "type", "location_flag", "uri", "hash", "actions"]


class NetworkServiceSerializer(serializers.ModelSerializer):
    developer = serializers.StringRelatedField()
    packages = NetworkServicePackageSerializer(many=True, required=False)

    class Meta:
        model = models.NetApp
        fields = ["identifier", "developer", "nad_file", "packages"]
        depth = 5

    def create(self, validated_data):
        return models.NetApp.objects.create_from_nad(validated_data["nad_file"])


class NetworkServiceNadSerializer(serializers.ModelSerializer):
    nad = serializers.FileField(validators=[FileExtensionValidator(['nad'])])

    class Meta:
        model = models.NetApp
        fields = ['nad']

    def create(self, validated_data):
        try:
            return models.NetApp.objects.create_from_nad(validated_data["nad"], validated_data["developer"])
        except Exception as e:
            raise NetworkServiceStoreError(e)

    def to_representation(self, instance):
        return NetworkServiceSerializer().to_representation(instance)
