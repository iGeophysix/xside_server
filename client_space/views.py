from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse('swagger-ui'))
    else:
        return redirect(f'{settings.FRONTEND_BASE_URL}/login')


