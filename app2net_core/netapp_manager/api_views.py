from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework import views
from rest_framework import permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from infrastructure_handler.models import Pvn
from .serializers import NetworkServiceNadSerializer, RepositorySerializer, NetworkServiceSerializer
from .models import Repository, NetApp
from .services.node_selector import define_compatible_nodes


class RepositoryViewSet(ModelViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()


class NetworkServiceListCreateView(generics.ListCreateAPIView):
    queryset = NetApp.objects.all()
    lookup_url_kwarg = 'developer'
    lookup_field = 'developer'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NetworkServiceSerializer
        else:
            return NetworkServiceNadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.kwargs:
            return qs.filter(developer__username=self.kwargs['developer'])
        return qs

    def perform_create(self, serializer):
        serializer.save(developer=self.request.user)


class NetworkServiceDetailView(generics.RetrieveAPIView):
    serializer_class = NetworkServiceSerializer
    queryset = NetApp.objects.all()

    def get_object(self):
        return self.queryset.get(
            developer__username=self.kwargs["developer"],
            identifier=self.kwargs["identifier"]
        )


class NetworkServiceCreateView(generics.CreateAPIView):
    serializer_class = NetworkServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer): 
        serializer.save(developer=self.request.user)


class DeployNetworkService(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        developer = self.kwargs["developer"]
        network_service_id = self.kwargs["identifier"]

        network_service = NetApp.objects.get(
            developer__username=developer, identifier=network_service_id
        )

        pvn_info = get_object_or_404(Pvn,
            id=request.POST['pvn'],
            owners=request.user,
        ).get_info()

        define_compatible_nodes(pvn_info, network_service)
        return Response({"success": True})
