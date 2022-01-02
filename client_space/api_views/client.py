import json

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import Client, ClientUser


def serialize_client(client):
    serialized = model_to_dict(client)
    serialized["name"] = str(client.name)
    return serialized


@extend_schema(
    operation_id='Get all clients',
    description='Get all available clients',
    parameters=[
        OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
    ],
    methods=["GET", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
)
@api_view(['GET', ])
def clients(request):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        clients_data = Client.objects.filter(clientuser__user=request.user)

        clients_count = clients_data.count()

        page_size = int(request.GET.get("page_size", "10"))
        page_no = int(request.GET.get("page", "0"))
        clients_data = list(clients_data[page_no * page_size:page_no * page_size + page_size])

        clients_data = [serialize_client(client) for client in clients_data]
        return JsonResponse({"count": clients_count, "data": clients_data}, status=status.HTTP_200_OK)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


@extend_schema(
    operation_id='Get client by id',
    description='Get one client',
    parameters=[],
    methods=["GET", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
)
@api_view(['GET', ])
def client(request, client_id):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    # check if user can access this client
    try:
        ClientUser.objects.get(client__id=client_id, user=request.user)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        client = Client.objects.get(pk=client_id)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return JsonResponse({"data": serialize_client(client)}, status=status.HTTP_200_OK)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)
