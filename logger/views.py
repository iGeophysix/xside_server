from django.shortcuts import redirect

# Create your views here.
from django.urls import reverse


def index(request):
    return redirect(reverse('swagger-ui'))
