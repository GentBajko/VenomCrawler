from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('profile/', views.register, name="profile"),
    path('password/', views.register, name="change-password"),
    path('subscription/', views.register, name="subscription"),
    path('crawlers/', views.register, name="crawlers"),
]
