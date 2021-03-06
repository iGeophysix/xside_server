"""xside_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .api_views import client, item
from .api_views.auth import EmailTokenObtainPairView, user

app_name = 'client_space'

urlpatterns = [
    path('', views.index, name='index'),
    # auth
    path('token/', EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_obtain_pair_refresh"),
    path('user/', user, name="user"),

    # client
    path('client/', client.clients, name='client'),
    path('client/<int:client_id>', client.client, name='client'),

    # item
    path('item/', item.items, name='item'),
    path('item/<int:item_id>', item.item, name='item'),
    path('item/<int:item_id>/image', item.image, name='image'),
]
