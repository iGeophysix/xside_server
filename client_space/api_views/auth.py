from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView

from client_space.serializers.auth import CustomTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    operation_id='Update user info',
    description='Update user info',
    parameters=[
        OpenApiParameter("first_name", OpenApiTypes.STR, description="First Name"),
        OpenApiParameter("last_name", OpenApiTypes.STR, description="Last Name"),
        OpenApiParameter("email", OpenApiTypes.STR, description="Email"),

    ],
    methods=["POST", ],
    responses={
        (200, 'application/json'): OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            'Example',
            value={},
        ),
    ],
)
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
    if request.method == "POST":
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        email = request.data.get('email', None)

        if not (first_name and last_name and email):
            return JsonResponse({"detail": "All fields are required"}, status=status.HTTP_401_UNAUTHORIZED)

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
        return JsonResponse({"data": data}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"detail": "Wrong method"}, status=status.HTTP_501_NOT_IMPLEMENTED)
