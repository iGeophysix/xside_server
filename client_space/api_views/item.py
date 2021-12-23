import decimal
import json

from django.contrib.gis.gdal import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.forms.models import model_to_dict
from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import Item, Client, ItemFile

MAX_PAGE_SIZE = 100

class ParsingError(Exception):
    pass


def serialize_item(item):
    serialized = model_to_dict(item)
    out = {
        "name": str(item.name),
        "client": item.client.name,
        "images": list(ItemFile.objects.filter(item=item).values_list("image", flat=1)),
        "areas": json.loads(item.areas.geojson),
        "max_rate": float(item.max_rate),
        "max_daily_spend": float(item.max_daily_spend)
    }
    serialized.update(out)
    return serialized


@extend_schema(
    description='Get all available items',
    parameters=[
        OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
    ],
    methods=["GET", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={
                "count": 2,
                "data": [
                    {
                        "id": 49,
                        "client": "Client1",
                        "name": "Test 2",
                        "areas": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [
                                            37.60200012009591,
                                            55.753318768941305
                                        ],
                                        [
                                            37.60157692828216,
                                            55.750842010116045
                                        ],
                                        [
                                            37.60936881881207,
                                            55.74906941558997
                                        ],
                                        [
                                            37.613412427017465,
                                            55.75213456321547
                                        ],
                                        [
                                            37.607292663306005,
                                            55.75327778725062
                                        ],
                                        [
                                            37.60314446990378,
                                            55.75346674901331
                                        ],
                                        [
                                            37.60200012009591,
                                            55.753318768941305
                                        ]
                                    ]
                                ]
                            ]
                        },
                        "is_active": True,
                        "max_rate": 12.0,
                        "max_daily_spend": 110.01,
                        "images": [
                            "path/to/file1.jpg"
                        ]
                    },
                    {
                        "id": 46,
                        "client": "Client1",
                        "name": "Test Client 1",
                        "areas": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [
                                            37.60200012009591,
                                            55.753318768941305
                                        ],
                                        [
                                            37.60157692828216,
                                            55.750842010116045
                                        ],
                                        [
                                            37.60936881881207,
                                            55.74906941558997
                                        ],
                                        [
                                            37.613412427017465,
                                            55.75213456321547
                                        ],
                                        [
                                            37.607292663306005,
                                            55.75327778725062
                                        ],
                                        [
                                            37.60314446990378,
                                            55.75346674901331
                                        ],
                                        [
                                            37.60200012009591,
                                            55.753318768941305
                                        ]
                                    ]
                                ]
                            ]
                        },
                        "is_active": True,
                        "max_rate": 12.0,
                        "max_daily_spend": 110.01,
                        "images": [
                            "path/to/file2.jpg"
                        ]
                    }
                ]
            }
        ),
    ],
)
@extend_schema(
    description='Add new item',
    parameters=[
        OpenApiParameter("name", OpenApiTypes.STR, description="Item Name"),
        OpenApiParameter("client", OpenApiTypes.STR, description="Client Name", examples=[
            OpenApiExample('Client1', value='Client1'), OpenApiExample('Client2', value='Client2')
        ]),
        OpenApiParameter("image", OpenApiTypes.BINARY, description="Image to show"),
        OpenApiParameter("areas", OpenApiTypes.OBJECT, description="Areas to show item in", examples=[OpenApiExample('Sample Polygon', value={
            "type": "MultiPolygon",
            "coordinates": [[[[37.60200012009591, 55.753318768941305],
                              [37.60157692828216, 55.750842010116045],
                              [37.60936881881207, 55.74906941558997],
                              [37.613412427017465, 55.75213456321547],
                              [37.607292663306005, 55.75327778725062],
                              [37.60314446990378, 55.75346674901331],
                              [37.60200012009591, 55.753318768941305]]]]
        })]),
        OpenApiParameter("is_active", OpenApiTypes.BOOL, description="Item is active?"),
        OpenApiParameter("max_rate", OpenApiTypes.DECIMAL, description="Max Rate for show"),
        OpenApiParameter("max_daily_spend", OpenApiTypes.DECIMAL, description="Max daily spend"),
    ],
    methods=["POST", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={"id": 1,
                   "client": "Client1",
                   "name": "Item1",
                   "image": "/path/to/image1.jpg",
                   "areas": {
                       "type": "MultiPolygon",
                       "coordinates": [[[[37.60200012009591, 55.753318768941305],
                                         [37.60157692828216, 55.750842010116045],
                                         [37.60936881881207, 55.74906941558997],
                                         [37.613412427017465, 55.75213456321547],
                                         [37.607292663306005, 55.75327778725062],
                                         [37.60314446990378, 55.75346674901331],
                                         [37.60200012009591, 55.753318768941305]]]]
                   },
                   "is_active": False,
                   "max_rate": 10.0,
                   "max_daily_spend": 100.0
                   },

        ),
    ],
)
@api_view(['GET', 'POST', ])
def items(request):
    """
    Get all items available for the user
    :return:
    """
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        clients = Client.objects.filter(clientuser__user=request.user)
        items_data = Item.objects.filter(client__in=clients)

        items_count = items_data.count()

        page_size = min(MAX_PAGE_SIZE, int(request.GET.get("page_size", MAX_PAGE_SIZE)))
        page_no = int(request.GET.get("page", "0"))
        items_data = list(items_data[page_no * page_size:page_no * page_size + page_size])

        items_data = [serialize_item(item) for item in items_data]
        return JsonResponse({"count": items_count, "data": items_data}, status=status.HTTP_200_OK)

    if request.method == "POST":
        item = Item()
        return save_item(request, item, status.HTTP_201_CREATED)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


@extend_schema(
    description='Get item by id',
    parameters=[],
    methods=["GET", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={
                "data": {
                    "id": 49,
                    "client": "Client1",
                    "name": "Test 2",
                    "areas": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [
                                        37.60200012009591,
                                        55.753318768941305
                                    ],
                                    [
                                        37.60157692828216,
                                        55.750842010116045
                                    ],
                                    [
                                        37.60936881881207,
                                        55.74906941558997
                                    ],
                                    [
                                        37.613412427017465,
                                        55.75213456321547
                                    ],
                                    [
                                        37.607292663306005,
                                        55.75327778725062
                                    ],
                                    [
                                        37.60314446990378,
                                        55.75346674901331
                                    ],
                                    [
                                        37.60200012009591,
                                        55.753318768941305
                                    ]
                                ]
                            ]
                        ]
                    },
                    "is_active": True,
                    "max_rate": 12.0,
                    "max_daily_spend": 110.01,
                    "images": [
                        "path/to/file1.jpg"
                    ]
                }
            }
        ),
    ],
)
@extend_schema(
    description='Update item by id',
    parameters=[
        OpenApiParameter("name", OpenApiTypes.STR, description="Item Name"),
        OpenApiParameter("client", OpenApiTypes.STR, description="Client Name", examples=[
            OpenApiExample('Client1', value='Client1'), OpenApiExample('Client2', value='Client2')
        ]),
        OpenApiParameter("image", OpenApiTypes.BINARY, description="Image to show"),
        OpenApiParameter("areas", OpenApiTypes.OBJECT, description="Areas to show item in", examples=[OpenApiExample('Sample Polygon', value={
            "type": "MultiPolygon",
            "coordinates": [[[[37.60200012009591, 55.753318768941305],
                              [37.60157692828216, 55.750842010116045],
                              [37.60936881881207, 55.74906941558997],
                              [37.613412427017465, 55.75213456321547],
                              [37.607292663306005, 55.75327778725062],
                              [37.60314446990378, 55.75346674901331],
                              [37.60200012009591, 55.753318768941305]]]]
        })]),
    ],
    methods=["PUT", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={
                "data": {
                    "id": 49,
                    "client": "Client1",
                    "name": "Test 2",
                    "areas": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [
                                    [
                                        37.60200012009591,
                                        55.753318768941305
                                    ],
                                    [
                                        37.60157692828216,
                                        55.750842010116045
                                    ],
                                    [
                                        37.60936881881207,
                                        55.74906941558997
                                    ],
                                    [
                                        37.613412427017465,
                                        55.75213456321547
                                    ],
                                    [
                                        37.607292663306005,
                                        55.75327778725062
                                    ],
                                    [
                                        37.60314446990378,
                                        55.75346674901331
                                    ],
                                    [
                                        37.60200012009591,
                                        55.753318768941305
                                    ]
                                ]
                            ]
                        ]
                    },
                    "is_active": True,
                    "max_rate": 12.0,
                    "max_daily_spend": 110.01,
                    "images": [
                        "path/to/file1.jpg"
                    ]
                }
            },
        ),
    ],
)
@extend_schema(
    description='Delete item by id',
    parameters=[],
    methods=["DELETE", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={"detail": "deleted"}
        ),
    ],
)
@api_view(['GET', 'PUT', 'DELETE'])
def item(request, item_id):
    """
    CRUD operations with Items
    :param request:
    :param item_id:
    :return:
    """
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        item = Item.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return JsonResponse({"data": serialize_item(item)}, status=status.HTTP_200_OK)

    if request.method == "PUT":
        return save_item(request, item, status.HTTP_200_OK)

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"detail": "deleted"}, status=status.HTTP_410_GONE)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


def save_item(request, item, success_status):
    """Validate request and save item"""

    errors, areas, client, images, is_active, max_daily_spend, max_rate, name = parse_request_body(request)

    if errors:
        return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        item.client = client
        item.name = name
        item.areas = areas
        item.is_active = is_active
        item.max_rate = max_rate
        item.max_daily_spend = max_daily_spend

        with transaction.atomic():
            item.save()
            ItemFile.objects.filter(item=item).delete()
            for image in images:
                ItemFile(item_id=item.pk, image=image).save()
    except IntegrityError as e:
        return JsonResponse({"errors": [{"Item": str(e).strip().split("\n")[-1]}, ] + errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"errors": [{"Item": str(e)}, ] + errors}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"data": serialize_item(item)}, status=success_status)


def parse_request_body(request):
    """
    Parese request body
    :param errors:
    :param request:
    :return:
    """
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

    images = request.FILES.getlist("image", None)
    if images is None:
        errors.append({"image": "This field is required"})

    areas = request.data.get("areas", "")
    if name == "":
        errors.append({"areas": "This field is required"})
    try:
        areas = GEOSGeometry(areas)
        if areas.geom_type != 'MultiPolygon':
            raise GDALException(f'Expected MultiPolygon, got {areas.geom_type}')
    except GDALException:
        errors.append({"areas": "Incorrect format of the field. Expected MultiPolygon in GeoJSON format."})

    is_active = str(request.data.get("is_active", Item._meta.get_field('is_active').get_default()))
    try:
        if is_active.lower() in ('true', 'false'):
            is_active = is_active.lower() == 'true'
        else:
            raise ParsingError('Cannot parse is_active field')
    except ParsingError:
        errors.append({'is_active': 'Cannot parse is_active. Expected value: true or false'})

    max_rate = request.data.get("max_rate", Item._meta.get_field('max_rate').get_default())
    try:
        max_rate = round(decimal.Decimal(max_rate), Item._meta.get_field('max_daily_spend').decimal_places)
    except Exception:
        errors.append({'max_rate': 'Cannot parse max_rate. Expected decimal number'})

    max_daily_spend = request.data.get("max_daily_spend", Item._meta.get_field('max_daily_spend').get_default())
    try:
        max_daily_spend = round(decimal.Decimal(max_daily_spend), Item._meta.get_field('max_daily_spend').decimal_places)
    except Exception:
        errors.append({'max_daily_spend': 'Cannot parse max_daily_spend. Expected decimal number'})

    return errors, areas, client, images, is_active, max_daily_spend, max_rate, name
