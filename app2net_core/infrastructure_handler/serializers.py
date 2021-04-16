from rest_framework import serializers

from .models import Pvn, Device, Resource
from .services import configure_nodes


class ResourceSerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField('get_unit')
    resource_type = serializers.SerializerMethodField('get_resource_type')

    class Meta:
        model = Resource
        fields = ['name', 'resource_type', 'value', 'unit']

    def get_unit(self, instance):
        return instance.resource_type.unit

    def get_resource_type(self, instance):
        return instance.resource_type.name


class DeviceSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True)

    class Meta:
        model = Device
        fields = ['name', 'status', 'create_date', 'update_date', "drivers", "resources"]
        depth = 5


class PvnSerializer(serializers.ModelSerializer):
    owners = serializers.StringRelatedField(many=True)

    class Meta:
        model = Pvn
        fields = ['id', 'name', 'owners']


class PvnDetailSerializer(serializers.ModelSerializer):
    owners = serializers.StringRelatedField(many=True)
    devices = DeviceSerializer(many=True)

    class Meta:
        model = Pvn
        fields = ['id', 'name', 'owners', 'devices']
        depth = 2


class PvnCreationSerializer(serializers.ModelSerializer):
    vxdl = serializers.FileField()

    class Meta:
        model = Pvn
        fields = ['id', 'vxdl']

    def create(self, validated_data):
        vxdl = validated_data['vxdl']
        owner = validated_data['owner']

        return configure_nodes(vxdl, owner)

    def to_representation(self, instance):
        return PvnDetailSerializer().to_representation(instance)
