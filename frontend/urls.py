from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.index),
    path('edit/', views.index),
    path('delete/', views.index),
    path('start/', views.index),
    path('cancel/', views.index),
]
