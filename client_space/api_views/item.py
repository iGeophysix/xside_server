import json

from django.contrib.gis.gdal import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
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


@api_view(['GET', 'POST', ])
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


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
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
    """Validate request and save item"""
    errors = []
    client = request.data.get("client", "")
    if client == "":
        errors.append({"client": "This field is required"})

    try:
        client = Client.objects.get(name=client, clientuser__user=request.user)
    except Client.DoesNotExist:
        errors.append({"client": "Client not found or user doesn't have access to this manage this client"})

    name = request.data.get("name", "")
    if name == "":
        errors.append({"name": "This field is required"})

    image = request.FILES.get("image", None)
    if image is None:
        errors.append({"image": "This field is required"})

    areas = request.data.get("areas", "")
    if name == "":
        errors.append({"areas": "This field is required"})
    try:
        areas = GEOSGeometry(areas)
        if areas.geom_type != 'MultiPolygon':
            raise GDALException(f'Expected MultiPolygon, got {areas.geom_type}')
    except GDALException as e:
        errors.append({"areas": "Incorrect format of the field. Expected MultiPolygon in GeoJSON format."})

    if errors:
        return HttpResponse(json.dumps({"errors": errors}), status=status.HTTP_400_BAD_REQUEST)

    try:
        item.client = client
        item.name = name
        item.image = image
        item.areas = areas
        item.save()
    except IntegrityError as e:
        return HttpResponse(json.dumps(
            {"errors": [{"Item": str(e).strip().split("\n")[-1]}, ]}
        ), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({
            "errors": [{"Item": str(e)}, ]
        }), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps({"data": serialize_item(item)}), status=success_status)
