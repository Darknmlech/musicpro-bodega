from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inventario/', views.inventario, name='inventario'),
    path('movimientos/', views.movimientos, name='movimientos'),
]