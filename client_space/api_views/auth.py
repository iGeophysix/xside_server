from rest_framework_simplejwt.views import TokenObtainPairView

from client_space.serializers.auth import CustomTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer