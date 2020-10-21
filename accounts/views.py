from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def login(request):
    return render(request, '../templates/index.html')


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return render(request, '../templates/index.html')
    context = {'form': form}
    return render(request, '../templates/index.html', context)
