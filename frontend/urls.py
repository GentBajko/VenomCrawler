from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="homepage"),
    path('login/', views.index, name="login-page"),
    path('register/', views.index, name="registration-page"),
]
