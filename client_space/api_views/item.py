import json

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.shortcuts import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import Item, Client


def serialize_item(item):
    serialized = model_to_dict(item)
    out = {
        "name": str(item.name),
        "client": item.client.name,
        "image": item.image.url,
        "areas": json.loads(item.areas.geojson),
    }
    serialized.update(out)
    return serialized


@api_view(['GET', ])
def items(request):
    """
    Get all items available for the user
    :param request:
    :return:
    """
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        clients = Client.objects.filter(clientuser__user=request.user)
        items_data = Item.objects.filter(client__in=clients)

        items_count = items_data.count()

        page_size = int(request.GET.get("page_size", "10"))
        page_no = int(request.GET.get("page_no", "0"))
        items_data = list(items_data[page_no * page_size:page_no * page_size + page_size])

        items_data = [serialize_item(item) for item in items_data]
        return HttpResponse(json.dumps({"count": items_count, "data": items_data}), status=status.HTTP_200_OK)

    if request.method == "POST":
        item = Item()
        return save_item(request, item, status.HTTP_201_CREATED)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', 'PUT', 'DELETE'])
def item(request, item_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({"detail": "Not authorized"}), status=status.HTTP_401_UNAUTHORIZED)

    try:
        item = Item.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({"detail": "Not found"}), status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return HttpResponse(json.dumps({"data": serialize_item(item)}), status=status.HTTP_200_OK)

    if request.method == "PUT":
        return save_item(request, item, status.HTTP_200_OK)

    if request.method == "DELETE":
        item.delete()
        return HttpResponse(json.dumps({"detail": "deleted"}), status=status.HTTP_410_GONE)

    return HttpResponse(json.dumps({"detail": "Wrong method"}), status=status.HTTP_501_NOT_IMPLEMENTED)


def save_item(request, item, success_status):
    errors = []
    name = request.data.get("name", "")
    if name == "":
        errors.append({"name": "This field is required"})

    try:
        item.name = name
        item.save()
    except Exception as e:
        return HttpResponse(json.dumps(
            {
                "errors": {"Item": str(e)}
            }), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"data": serialize_item(item)}), status=success_status)
