from rest_framework import serializers

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
        model = models.NetworkServicePackage
        fields = ["technology", "type", "location_flag", "uri", "hash", "actions"]


class NetworkServiceSerializer(serializers.ModelSerializer):
    developer = serializers.StringRelatedField()
    packages = NetworkServicePackageSerializer(many=True, required=False)

    class Meta:
        model = models.NetworkService
        fields = ["identifier", "developer", "nad_file", "packages"]
        depth = 5

    def create(self, validated_data):
        return models.NetworkService.objects.create_from_nad(validated_data["nad_file"])
