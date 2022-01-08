import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import ItemFile
from logger.models import Log

MAX_PAGE_SIZE = 100


class ParsingError(Exception):
    pass


@extend_schema(
    operation_id='Add new log',
    description='Add new log',
    parameters=[],
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
@api_view(['POST', ])
def logs(request):
    """
    Get all items available for the user
    :return:
    """
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        log = Log()
        return save_log(request, log, status.HTTP_201_CREATED)

    return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)


def save_log(request, log, success_status):
    try:
        videomodule = request.user.videomodule
    except User.DoesNotExist:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

    if not "features" in request.data.keys():
        return JsonResponse({"detail": "Feature collection not found"}, status=status.HTTP_400_BAD_REQUEST)

    for f in request.data['features']:
        try:
            event = f['properties']['event']
            item_file = f['properties']['item_file']
            data = json.loads(f['properties']['data']) if f['properties']['data'] is not None else None
            ts = f['properties']['timestamp']
            point = GEOSGeometry(json.dumps(f['geometry']))
        except KeyError:
            return JsonResponse({"detail": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            log.module = videomodule
            log.timestamp = ts
            log.point = point
            log.event = event
            log.item_file = ItemFile.objects.get(image=item_file) if item_file else None
            log.data = data
            log.save()
        except Exception as e:
            return JsonResponse({"detail": "Incorrect data"}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"data": "OK"}, status=success_status)
