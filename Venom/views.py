from django.core import validators
from django.http import HttpResponse
import os


def index(request):
    return HttpResponse([f"{x}\n".replace(".py", "\n") for x in os.listdir('crawlers')])