import json

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.shortcuts import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import Client, ClientUser


def serialize_client(client):
    serialized = model_to_dict(client)
    serialized["name"] = str(client.name)
    return serialized


@api_view(['GET', ])
def clients(request):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        clients_data = Client.objects.filter(clientuser__user=request.user)

        clients_count = clients_data.count()

        page_size = int(request.GET.get("page_size", "10"))
        page_no = int(request.GET.get("page_no", "0"))
        clients_data = list(clients_data[page_no * page_size:page_no * page_size + page_size])

        clients_data = [serialize_client(client) for client in clients_data]
        return HttpResponse(json.dumps({"count": clients_count, "data": clients_data}), status=status.HTTP_200_OK)
    """
    if request.method == "POST":
        client = Client()
        return save_client(request, client, status.HTTP_201_CREATED)
    """
    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', ])
def client(request, client_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    # check if user can access this client
    try:
        ClientUser.objects.get(client__id=client_id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    try:
        client = Client.objects.get(pk=client_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_client(client)}), status=status.HTTP_200_OK)
    """
    if request.method == "PUT":
        return save_client(request, client, status.HTTP_200_OK)

    if request.method == "DELETE":
        client.delete()
        return HttpResponse(json.dumps({"detail": "deleted"}), status=status.HTTP_410_GONE)
    """
    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


"""
def save_client(request, client, success_status):
    errors = []
    name = request.data.get("name", "")
    if name == "":
        errors.append({"name": "This field is required"})

    try:
        client.name = name
        client.save()
    except Exception as e:
        return HttpResponse(json.dumps(
            {
                "errors": {"Client": str(e)}
            }), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"data": serialize_client(client)}), status=success_status)
"""
