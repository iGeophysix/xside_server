import json

from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view

from client_space.models import ItemFile
from logger.models import Log, VideoModule

MAX_PAGE_SIZE = 100


class ParsingError(Exception):
    pass


@extend_schema(exclude=True, )
@api_view(['POST', ])
def logs(request):
    """
    POST logs from video modules
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
    except VideoModule.DoesNotExist:
        return JsonResponse({"detail": "Not videomodule"}, status=status.HTTP_403_FORBIDDEN)

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
        except Exception:
            return JsonResponse({"detail": "Incorrect data"}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"data": "OK"}, status=success_status)
