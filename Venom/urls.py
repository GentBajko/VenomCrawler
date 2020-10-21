from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('create/', views.create),
    path('edit/', views.edit),
    path('delete/', views.delete),
    path('start/', views.start),
    path('cancel/', views.cancel),
]
