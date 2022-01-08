import decimal
import json
from hashlib import md5

from django.contrib.gis.gdal import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
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


def serialize_item(item, fields=None):
    serialized = model_to_dict(item)
    out = {
        "name": str(item.name),
        "client": item.client.name,
        "images": list(ItemFile.objects.filter(item=item).values_list("image", flat=1)),
        "images_url": [i.image.url for i in ItemFile.objects.filter(item=item)],
        "areas": json.loads(item.areas.geojson),
        "max_rate": float(item.max_rate),
        "max_daily_spend": float(item.max_daily_spend)
    }
    serialized.update(out)
    if fields:
        serialized = {field: serialized.get(field, None) for field in fields}
    return serialized


@extend_schema(
    operation_id='Get all items',
    description='Get all available items',
    parameters=[
        OpenApiParameter("fields", OpenApiTypes.OBJECT, description="list of fields",
                         examples=[
                             OpenApiExample(
                                 'All fields',
                                 value=None
                             ),
                             OpenApiExample(
                                 'Only ID',
                                 value=['id']
                             ),
                             OpenApiExample(
                                 'Only ID and name',
                                 value=["id", "name"]
                             ),
                         ]),
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
                        ],
                        "images_url": [
                            "https://storage.yandexcloud.net/xside/images/path/to/file1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
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
                        ],
                        "images_url": [
                            "https://storage.yandexcloud.net/xside/images/path/to/file2.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                        ]
                    }
                ]
            }
        ),
    ],
)
@extend_schema(
    operation_id='Add new item',
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
                   "images_url": [
                       "https://storage.yandexcloud.net/xside/images/path/to/image1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                   ],
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
@api_view(['GET', 'HEAD', 'POST', ])
def items(request):
    """
    Get all items available for the user
    :return:
    """
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method in ("GET", 'HEAD'):
        clients = Client.objects.filter(clientuser__user=request.user)
        items_data = Item.objects.filter(client__in=clients)

        items_count = items_data.count()

        page_size = min(MAX_PAGE_SIZE, int(request.GET.get("page_size", MAX_PAGE_SIZE)))
        page_no = int(request.GET.get("page", "0"))
        items_data = list(items_data[page_no * page_size:page_no * page_size + page_size])
        fields = request.GET.getlist("fields", [])
        items_data = [serialize_item(item, fields) for item in items_data]

        return JsonResponse({"count": items_count, "data": items_data}, status=status.HTTP_200_OK)

    if request.method == "POST":
        item = Item()
        return save_item(request, item, status.HTTP_201_CREATED)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


@extend_schema(
    operation_id='Get item by id',
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
                    ],
                    "images_url": [
                        "https://storage.yandexcloud.net/xside/images/path/to/file1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                    ]
                }
            }
        ),
    ],
)
@extend_schema(
    operation_id='Update item by id',
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
                    ],
                    "images_url": [
                        "https://storage.yandexcloud.net/xside/images/path/to/file1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                    ],
                }
            },
        ),
    ],
)
@extend_schema(
    operation_id='Delete item by id',
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

    # check user permissions to access this item
    if not item.client.clientuser_set.filter(user=request.user):
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        return JsonResponse({"data": serialize_item(item)}, status=status.HTTP_200_OK)

    if request.method == "PUT":
        return save_item(request, item, status.HTTP_200_OK)

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"detail": "deleted"}, status=status.HTTP_200_OK)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


@extend_schema(
    operation_id='Add item images by item id',
    description='Add item images by item id without updating item\'s info',
    parameters=[],
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
                    ],
                    "images_url": [
                        "https://storage.yandexcloud.net/xside/images/path/to/file1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                    ],
                }
            },
        ),
    ],
)
@extend_schema(
    operation_id='Delete item images',
    description='Delete item images by item id and image name',
    parameters=[
        OpenApiParameter("image", OpenApiTypes.STR, description="Image path (short)"),
    ],
    methods=["DELETE", ],
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
                    ],
                    "images_url": [
                        "https://storage.yandexcloud.net/xside/images/path/to/file1.jpg?AWSAccessKeyId=s***********Nv&Signature=zrQSgfWu5f********o%3D&Expires=1641412663"
                    ],
                }
            },
        ),
    ],
)
@api_view(['PUT', 'DELETE'])
def image(request, item_id):
    """
    Update item images by item id without updating item\'s info
    :param item_id:
    :return:
    """

    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        item = Item.objects.get(pk=item_id)
    except ObjectDoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    # check user permissions to access this item
    if not item.client.clientuser_set.filter(user=request.user):
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "PUT":
        images = request.FILES.getlist("image", None)
        if not images:
            return JsonResponse({"errors": [{"image": "This field is required"}]}, status=status.HTTP_404_NOT_FOUND)

        for image in images:
            image_md5 = _get_md5(image)
            existing_file = ItemFile.objects.filter(item_id=item.pk, md5=image_md5)
            if not existing_file:
                ItemFile(item=item, image=image).save()
        return JsonResponse({"data": serialize_item(item)}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        path = request.GET.get('image', None)
        if not path:
            return JsonResponse({"errors": [{"Images": "Image path not specified"}, ]}, status=status.HTTP_400_BAD_REQUEST)
        image = ItemFile.objects.filter(item_id=item_id, image=path)
        if not image:
            return JsonResponse({"errors": [{"Images": "Image not found"}, ]}, status=status.HTTP_404_NOT_FOUND)

        if ItemFile.objects.filter(item_id=item_id).count() < 2:
            return JsonResponse({"errors": [{"Images": "Cannot delete the last image"}, ]}, status=status.HTTP_400_BAD_REQUEST)

        image.delete()
        return JsonResponse({"data": serialize_item(item)}, status=status.HTTP_200_OK)


def _get_md5(file):
    result = md5(file.read()).hexdigest()
    file.seek(0)
    return result


def save_item(request, item, success_status):
    """Validate request and save item"""

    areas, client, is_active, max_daily_spend, max_rate, name, errors = _parse_request_body(request)
    if errors:
        return JsonResponse({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    try:
        item.client = client
        item.name = name
        item.areas = areas
        item.is_active = is_active
        item.max_rate = max_rate
        item.max_daily_spend = max_daily_spend
        item.save()

    except IntegrityError as e:
        return JsonResponse({"errors": [{"Item": "Item already exists"}, ] + errors}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        return JsonResponse({"errors": [{"Item": str(e)}, ] + errors}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"data": serialize_item(item)}, status=success_status)


def _parse_request_body(request):
    """
    Parese request body
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
    areas = request.data.get("areas", "")
    if name == "":
        errors.append({"areas": "This field is required"})
    try:
        areas = GEOSGeometry(areas)
        if areas.geom_type != 'MultiPolygon':
            raise GDALException(f'Expected MultiPolygon, got {areas.geom_type}')
    except (GDALException, ValueError):
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
        if max_rate <= 0:
            errors.append({'max_rate': 'Max_rate cannot be negative or zero. Expected positive number'})
    except Exception:
        errors.append({'max_rate': 'Cannot parse max_rate. Expected decimal number'})
    max_daily_spend = request.data.get("max_daily_spend", Item._meta.get_field('max_daily_spend').get_default())
    try:
        max_daily_spend = round(decimal.Decimal(max_daily_spend), Item._meta.get_field('max_daily_spend').decimal_places)

        if max_daily_spend <= 0:
            errors.append({'max_daily_spend': 'Max_daily_spend cannot be negative or zero. Expected positive number'})

    except Exception:
        errors.append({'max_daily_spend': 'Cannot parse max_daily_spend. Expected decimal number'})
    return areas, client, is_active, max_daily_spend, max_rate, name, errors
