from django.conf import settings
from django.shortcuts import redirect


def index(request):
    if request.user.is_authenticated:
        return redirect(f'{settings.FRONTEND_BASE_URL}/dashboard')
    else:
        return redirect(f'{settings.FRONTEND_BASE_URL}/login')


