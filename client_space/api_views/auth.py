from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView

from client_space.serializers.auth import CustomTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET', 'POST', ])
def user(request):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
    user = request.user
    if request.method == "GET":
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
        return JsonResponse({"data": data}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)
