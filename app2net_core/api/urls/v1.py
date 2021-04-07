from django.urls import path, include
from rest_framework import routers


import netapp_manager.api_views as nm_views
import infrastructure_handler.api_views as ih_views
from rest_framework.authtoken.views import ObtainAuthToken


router = routers.DefaultRouter()
router.register("repositories", nm_views.RepositoryViewSet)
router.register("pvns", ih_views.PvnViewSet)


app_name = 'v1'

urlpatterns = [
    path('auth/', ObtainAuthToken.as_view(), name="get_auth_token"),

    path('network_services/', nm_views.NetworkServiceListView.as_view(), name="network_services__list"),
    path('network_services/<str:developer>/',
         nm_views.NetworkServiceListView.as_view(),
         name="network_services__developer__list"),
    path('network_services/<str:developer>/<str:identifier>/',
         nm_views.NetworkServiceDetailView.as_view(),
         name="network_service_retrieve"),
    path('network_services/<str:developer>/<str:identifier>/deploy/',
         nm_views.DeployNetworkService.as_view(),
         name="network_service_retrieve"),
    path('', include(router.urls)),
]
