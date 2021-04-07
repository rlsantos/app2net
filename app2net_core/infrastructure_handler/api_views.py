from rest_framework.viewsets import ModelViewSet
from .serializers import PvnSerializer, PvnDetailSerializer, PvnCreationSerializer
from .models import Pvn
from .permissions import UserOwnsObject


class PvnViewSet(ModelViewSet):
    queryset = Pvn.objects.all()
    permission_classes = [UserOwnsObject]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(owners=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PvnDetailSerializer
        elif self.action == 'create':
            return PvnCreationSerializer
        else:
            return PvnSerializer
