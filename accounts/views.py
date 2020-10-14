from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def login(request):
    return render(request, '../frontend/templates/frontend/index.html')


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return render(request, '../frontend/templates/frontend/index.html')
    context = {'form': form}
    return render(request, '../frontend/templates/frontend/index.html', context)
