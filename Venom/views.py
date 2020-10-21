from django.core import validators
from django.http import HttpResponse
from . import models


def dashboard(request):
    return HttpResponse('Venom Dashboard')


def create(request):
    return HttpResponse('Venom Create')


def edit(request):
    return HttpResponse('Venom Edit')


def delete(request):
    return HttpResponse('Venom Delete')


def start(request):
    return HttpResponse('Venom Start')


def cancel(request):
    return HttpResponse('Venom Cancel')
