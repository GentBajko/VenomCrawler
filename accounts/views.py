from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Registration
from .forms import RegistrationForm


def login(request):
    return render(request, '../templates/index.html')


@csrf_exempt
def register(request):
    form = RegistrationForm(request.POST)
    if request.method == "POST" and form.is_valid():
        form = form.clean()
        Registration(form).save()
        return render(request, '../templates/index.html')
    context = {'form': form}
    return render(request, '../templates/index.html', context)
