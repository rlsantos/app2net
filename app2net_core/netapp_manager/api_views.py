from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import views
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from infrastructure_handler.models import Pvn
from .serializers import RepositorySerializer, NetworkServiceSerializer
from .models import Repository, NetworkService
from .services.node_selector import define_compatible_nodes



class RepositoryViewSet(ModelViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()


class NetworkServiceListView(generics.ListAPIView):
    serializer_class = NetworkServiceSerializer
    queryset = NetworkService.objects.all()
    lookup_url_kwarg = 'developer'
    lookup_field = 'developer'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.kwargs:
            return qs.filter(developer__username=self.kwargs['developer'])
        return qs


class NetworkServiceDetailView(generics.RetrieveAPIView):
    serializer_class = NetworkServiceSerializer
    queryset = NetworkService.objects.all()

    def get_object(self):
        return self.queryset.get(
            developer__username=self.kwargs["developer"],
            identifier=self.kwargs["identifier"]
        )


class DeployNetworkService(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        developer = self.kwargs["developer"]
        network_service_id = self.kwargs["identifier"]

        network_service = NetworkService.objects.get(
            developer__username=developer, identifier=network_service_id
        )

        pvn_info = get_object_or_404(Pvn,
            id=request.POST['pvn'],
            owner=request.user,
        ).get_info()

        define_compatible_nodes(pvn_info, network_service)
        return Response({"success": True})
