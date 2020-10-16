from django.core import validators
from django.http import HttpResponse
from . import models


def index(request):
    return HttpResponse(models.Crawler.all())
